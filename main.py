import streamlit as st
import json
import os
from gtts import gTTS
import time
import re
from googletrans import Translator, LANGUAGES
import base64
import pandas as pd

# Set page configuration
st.set_page_config(
    page_title="Bengali to Hindi Translator",
    page_icon="🔤",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .bengali-text {
        font-size: 18px;
        padding: 10px;
        background-color: #f0f8ff;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .hindi-text {
        font-size: 18px;
        padding: 10px;
        background-color: #fff0f5;
        border-radius: 5px;
        margin-bottom: 10px;
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
    .audio-button {
        margin-top: 5px;
        padding: 5px 10px;
        background-color: #2196F3;
        color: white;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }
    .line-container {
        padding: 10px;
        margin-bottom: 15px;
        border: 1px solid #ddd;
        border-radius: 5px;
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'translations' not in st.session_state:
    st.session_state.translations = {}

# Directory for audio files - use temp directory
audio_dir = "audio_files"
if not os.path.exists(audio_dir):
    os.makedirs(audio_dir)

# Function to get audio HTML
def get_audio_html(text, lang):
    """Generate audio for text and return HTML audio player"""
    try:
        # Create a unique filename
        filename = f"{audio_dir}/{lang}_{hash(text)}.mp3"
        
        # Generate audio if file doesn't exist
        if not os.path.exists(filename):
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(filename)
        
        # Read audio file as bytes
        with open(filename, "rb") as audio_file:
            audio_bytes = audio_file.read()
        
        # Encode to base64
        audio_base64 = base64.b64encode(audio_bytes).decode()
        
        # Create HTML audio element
        audio_html = f"""
        <audio controls>
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            Your browser does not support the audio element.
        </audio>
        """
        
        return audio_html
    
    except Exception as e:
        st.error(f"Audio error: {str(e)}")
        return ""

# Function to translate text
def translate_text(bengali_text):
    """Translate Bengali text to Hindi"""
    if not bengali_text:
        st.warning("Please enter Bengali text to translate.")
        return
    
    try:
        # Create translator
        translator = Translator()
        
        # Split the text into lines
        lines = bengali_text.split('\n')
        lines = [line.strip() for line in lines if line.strip()]
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Process each line
        for i, line in enumerate(lines):
            if line not in st.session_state.translations:
                status_text.text(f"Translating line {i+1} of {len(lines)}...")
                
                # Translate the whole line
                line_translation = translator.translate(line, src='bn', dest='hi').text
                
                # Split line into words and translate each
                words = re.findall(r'[\w\u0980-\u09FF]+|[^\w\s]', line)
                word_translations = []
                
                for j, word in enumerate(words):
                    if word.strip():
                        try:
                            word_trans = translator.translate(word, src='bn', dest='hi').text
                            pronunciation = word  # Placeholder for proper transliteration
                            word_translations.append({
                                'bengali': word,
                                'hindi': word_trans,
                                'pronunciation': pronunciation
                            })
                        except Exception:
                            word_translations.append({
                                'bengali': word,
                                'hindi': '?',
                                'pronunciation': word
                            })
                
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

# Header
st.title("Bengali to Hindi Translator")
st.markdown("Paste Bengali text below to get Hindi translation with audio support.")

# Input area
bengali_text = st.text_area("Input Bengali Text", height=150)

col1, col2 = st.columns([1, 5])
translate_button = col1.button("Translate")
clear_button = col2.button("Clear All")

# Handle clear button
if clear_button:
    st.session_state.translations = {}
    st.experimental_rerun()

# Translate when button is clicked
if translate_button and bengali_text:
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
            with st.container():
                st.markdown(f"<div class='line-container'>", unsafe_allow_html=True)
                
                # Line number and Bengali text
                st.markdown(f"<strong>Line {i+1}:</strong>", unsafe_allow_html=True)
                st.markdown(f"<div class='bengali-text'>{line}</div>", unsafe_allow_html=True)
                
                # Audio for Bengali
                bengali_audio = get_audio_html(line, 'bn')
                st.markdown(f"<div style='text-align: right;'>{bengali_audio}</div>", unsafe_allow_html=True)
                
                # Hindi translation based on view mode
                if view_mode == "Line-by-Line":
                    hindi_line = st.session_state.translations[line]['hindiLine']
                    st.markdown(f"<div class='hindi-text'>{hindi_line}</div>", unsafe_allow_html=True)
                    
                    # Audio for Hindi
                    hindi_audio = get_audio_html(hindi_line, 'hi')
                    st.markdown(f"<div style='text-align: right;'>{hindi_audio}</div>", unsafe_allow_html=True)
                
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
                
                st.markdown("</div>", unsafe_allow_html=True)
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

# Add information and help
with st.expander("Help & Information"):
    st.markdown("""
    ### How to use this tool
    
    1. **Paste Bengali text** in the input area
    2. Click the **Translate** button
    3. Choose between **Line-by-Line** or **Word-by-Word** view
    4. Use the **audio controls** to listen to pronunciation
    5. **Export** your translations as needed
    
    ### Features
    
    - Translation from Bengali to Hindi
    - Audio playback for both languages
    - Word-by-word breakdown option
    - Export functionality
    
    ### Notes
    
    - This tool uses Google Translate API
    - Audio quality depends on the text-to-speech engine
    - For best results, paste well-formatted Bengali text
    """)

# Add footer
st.markdown("---")
st.markdown("*Bengali to Hindi Translator Tool* | *Created with Streamlit*")
