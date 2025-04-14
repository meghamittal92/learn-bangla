import streamlit as st
import pandas as pd
import base64
from gtts import gTTS
import os
import tempfile
import time
import hashlib

def text_to_speech(text, lang='bn'):
    """Convert text to speech using gTTS and return the audio file path"""
    try:
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        temp_file.close()
        
        # Generate the audio
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(temp_file.name)
        
        return temp_file.name
    except Exception as e:
        st.error(f"Error generating audio: {e}")
        return None

def get_audio_html(audio_path):
    """Generate HTML for audio player"""
    audio_file = open(audio_path, "rb")
    audio_bytes = audio_file.read()
    audio_file.close()
    
    # Clean up the file after reading
    try:
        os.unlink(audio_path)
    except:
        pass
    
    audio_b64 = base64.b64encode(audio_bytes).decode()
    audio_html = f'''
        <audio controls>
            <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
            Your browser does not support the audio element.
        </audio>
    '''
    return audio_html

def audio_button(text, label="Listen", section="general"):
    """Create a button that plays audio when clicked"""
    # Create a deterministic but unique hash based on text and section
    # This ensures the same text in different sections gets different keys
    hash_input = f"{section}_{text}"
    hashed_key = hashlib.md5(hash_input.encode()).hexdigest()
    button_key = f"btn_{hashed_key}"
    
    if st.button(f"{label} 🔊", key=button_key):
        with st.spinner('Generating audio...'):
            audio_path = text_to_speech(text)
            if audio_path:
                st.markdown(get_audio_html(audio_path), unsafe_allow_html=True)
                return True
    return False

