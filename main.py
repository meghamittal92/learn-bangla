import streamlit as st
import os
from gtts import gTTS
import time
import re
import base64
import pandas as pd
import uuid
import requests
import json

# Set page configuration
st.set_page_config(
    page_title="Bengali to Hindi Translator",
    page_icon="🔤",
    layout="wide"
)

# Custom CSS with fixes for display issues
st.markdown("""
<style>
    .bengali-text {
        font-size: 18px;
        padding: 10px;
        background-color: #f0f8ff;
        border-radius: 5px;
        margin: 10px 0;
        display: block;
        width: 100%;
    }
    .hindi-text {
        font-size: 18px;
        padding: 10px;
        background-color: #fff0f5;
        border-radius: 5px;
        margin: 10px 0;
        display: block;
        width: 100%;
    }
    .word-card {
        display: inline-block;
        padding: 8px;
        margin: 4px;
        background-color: #e6f7ff;
        border-radius: 5px;
        border: 1px solid #b3e0ff;
    }
    .word-bengali {
        font-size: 16px;
        font-weight: bold;
    }
    .word-hindi {
        font-size: 16px;
        color: #0066cc;
    }
    .line-container {
        padding: 10px;
        margin-bottom: 15px;
        border: 1px solid #ddd;
        border-radius: 5px;
        background-color: white;
        display: block;
        width: 100%;
    }
    div[data-testid="stVerticalBlock"] {
        gap: 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'translations' not in st.session_state:
    st.session_state.translations = {}
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""

# Directory for audio files
audio_dir = "audio_files"
if not os.path.exists(audio_dir):
    os.makedirs(audio_dir)

# Function to get audio HTML
def get_audio_html(text, lang):
    """Generate audio for text and return HTML audio player"""
    try:
        # Create a unique filename with UUID to avoid hash collisions
        filename = f"{audio_dir}/{lang}_{uuid.uuid4()}.mp3"
        
        # Generate audio
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(filename)
        
        # Read audio file as bytes
        with open(filename, "rb") as audio_file:
            audio_bytes = audio_file.read()
        
        # Encode to base64
        audio_base64 = base64.b64encode(audio_bytes).decode()
        
        # Create HTML audio element with explicit width and controls
        audio_html = f"""
        <audio controls style="width:100%; max-width:250px; display:block; margin-top:5px;">
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            Your browser does not support the audio element.
        </audio>
        """
        
        # Clean up file after encoding
        try:
            os.remove(filename)
        except:
            pass
            
        return audio_html
    
    except Exception as e:
        st.error(f"Audio error: {str(e)}")
        return ""

# Function to translate using Claude API
def translate_with_claude(text, target_language="Hindi"):
    """Translate text using Claude API"""
    api_key = st.session_state.api_key
    
    if not api_key:
        st.error("Claude API key is required. Please enter it in the settings.")
        return "API key required"
    
    try:
        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01"
        }
        
        # Create a prompt that asks Claude to translate
        prompt = f"""Please translate the following Bengali text into {target_language}. 
Provide only the translation, without any explanations or additional text.

Bengali text: {text}

{target_language} translation:"""
        
        payload = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 1000,
            "temperature": 0,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=payload
        )
        
        # Handle the response
        if response.status_code == 200:
            response_data = response.json()
            translation = response_data["content"][0]["text"]
            # Clean the response - strip any markdown formatting if present
            translation = translation.strip()
            return translation
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return f"Translation error: API returned {response.status_code}"
    
    except Exception as e:
        st.error(f"Translation error: {str(e)}")
        return "Translation failed"

# Function to translate words with Claude (with batching for efficiency)
def translate_words_batch(words, target_language="Hindi"):
    """Translate a batch of words using Claude API for efficiency"""
    api_key = st.session_state.api_key
    
    if not api_key or not words:
        return []
    
    try:
        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01"
        }
        
        # Create a JSON format for Claude to parse
        words_str = json.dumps(words)
        
        prompt = f"""Please translate each of these Bengali words into {target_language}.
Return your answer as a JSON array with each element containing the Bengali word and its {target_language} translation.
Do not include anything else in your response except the JSON array.

Bengali words: {words_str}

JSON response format:
[
  {{"bengali": "word1", "hindi": "translation1"}},
  {{"bengali": "word2", "hindi": "translation2"}},
  ...
]"""
        
        payload = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 1000,
            "temperature": 0,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=payload
        )
        
        # Handle the response
        if response.status_code == 200:
            response_data = response.json()
            content = response_data["content"][0]["text"]
            
            # Extract JSON from response (handle potential surrounding text)
            json_pattern = r'\[\s*\{.*\}\s*\]'
            json_match = re.search(json_pattern, content, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(0)
                translations = json.loads(json_str)
                return translations
            else:
                # Fallback if JSON pattern not found
                return [{"bengali": w, "hindi": "Translation not available"} for w in words]
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return [{"bengali": w, "hindi": "API error"} for w in words]
    
    except Exception as e:
        st.error(f"Word translation error: {str(e)}")
        return [{"bengali": w, "hindi": "Error"} for w in words]

# Function to translate text with progress tracking
def translate_text(bengali_text):
    """Translate Bengali text to Hindi using Claude API"""
    if not bengali_text:
        st.warning("Please enter Bengali text to translate.")
        return
    
    if not st.session_state.api_key:
        st.error("Claude API key is required. Please enter it in the settings.")
        return
    
    try:
        # Split the text into lines
        lines = bengali_text.split('\n')
        lines = [line.strip() for line in lines if line.strip()]
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Process each line
        for i, line in enumerate(lines):
            if line not in st.session_state.translations:
                status_text.text(f"Translating line {i+1} of {len(lines)}...")
                
                # Translate the whole line using Claude API
                line_translation = translate_with_claude(line)
                
                # Split line into words for word-by-word translation
                words = re.findall(r'[\w\u0980-\u09FF]+|[^\w\s]', line)
                words = [w for w in words if w.strip()]
                
                # Translate words in batch for efficiency
                word_translations = translate_words_batch(words)
                
                # Store the translations
                st.session_state.translations[line] = {
                    'hindiLine': line_translation,
                    'words': word_translations
                }
            
            # Update progress
            progress_bar.progress((i + 1) / len(lines))
        
        status_text.text(f"Translation completed. Processed {len(lines)} lines.")
        time.sleep(1)
        status_text.empty()
        progress_bar.empty()
        
    except Exception as e:
        st.error(f"Translation error: {str(e)}")

# Settings section for API key
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Claude API Key", type="password", value=st.session_state.api_key)
    if api_key:
        st.session_state.api_key = api_key
    
    st.markdown("""
    ### About the Claude API
    
    You need an Anthropic API key to use this translator. 
    
    1. Sign up at [anthropic.com](https://anthropic.com/)
    2. Generate an API key in your account
    3. Paste the key above
    
    Your key is stored only in your session and not saved permanently.
    """)

# Header
st.title("Bengali to Hindi Translator")
st.markdown("Paste Bengali text below to get Hindi translation with Claude AI.")

# Input area
bengali_text = st.text_area("Input Bengali Text", height=150)

col1, col2, col3 = st.columns([1, 1, 4])
translate_button = col1.button("Translate")
clear_button = col2.button("Clear All")

# Handle clear button
if clear_button:
    st.session_state.translations = {}
    st.experimental_rerun()

# Translate when button is clicked
if translate_button and bengali_text:
    if not st.session_state.api_key:
        st.error("Please enter your Claude API key in the settings panel.")
    else:
        translate_text(bengali_text)

# View option
view_mode = st.radio("View Mode:", ["Line-by-Line", "Word-by-Word"], horizontal=True)

# Display translations if available
if bengali_text and st.session_state.translations:
    st.subheader("Translation Results")
    
    # Split into lines
    lines = bengali_text.split('\n')
    lines = [line.strip() for line in lines if line.strip()]
    
    # Create a table-like structure for display
    for i, line in enumerate(lines):
        if line in st.session_state.translations:
            # Use columns instead of containers for better layout
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown(f"**Line {i+1} (Bengali)**")
                # Use a div with explicit styling to ensure visibility
                st.markdown(f"<div class='bengali-text'>{line}</div>", unsafe_allow_html=True)
                bengali_audio = get_audio_html(line, 'bn')
                st.markdown(bengali_audio, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"**Hindi Translation**")
                # Hindi translation based on view mode
                if view_mode == "Line-by-Line":
                    hindi_line = st.session_state.translations[line]['hindiLine']
                    st.markdown(f"<div class='hindi-text'>{hindi_line}</div>", unsafe_allow_html=True)
                    # No audio for Hindi as requested
                
                else:  # Word-by-Word
                    word_html = "<div style='display: flex; flex-wrap: wrap;'>"
                    for word_data in st.session_state.translations[line]['words']:
                        word_html += f"""
                        <div class='word-card'>
                            <div class='word-bengali'>{word_data['bengali']}</div>
                            <div class='word-hindi'>{word_data['hindi']}</div>
                        </div>
                        """
                    word_html += "</div>"
                    st.markdown(word_html, unsafe_allow_html=True)
            
            st.markdown("---")

# Add stats and export options if translations exist
if st.session_state.translations:
    st.subheader("Statistics")
    
    # Calculate statistics
    total_lines = len(st.session_state.translations)
    total_words = sum(len(data['words']) for data in st.session_state.translations.values())
    
    col1, col2 = st.columns(2)
    col1.metric("Total Lines", total_lines)
    col2.metric("Total Words", total_words)
    
    # Export option
    st.subheader("Export Options")
    
    if st.button("Export as CSV"):
        # Prepare data for CSV
        export_data = []
        for line, trans in st.session_state.translations.items():
            export_data.append({
                "Bengali": line,
                "Hindi": trans['hindiLine']
            })
        
        # Create DataFrame and convert to CSV
        df = pd.DataFrame(export_data)
        csv = df.to_csv(index=False).encode('utf-8')
        
        # Create download button
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="bengali_hindi_translation.csv",
            mime="text/csv"
        )

# Add information about the translation engine
with st.expander("About the Translation Engine"):
    st.markdown("""
    ### Claude AI Translation
    
    This application uses Anthropic's Claude AI for high-quality translations:
    
    - **Advanced AI Understanding**: Claude understands context and nuances in language
    - **Better Literary Translation**: More accurate for poetry and literature than generic translation engines
    - **Cultural Context Awareness**: Understands cultural references in Bengali literature
    
    For best results:
    
    - Provide complete sentences for better context
    - For poetry, translate stanza by stanza
    - The API processes each translation request securely
    """)

# Add help
with st.expander("Help & Information"):
    st.markdown("""
    ### How to use this tool
    
    1. **Enter your Claude API key** in the settings panel
    2. **Paste Bengali text** in the input area
    3. Click the **Translate** button
    4. Choose between **Line-by-Line** or **Word-by-Word** view
    5. Use the **audio controls** to listen to Bengali pronunciation
    6. **Export** your translations as needed
    
    ### Features
    
    - High-quality translation from Bengali to Hindi using Claude AI
    - Audio playback for Bengali text
    - Word-by-word breakdown option
    - Export functionality
    """)

# Add footer
st.markdown("---")
st.markdown("*Bengali to Hindi Translator Tool powered by Claude AI*")
