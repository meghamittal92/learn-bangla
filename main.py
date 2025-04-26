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
from googletrans import Translator

# Set page configuration
st.set_page_config(
    page_title="Bengali to Hindi Translator",
    page_icon="🔤",
    layout="wide"
)

# Custom CSS with fixes for display issues and text visibility
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
        color: #000000;  /* Black text for contrast */
        border: 1px solid #b3d1ff;  /* Add border for definition */
    }
    .hindi-text {
        font-size: 18px;
        padding: 10px;
        background-color: #fff0f5;
        border-radius: 5px;
        margin: 10px 0;
        display: block;
        width: 100%;
        color: #000000;  /* Black text for contrast */
        border: 1px solid #ffb3d1;  /* Add border for definition */
    }
    .word-card {
        display: inline-block;
        padding: 8px;
        margin: 4px;
        background-color: #e6f7ff;
        border-radius: 5px;
        border: 1px solid #b3e0ff;
        color: #000000;  /* Ensure text is black */
    }
    .word-bengali {
        font-size: 16px;
        font-weight: bold;
        color: #000000;  /* Black text */
    }
    .word-hindi {
        font-size: 16px;
        color: #0066cc;  /* Dark blue for contrast */
    }
    .line-container {
        padding: 10px;
        margin-bottom: 15px;
        border: 1px solid #ddd;
        border-radius: 5px;
        background-color: #f8f9fa;  /* Light gray background */
        display: block;
        width: 100%;
    }
    div[data-testid="stVerticalBlock"] {
        gap: 0;
    }
    /* Ensure all text in markdown is visible */
    p, h1, h2, h3, h4, h5, h6, li, div {
        color: #000000;
    }
    /* High contrast for section headers */
    .section-header {
        font-weight: bold;
        color: #000000 !important;
        background-color: #f2f2f2;
        padding: 5px;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'translations' not in st.session_state:
    st.session_state.translations = {}

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

# Function to provide better translations using a custom dictionary
def translate_using_dictionary(text):
    """Use a custom dictionary for better translations"""
    # Dictionary of pre-translated Bengali poems and common phrases
    translations = {
        "আকাশ ভরা সূর্য তারা": "आकाश भरा सूरज तारे",
        "বিশ্ব ভরা প্রাণ": "विश्व भरा प्राण",
        "তাহারি মাঝখানে আমি": "उनके बीच में मैं",
        "পেয়েছি মোর স্থান।": "पाया है अपना स्थान।",
        "বিস্ময়ে তাই জাগে আমার গান।": "विस्मय से इसलिए जागे मेरा गान।",
        # Additional translations for common Bengali phrases
        "নমস্কার": "नमस्कार",
        "ধন্যবাদ": "धन्यवाद",
        "আমি তোমাকে ভালোবাসি": "मैं तुमसे प्यार करता हूँ",
        "সুপ্রভাত": "सुप्रभात",
        "শুভ রাত্রি": "शुभ रात्रि",
        "আপনি কেমন আছেন?": "आप कैसे हैं?",
        "আমি ভালো আছি": "मैं अच्छा हूँ",
        "আমার নাম": "मेरा नाम",
        "বাংলা": "बंगाली",
        "হিন্দি": "हिंदी",
    }
    
    # Check if the exact phrase is in our dictionary
    if text in translations:
        return translations[text]
    
    # If not, use Google Translate
    try:
        translator = Translator()
        return translator.translate(text, src='bn', dest='hi').text
    except Exception as e:
        st.warning(f"Translation fallback error: {str(e)}")
        
        # Very basic character mapping as ultimate fallback
        bengali_to_hindi = {
            'অ': 'अ', 'আ': 'आ', 'ই': 'इ', 'ঈ': 'ई', 'উ': 'उ', 'ঊ': 'ऊ',
            'এ': 'ए', 'ঐ': 'ऐ', 'ও': 'ओ', 'ঔ': 'औ', 'ক': 'क', 'খ': 'ख',
            'গ': 'ग', 'ঘ': 'घ', 'ঙ': 'ङ', 'চ': 'च', 'ছ': 'छ', 'জ': 'ज',
            'ঝ': 'झ', 'ঞ': 'ञ', 'ট': 'ट', 'ঠ': 'ठ', 'ড': 'ड', 'ঢ': 'ढ',
            'ণ': 'ण', 'ত': 't', 'থ': 'थ', 'দ': 'द', 'ধ': 'ध', 'ন': 'न',
            'প': 'प', 'ফ': 'फ', 'ব': 'ब', 'ভ': 'भ', 'ম': 'म', 'য': 'य',
            'র': 'र', 'ল': 'ल', 'শ': 'श', 'ষ': 'ष', 'স': 'स', 'হ': 'ह',
            'ড়': 'ड़', 'ঢ়': 'ढ़', 'য়': 'य', 'ৎ': 'त्', 'ং': 'ं', 'ঃ': 'ः',
            'ঁ': 'ँ', '।': '।'
        }
        
        result = ""
        for char in text:
            if char in bengali_to_hindi:
                result += bengali_to_hindi[char]
            else:
                result += char
        return result

# Function to translate text with progress tracking
def translate_text(bengali_text):
    """Translate Bengali text to Hindi"""
    if not bengali_text:
        st.warning("Please enter Bengali text to translate.")
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
                
                # Translate the whole line using dictionary + Google Translate
                line_translation = translate_using_dictionary(line)
                
                # Split line into words and translate each
                words = re.findall(r'[\w\u0980-\u09FF]+|[^\w\s]', line)
                word_translations = []
                
                for j, word in enumerate(words):
                    if word.strip():
                        try:
                            word_trans = translate_using_dictionary(word)
                            word_translations.append({
                                'bengali': word,
                                'hindi': word_trans
                            })
                        except Exception:
                            word_translations.append({
                                'bengali': word,
                                'hindi': '?'
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

# Add information in the sidebar
with st.sidebar:
    st.header("About This Translator")
    st.markdown("""
    ### Bengali to Hindi Translator
    
    This application translates Bengali text to Hindi using an enhanced translation approach:
    
    - **Custom Dictionary**: For common Bengali phrases and poetry
    - **Google Translate API**: For general translation
    - **Character Mapping**: As a fallback mechanism
    
    The translator is optimized for Rabindranath Tagore's poetry and common phrases.
    """)
    
    st.markdown("---")
    
    st.markdown("""
    ### Tips for Best Results
    
    - For poetry, translate stanza by stanza
    - Complete sentences translate better than isolated words
    - Some idiomatic expressions may not translate perfectly
    """)

# Header with clear styling
st.markdown('<h1 style="color: #000000;">Bengali to Hindi Translator</h1>', unsafe_allow_html=True)
st.markdown('<p style="color: #000000; font-size: 16px;">Paste Bengali text below to get Hindi translation with audio support.</p>', unsafe_allow_html=True)

# Input area - ensure text is visible
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
    st.markdown('<h2 class="section-header">Translation Results</h2>', unsafe_allow_html=True)
    
    # Split into lines
    lines = bengali_text.split('\n')
    lines = [line.strip() for line in lines if line.strip()]
    
    # Create a table-like structure for display
    for i, line in enumerate(lines):
        if line in st.session_state.translations:
            # Display container with explicit styling
            st.markdown(f'<div style="padding: 10px; margin-bottom: 10px; border: 1px solid #ddd; border-radius: 5px; background-color: #f8f9fa;">', unsafe_allow_html=True)
            
            # Line number with clear styling
            st.markdown(f'<h3 style="color: #000000; margin-bottom: 10px;">Line {i+1}</h3>', unsafe_allow_html=True)
            
            # Use columns instead of containers for better layout
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown(f'<p style="color: #000000; font-weight: bold;">Bengali:</p>', unsafe_allow_html=True)
                # Use a div with explicit styling to ensure visibility
                st.markdown(f'<div class="bengali-text">{line}</div>', unsafe_allow_html=True)
                bengali_audio = get_audio_html(line, 'bn')
                st.markdown(bengali_audio, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f'<p style="color: #000000; font-weight: bold;">Hindi Translation:</p>', unsafe_allow_html=True)
                # Hindi translation based on view mode
                if view_mode == "Line-by-Line":
                    hindi_line = st.session_state.translations[line]['hindiLine']
                    st.markdown(f'<div class="hindi-text">{hindi_line}</div>', unsafe_allow_html=True)
                    # No audio for Hindi as requested
                
                else:  # Word-by-Word
                    word_html = '<div style="display: flex; flex-wrap: wrap;">'
                    for word_data in st.session_state.translations[line]['words']:
                        word_html += f"""
                        <div class="word-card">
                            <div class="word-bengali">{word_data['bengali']}</div>
                            <div class="word-hindi">{word_data['hindi']}</div>
                        </div>
                        """
                    word_html += "</div>"
                    st.markdown(word_html, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

# Add stats and export options if translations exist
if st.session_state.translations:
    st.markdown('<h2 class="section-header">Statistics</h2>', unsafe_allow_html=True)
    
    # Calculate statistics
    total_lines = len(st.session_state.translations)
    total_words = sum(len(data['words']) for data in st.session_state.translations.values())
    
    col1, col2 = st.columns(2)
    col1.metric("Total Lines", total_lines)
    col2.metric("Total Words", total_words)
    
    # Export option
    st.markdown('<h2 class="section-header">Export Options</h2>', unsafe_allow_html=True)
    
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

# Add help with proper styling
with st.expander("Help & Information"):
    st.markdown("""
    ### How to use this tool
    
    1. **Paste Bengali text** in the input area
    2. Click the **Translate** button
    3. Choose between **Line-by-Line** or **Word-by-Word** view
    4. Use the **audio controls** to listen to Bengali pronunciation
    5. **Export** your translations as needed
    
    ### Features
    
    - Translation from Bengali to Hindi
    - Audio playback for Bengali text
    - Word-by-word breakdown option
    - Export functionality
    
    ### Sample Bengali Text
    
    Try this sample poem by Rabindranath Tagore:
    
    ```
    আকাশ ভরা সূর্য তারা,
    বিশ্ব ভরা প্রাণ
    তাহারি মাঝখানে আমি
    পেয়েছি মোর স্থান।

    বিস্ময়ে তাই জাগে আমার গান।
    ```
    """)

# Add footer with explicit styling
st.markdown('<hr style="margin-top: 30px; margin-bottom: 10px;">', unsafe_allow_html=True)
st.markdown('<p style="color: #000000; text-align: center;">Bengali to Hindi Translator Tool</p>', unsafe_allow_html=True)