def main():
    st.set_page_config(page_title="Learn Bengali", layout="wide")
    st.title("বাংলা শেখার অ্যাপ (Bengali Learning App)")
    
    # Check if gtts is installed
    try:
        from gtts import gTTS
    except ImportError:
        st.error("Please install the required package using: pip install gTTS")
        st.info("This package is needed for the text-to-speech functionality.")
        return
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Introduction", "Letters & Vowels", "Words", "Grammar", "Story"])
    
    with tab1:
        st.header("Welcome to Bengali Learning App")
        st.write("""
        This app will help you learn Bengali through a simple children's story.
        Since you already know Hindi, you'll notice many similarities in the script and vocabulary.
        
        The story we'll learn is "রাজা ও তিনটি ছেলে" (The King and His Three Sons) - a classic Bengali folktale.
        
        Navigate through the tabs to learn letters, words, grammar, and finally read the story!
        """)
        
        st.subheader("Listen to the Introduction in Bengali:")
        intro_text = "বাংলা শেখার অ্যাপে আপনাকে স্বাগতম। এই অ্যাপের মাধ্যমে আপনি একটি সহজ বাংলা গল্প দিয়ে বাংলা শিখতে পারবেন।"
        audio_button(intro_text, "Listen to Introduction", "intro_section")
        
        st.image("https://via.placeholder.com/600x400.png?text=Bengali+Learning", caption="Learn Bengali")
    
    with tab2:
        st.header("Bengali Letters & Vowels")
        
        st.subheader("Letters (Consonants) in our story:")
        letters = [
            {"Letter": "র", "Pronunciation": "ro (like 'r' in Hindi)", "Similar to Hindi": "र"},
            {"Letter": "জ", "Pronunciation": "jo (like 'j' in Hindi)", "Similar to Hindi": "ज"},
            {"Letter": "ত", "Pronunciation": "to (like 't' in Hindi)", "Similar to Hindi": "त"},
            {"Letter": "ন", "Pronunciation": "no (like 'n' in Hindi)", "Similar to Hindi": "न"},
            {"Letter": "ট", "Pronunciation": "To (harder 't' sound)", "Similar to Hindi": "ट"},
            {"Letter": "ছ", "Pronunciation": "chho (aspirated 'ch')", "Similar to Hindi": "छ"},
            {"Letter": "ল", "Pronunciation": "lo (like 'l' in Hindi)", "Similar to Hindi": "ल"},
            {"Letter": "ক", "Pronunciation": "ko (like 'k' in Hindi)", "Similar to Hindi": "क"},
            {"Letter": "ব", "Pronunciation": "bo (like 'b' in Hindi)", "Similar to Hindi": "ब"},
            {"Letter": "স", "Pronunciation": "so/sho (like 's' in Hindi)", "Similar to Hindi": "स"},
            {"Letter": "ম", "Pronunciation": "mo (like 'm' in Hindi)", "Similar to Hindi": "म"},
            {"Letter": "য়", "Pronunciation": "yo (like 'y' in Hindi)", "Similar to Hindi": "य"},
            {"Letter": "প", "Pronunciation": "po (like 'p' in Hindi)", "Similar to Hindi": "प"},
            {"Letter": "ধ", "Pronunciation": "dho (aspirated 'd')", "Similar to Hindi": "ध"},
            {"Letter": "থ", "Pronunciation": "tho (aspirated 't')", "Similar to Hindi": "थ"},
        ]
        
        # Display letters with sound buttons
        df_letters = pd.DataFrame(letters)
        for i, row in df_letters.iterrows():
            col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
            with col1:
                st.markdown(f"### {row['Letter']}")
            with col2:
                st.write(f"**Pronunciation:** {row['Pronunciation']}")
            with col3:
                st.write(f"**Similar to Hindi:** {row['Similar to Hindi']}")
            with col4:
                audio_button(row['Letter'], "🔊", f"letter_{i}")
        
        st.subheader("Vowels and Vowel Signs:")
        vowels = [
            {"Vowel": "া", "Name": "aa-kar", "Pronunciation": "aa (like 'आ' in Hindi)", "Example": "রা (raa)"},
            {"Vowel": "ি", "Name": "i-kar", "Pronunciation": "i (like 'इ' in Hindi)", "Example": "তি (ti)"},
            {"Vowel": "ে", "Name": "e-kar", "Pronunciation": "e (like 'े' in Hindi)", "Example": "লে (le)"},
            {"Vowel": "ু", "Name": "u-kar", "Pronunciation": "u (like 'ु' in Hindi)", "Example": "তু (tu)"},
            {"Vowel": "ী", "Name": "dirgho-i", "Pronunciation": "ii (like 'ई' in Hindi)", "Example": "নী (nii)"},
        ]
        
        # Display vowels with sound buttons
        for i, row in pd.DataFrame(vowels).iterrows():
            col1, col2, col3, col4, col5 = st.columns([1, 1.5, 2, 1.5, 1])
            with col1:
                st.markdown(f"### {row['Vowel']}")
            with col2:
                st.write(f"**Name:** {row['Name']}")
            with col3:
                st.write(f"**Pronunciation:** {row['Pronunciation']}")
            with col4:
                st.write(f"**Example:** {row['Example']}")
            with col5:
                audio_button(row['Example'], "🔊", f"vowel_{i}")
        
        st.subheader("Special Characters:")
        special = [
            {"Character": "ং", "Name": "anusvara", "Pronunciation": "ng (like 'ं' in Hindi)", "Example": "বাং (bang)"},
            {"Character": "ঃ", "Name": "visarga", "Pronunciation": "h (like 'ः' in Hindi)", "Example": "দুঃখ (dukho)"},
            {"Character": "্", "Name": "hasanta", "Pronunciation": "consonant joiner (like '्' in Hindi)", "Example": "ক্ষ (ksha)"},
        ]
        
        # Display special characters with sound buttons
        for i, row in pd.DataFrame(special).iterrows():
            col1, col2, col3, col4, col5 = st.columns([1, 1.5, 2, 1.5, 1])
            with col1:
                st.markdown(f"### {row['Character']}")
            with col2:
                st.write(f"**Name:** {row['Name']}")
            with col3:
                st.write(f"**Pronunciation:** {row['Pronunciation']}")
            with col4:
                st.write(f"**Example:** {row['Example']}")
            with col5:
                audio_button(row['Example'], "🔊", f"special_{i}")
        
        st.subheader("Practice Pronouncing")
        with st.expander("Click to expand pronunciation guide"):
            st.write("""
            In Bengali, like Hindi, consonants inherently contain the sound 'o' (similar to 'अ' in Hindi).
            For example, 'ক' is pronounced as 'ko', not just 'k'.
            
            To remove this inherent vowel sound, use the hasanta (্) symbol.
            For example, 'ক্' is pronounced as just 'k'.
            """)
            
            st.subheader("Common Combinations")
            combinations = [
                {"Combo": "রা", "Pronunciation": "raa"},
                {"Combo": "জা", "Pronunciation": "jaa"},
                {"Combo": "তি", "Pronunciation": "ti"},
                {"Combo": "নে", "Pronunciation": "ne"},
                {"Combo": "ট", "Pronunciation": "To"},
            ]
            
            for i, row in pd.DataFrame(combinations).iterrows():
                col1, col2, col3 = st.columns([2, 3, 1])
                with col1:
                    st.markdown(f"### {row['Combo']}")
                with col2:
                    st.write(f"**Pronunciation:** {row['Pronunciation']}")
                with col3:
                    audio_button(row['Combo'], "🔊", f"combo_{i}")
    
    with tab3:
        st.header("Important Words in Our Story")
        
        words = [
            {"Bengali": "রাজা", "Pronunciation": "raja", "Meaning": "king"},
            {"Bengali": "ছেলে", "Pronunciation": "chhele", "Meaning": "boy/son"},
            {"Bengali": "তিনটি", "Pronunciation": "tin-ti", "Meaning": "three (with counter)"},
            {"Bengali": "বন", "Pronunciation": "bon", "Meaning": "forest"},
            {"Bengali": "যাওয়া", "Pronunciation": "jaowa", "Meaning": "to go"},
            {"Bengali": "দেখা", "Pronunciation": "dekha", "Meaning": "to see"},
            {"Bengali": "সোনা", "Pronunciation": "shona", "Meaning": "gold"},
            {"Bengali": "পাখি", "Pronunciation": "pakhi", "Meaning": "bird"},
            {"Bengali": "বলা", "Pronunciation": "bola", "Meaning": "to say/tell"},
            {"Bengali": "একটি", "Pronunciation": "ek-ti", "Meaning": "one (with counter)"},
            {"Bengali": "ফল", "Pronunciation": "phol", "Meaning": "fruit"},
            {"Bengali": "খাওয়া", "Pronunciation": "khaowa", "Meaning": "to eat"},
            {"Bengali": "নেওয়া", "Pronunciation": "neowa", "Meaning": "to take"},
            {"Bengali": "আসা", "Pronunciation": "asha", "Meaning": "to come"},
        ]
        
        # Display words with sound buttons
        for i, row in pd.DataFrame(words).iterrows():
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
            with col1:
                st.markdown(f"### {row['Bengali']}")
            with col2:
                st.write(f"**Pronunciation:** {row['Pronunciation']}")
            with col3:
                st.write(f"**Meaning:** {row['Meaning']}")
            with col4:
                audio_button(row['Bengali'], "🔊", f"word_{i}")
        
        st.subheader("Useful Phrases")
        phrases = [
            {"Bengali": "একদিন", "Pronunciation": "ekdin", "Meaning": "one day"},
            {"Bengali": "অনেক দূরে", "Pronunciation": "onek dure", "Meaning": "far away"},
            {"Bengali": "কিছুক্ষণ পরে", "Pronunciation": "kichhukkhon pore", "Meaning": "after some time"},
            {"Bengali": "বাড়ি ফিরে আসা", "Pronunciation": "bari fire asha", "Meaning": "to return home"},
            {"Bengali": "সুখে থাকা", "Pronunciation": "shukhe thaka", "Meaning": "to live happily"},
        ]
        
        # Display phrases with sound buttons
        for i, row in pd.DataFrame(phrases).iterrows():
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
            with col1:
                st.markdown(f"### {row['Bengali']}")
            with col2:
                st.write(f"**Pronunciation:** {row['Pronunciation']}")
            with col3:
                st.write(f"**Meaning:** {row['Meaning']}")
            with col4:
                audio_button(row['Bengali'], "🔊", f"phrase_{i}")
    
    with tab4:
        st.header("Basic Bengali Grammar")
        
        st.subheader("Sentence Structure")
        st.write("""
        Bengali, like Hindi, typically follows the Subject-Object-Verb (SOV) order:
        
        Example: আমি বই পড়ি (Ami boi pori) - "I book read" = "I read a book"
        
        This is similar to Hindi: मैं किताब पढ़ता हूँ
        """)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("**Listen to the example:**")
        with col2:
            audio_button("আমি বই পড়ি", "🔊", "grammar_example")
        
        st.subheader("Verb Forms")
        st.write("""
        Basic verb conjugation in Bengali is simpler than Hindi as it doesn't have gender agreement:
        
        Present tense example with "to go" (যাওয়া/jaowa):
        """)
        
        verbs_present = [
            {"Bengali": "আমি যাই", "Pronunciation": "ami jai", "Meaning": "I go"},
            {"Bengali": "তুমি যাও", "Pronunciation": "tumi jao", "Meaning": "You go"},
            {"Bengali": "সে যায়", "Pronunciation": "she jay", "Meaning": "He/She goes"},
        ]
        
        for i, row in pd.DataFrame(verbs_present).iterrows():
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
            with col1:
                st.markdown(f"### {row['Bengali']}")
            with col2:
                st.write(f"**Pronunciation:** {row['Pronunciation']}")
            with col3:
                st.write(f"**Meaning:** {row['Meaning']}")
            with col4:
                audio_button(row['Bengali'], "🔊", f"verb_present_{i}")
        
        st.write("""
        Past tense example:
        """)
        
        verbs_past = [
            {"Bengali": "আমি গেলাম", "Pronunciation": "ami gelam", "Meaning": "I went"},
            {"Bengali": "তুমি গেলে", "Pronunciation": "tumi gele", "Meaning": "You went"},
            {"Bengali": "সে গেল", "Pronunciation": "she gelo", "Meaning": "He/She went"},
        ]
        
        for i, row in pd.DataFrame(verbs_past).iterrows():
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
            with col1:
                st.markdown(f"### {row['Bengali']}")
            with col2:
                st.write(f"**Pronunciation:** {row['Pronunciation']}")
            with col3:
                st.write(f"**Meaning:** {row['Meaning']}")
            with col4:
                audio_button(row['Bengali'], "🔊", f"verb_past_{i}")
        
        st.subheader("Postpositions")
        st.write("""
        Like Hindi, Bengali uses postpositions instead of prepositions:
        """)
        
        postpos = [
            {"Bengali": "বনে", "Pronunciation": "bone", "Meaning": "in the forest (similar to Hindi \"वन में\")"},
            {"Bengali": "বাড়িতে", "Pronunciation": "barite", "Meaning": "in the house (similar to Hindi \"घर में\")"},
            {"Bengali": "রাজার", "Pronunciation": "rajar", "Meaning": "of the king (similar to Hindi \"राजा का\")"},
        ]
        
        for i, row in pd.DataFrame(postpos).iterrows():
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
            with col1:
                st.markdown(f"### {row['Bengali']}")
            with col2:
                st.write(f"**Pronunciation:** {row['Pronunciation']}")
            with col3:
                st.write(f"**Meaning:** {row['Meaning']}")
            with col4:
                audio_button(row['Bengali'], "🔊", f"postpos_{i}")
        
    with tab5:
        st.header("রাজা ও তিনটি ছেলে (The King and His Three Sons)")
        
        st.subheader("Story with Translation and Audio")
        
        story_lines = [
            "একদিন এক রাজা ছিলেন। তাঁর তিনটি ছেলে ছিল।",
            "রাজা তাঁর ছেলেদের বললেন, \"তোমরা বনে যাও এবং কিছু দেখে এসো।\"",
            "বড় ছেলে বনে গেল। সে একটি সোনার পাখি দেখল।",
            "সে বাড়ি ফিরে এসে রাজাকে বলল, \"আমি একটি সোনার পাখি দেখেছি।\"",
            "মেজো ছেলে বনে গেল। সে একটি সোনার গাছ দেখল।",
            "সে বাড়ি ফিরে এসে রাজাকে বলল, \"আমি একটি সোনার গাছ দেখেছি।\"",
            "ছোট ছেলে বনে গেল। সে একটি সোনার ফল দেখল। সে ফলটি খেয়ে ফেলল।",
            "তারপর বাড়ি ফিরে এসে রাজাকে বলল, \"আমি একটি সোনার ফল খেয়েছি।\"",
            "রাজা ছোট ছেলেকে বললেন, \"তুমি সোনার ফল খেয়ে ফেলেছ? সেটি তো অনেক মূল্যবান ছিল!\"",
            "ছোট ছেলে বলল, \"কিন্তু বাবা, আমি যখন ফলটি খেয়েছি, তখন আমার মুখ থেকে সোনার কথা বের হচ্ছে।\"",
            "রাজা অবাক হয়ে দেখলেন যে ছোট ছেলে যখন কথা বলে, তখন তার মুখ থেকে সোনা বের হয়।",
            "রাজা খুব খুশি হলেন এবং তাঁর ছোট ছেলেকে খুব ভালোবাসতে লাগলেন।"
        ]
        
        translation_lines = [
            "Once there was a king. He had three sons.",
            "The king said to his sons, \"Go to the forest and see something.\"",
            "The eldest son went to the forest. He saw a golden bird.",
            "He returned home and told the king, \"I saw a golden bird.\"",
            "The middle son went to the forest. He saw a golden tree.",
            "He returned home and told the king, \"I saw a golden tree.\"",
            "The youngest son went to the forest. He saw a golden fruit. He ate the fruit.",
            "Then he returned home and told the king, \"I ate a golden fruit.\"",
            "The king said to the youngest son, \"You ate the golden fruit? That was very valuable!\"",
            "The youngest son said, \"But father, when I ate the fruit, golden words come out of my mouth.\"",
            "The king was surprised to see that when the youngest son spoke, gold came out of his mouth.",
            "The king was very happy and loved his youngest son very much."
        ]
        
        # Display the story line by line with audio buttons
        for i, (bengali, english) in enumerate(zip(story_lines, translation_lines)):
            st.markdown(f"### Line {i+1}")
            col1, col2 = st.columns([1, 1])
            with col1:
                st.markdown(f"**Bengali:** {bengali}")
                audio_button(bengali, "Listen to Bengali 🔊", f"story_line_{i}")
            with col2:
                st.markdown(f"**English:** {english}")
        
        st.subheader("Listen to the Full Story")
        full_story = " ".join(story_lines)
        audio_button(full_story, "Listen to Full Story 🔊", "full_story")
            
        with st.expander("Vocabulary Breakdown"):
            st.write("""
            Key phrases from the story with detailed word-by-word breakdown:
            """)
            
            key_phrases = [
                {"Bengali": "একদিন এক রাজা ছিলেন", "Pronunciation": "ekdin ek raja chhilen", "Meaning": "Once there was a king", 
                 "Breakdown": [
                     {"Word": "একদিন", "Meaning": "one day", "Note": "এক (ek) = one + দিন (din) = day"},
                     {"Word": "এক", "Meaning": "a/one", "Note": "indefinite article"},
                     {"Word": "রাজা", "Meaning": "king", "Note": "similar to Hindi राजा (raja)"},
                     {"Word": "ছিলেন", "Meaning": "was/were (formal)", "Note": "past tense of थे/था in Hindi"}
                 ]},
                {"Bengali": "তাঁর তিনটি ছেলে ছিল", "Pronunciation": "tar tinti chhele chhilo", "Meaning": "He had three sons", 
                 "Breakdown": [
                     {"Word": "তাঁর", "Meaning": "his/her (formal)", "Note": "possessive pronoun, respectful form"},
                     {"Word": "তিনটি", "Meaning": "three", "Note": "তিন (tin) = three + টি (ti) = counter/classifier"},
                     {"Word": "ছেলে", "Meaning": "boy/son", "Note": "similar to छोरा in some Hindi dialects"},
                     {"Word": "ছিল", "Meaning": "was/were (informal)", "Note": "past tense, informal form"}
                 ]},
                {"Bengali": "বনে যাও", "Pronunciation": "bone jao", "Meaning": "Go to the forest", 
                 "Breakdown": [
                     {"Word": "বনে", "Meaning": "in the forest", "Note": "বন (bon) = forest + এ (e) = locative case ending"},
                     {"Word": "যাও", "Meaning": "go", "Note": "imperative form of যাওয়া (jaowa) = to go"}
                 ]},
                {"Bengali": "কিছু দেখে এসো", "Pronunciation": "kichhu dekhe esho", "Meaning": "See something and come back", 
                 "Breakdown": [
                     {"Word": "কিছু", "Meaning": "something", "Note": "similar to कुछ (kuchh) in Hindi"},
                     {"Word": "দেখে", "Meaning": "seeing/having seen", "Note": "perfective participle of দেখা (dekha) = to see"},
                     {"Word": "এসো", "Meaning": "come back", "Note": "imperative form of আসা (asha) = to come"}
                 ]},
                {"Bengali": "সোনার পাখি", "Pronunciation": "shonar pakhi", "Meaning": "Golden bird", 
                 "Breakdown": [
                     {"Word": "সোনার", "Meaning": "golden/of gold", "Note": "সোনা (shona) = gold + র (r) = possessive marker"},
                     {"Word": "পাখি", "Meaning": "bird", "Note": "similar to पंछी (panchhi) in Hindi"}
                 ]},
                {"Bengali": "বাড়ি ফিরে এসে", "Pronunciation": "bari fire eshe", "Meaning": "Having returned home", 
                 "Breakdown": [
                     {"Word": "বাড়ি", "Meaning": "home/house", "Note": "similar to बाड़ी in some Hindi dialects"},
                     {"Word": "ফিরে", "Meaning": "having returned", "Note": "perfective participle of ফেরা (phera) = to return"},
                     {"Word": "এসে", "Meaning": "having come", "Note": "perfective participle of আসা (asha) = to come"}
                 ]},
                {"Bengali": "সোনার ফল খেয়েছি", "Pronunciation": "shonar fol kheyechhi", "Meaning": "I ate a golden fruit", 
                 "Breakdown": [
                     {"Word": "সোনার", "Meaning": "golden/of gold", "Note": "সোনা (shona) = gold + র (r) = possessive marker"},
                     {"Word": "ফল", "Meaning": "fruit", "Note": "similar to फल (phal) in Hindi"},
                     {"Word": "খেয়েছি", "Meaning": "I have eaten", "Note": "present perfect of খাওয়া (khaowa) = to eat, 1st person"}
                 ]},
                {"Bengali": "অনেক মূল্যবান", "Pronunciation": "onek mulloban", "Meaning": "Very valuable", 
                 "Breakdown": [
                     {"Word": "অনেক", "Meaning": "very/much", "Note": "similar to अनेक (anek) in Hindi"},
                     {"Word": "মূল্যবান", "Meaning": "valuable", "Note": "মূল্য (mullo) = value + বান (ban) = possessing"}
                 ]},
                {"Bengali": "সোনার কথা", "Pronunciation": "shonar kotha", "Meaning": "Golden words", 
                 "Breakdown": [
                     {"Word": "সোনার", "Meaning": "golden/of gold", "Note": "সোনা (shona) = gold + র (r) = possessive marker"},
                     {"Word": "কথা", "Meaning": "words/speech", "Note": "similar to कथा (katha) in Hindi"}
                 ]},
                {"Bengali": "খুব খুশি", "Pronunciation": "khub khushi", "Meaning": "Very happy", 
                 "Breakdown": [
                     {"Word": "খুব", "Meaning": "very", "Note": "similar to खूब (khub) in Hindi"},
                     {"Word": "খুশি", "Meaning": "happy", "Note": "similar to खुशी (khushi) in Hindi"}
                 ]},
            ]
            
            # Display phrases with sound buttons and word breakdowns
            for i, row in pd.DataFrame(key_phrases).iterrows():
                st.markdown(f"### {i+1}. {row['Bengali']}")
                col1, col2, col3 = st.columns([2, 3, 1])
                with col1:
                    st.write(f"**Pronunciation:** {row['Pronunciation']}")
                with col2:
                    st.write(f"**Meaning:** {row['Meaning']}")
                with col3:
                    audio_button(row['Bengali'], "🔊", f"key_phrase_{i}")
                
                # Word-by-word breakdown
                st.write("**Word-by-word breakdown:**")
                breakdown_data = row['Breakdown']
                breakdown_df = pd.DataFrame(breakdown_data)
                
                for j, word_row in breakdown_df.iterrows():
                    word_col1, word_col2, word_col3, word_col4 = st.columns([1.5, 2, 2.5, 1])
                    with word_col1:
                        st.markdown(f"**{word_row['Word']}**")
                    with word_col2:
                        st.write(f"Meaning: {word_row['Meaning']}")
                    with word_col3:
                        st.write(f"Note: {word_row['Note']}")
                    with word_col4:
                        audio_button(word_row['Word'], "🔊", f"word_breakdown_{i}_{j}")
                
                st.markdown("---")
            
        st.subheader("Practice Reading")
        st.write("Try reading the story line by line, using the pronunciation guide and audio buttons for help.")
        
        st.subheader("Learn More")
        st.write("""
        This is just a simple introduction to Bengali. To learn more:
        
        1. Practice reading the story out loud
        2. Learn more vocabulary through the words tab
        3. Start with simple sentences using the grammar patterns shown
        4. Remember that knowing Hindi gives you an advantage as many concepts are similar!
        """)

if __name__ == "__main__":
    main()
