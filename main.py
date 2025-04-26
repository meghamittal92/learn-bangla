import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
import json
import os
from gtts import gTTS
import pygame
import time
from googletrans import Translator
import re

class BengaliHindiTranslator:
    def __init__(self, root):
        self.root = root
        self.root.title("Bengali to Hindi Translator")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f0f0")
        
        # Initialize pygame mixer for audio playback
        pygame.mixer.init()
        
        # Initialize Google Translator
        self.translator = Translator()
        
        # Dictionary to store translations
        self.translations = {}
        
        # Create the main frame
        main_frame = tk.Frame(root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create the input frame
        input_frame = tk.LabelFrame(main_frame, text="Input Bengali Text", bg="#f0f0f0", font=("Arial", 12))
        input_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Bengali text input
        self.bengali_text = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD, font=("Arial", 12), height=8)
        self.bengali_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Control frame
        control_frame = tk.Frame(main_frame, bg="#f0f0f0")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Translation button
        self.translate_btn = tk.Button(control_frame, text="Translate", command=self.translate_text, 
                                      bg="#4CAF50", fg="white", font=("Arial", 12), width=15)
        self.translate_btn.pack(side=tk.LEFT, padx=5)
        
        # Clear button
        self.clear_btn = tk.Button(control_frame, text="Clear", command=self.clear_all, 
                                  bg="#f44336", fg="white", font=("Arial", 12), width=15)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # View mode selection
        self.view_mode = tk.StringVar(value="line")
        view_frame = tk.Frame(control_frame, bg="#f0f0f0")
        view_frame.pack(side=tk.RIGHT, padx=5)
        
        tk.Label(view_frame, text="View Mode:", bg="#f0f0f0", font=("Arial", 12)).pack(side=tk.LEFT)
        tk.Radiobutton(view_frame, text="Line", variable=self.view_mode, value="line", 
                      command=self.update_view, bg="#f0f0f0", font=("Arial", 10)).pack(side=tk.LEFT)
        tk.Radiobutton(view_frame, text="Word", variable=self.view_mode, value="word", 
                      command=self.update_view, bg="#f0f0f0", font=("Arial", 10)).pack(side=tk.LEFT)
        
        # Output frame
        self.output_frame = tk.LabelFrame(main_frame, text="Translation", bg="#f0f0f0", font=("Arial", 12))
        self.output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Translation output - will be populated dynamically
        self.translation_canvas = tk.Canvas(self.output_frame, bg="white")
        self.translation_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar for the canvas
        self.scrollbar = tk.Scrollbar(self.translation_canvas, command=self.translation_canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.translation_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Create a frame inside the canvas
        self.translation_frame = tk.Frame(self.translation_canvas, bg="white")
        self.canvas_frame = self.translation_canvas.create_window((0, 0), window=self.translation_frame, anchor="nw")
        
        # Update the scroll region when the size of the frame changes
        self.translation_frame.bind("<Configure>", self.on_frame_configure)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = tk.Label(root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Directory for audio files
        self.audio_dir = "audio_files"
        if not os.path.exists(self.audio_dir):
            os.makedirs(self.audio_dir)
    
    def on_frame_configure(self, event):
        """Update the scroll region based on the size of the frame"""
        self.translation_canvas.configure(scrollregion=self.translation_canvas.bbox("all"))
    
    def translate_text(self):
        """Translate the Bengali text to Hindi"""
        # Get the Bengali text
        bengali_text = self.bengali_text.get("1.0", tk.END).strip()
        
        if not bengali_text:
            messagebox.showwarning("Warning", "Please enter Bengali text to translate.")
            return
        
        # Update status
        self.status_var.set("Translating...")
        self.root.update()
        
        try:
            # Split the text into lines
            lines = bengali_text.split('\n')
            lines = [line.strip() for line in lines if line.strip()]
            
            # Process each line
            for line in lines:
                if line not in self.translations:
                    # Translate the whole line
                    line_translation = self.translator.translate(line, src='bn', dest='hi').text
                    
                    # Split line into words and translate each
                    words = re.findall(r'[\w\u0980-\u09FF]+|[^\w\s]', line)
                    word_translations = []
                    
                    for word in words:
                        if word.strip():
                            try:
                                word_trans = self.translator.translate(word, src='bn', dest='hi').text
                                pronunciation = word  # In a real app, we'd use a proper transliteration API
                                word_translations.append({
                                    'bengali': word,
                                    'hindi': word_trans,
                                    'pronunciation': pronunciation
                                })
                            except Exception as e:
                                word_translations.append({
                                    'bengali': word,
                                    'hindi': '?',
                                    'pronunciation': word
                                })
                    
                    # Store the translations
                    self.translations[line] = {
                        'hindiLine': line_translation,
                        'words': word_translations
                    }
            
            # Update the display
            self.update_view()
            
            # Update status
            self.status_var.set(f"Translation completed. {len(lines)} lines processed.")
        
        except Exception as e:
            messagebox.showerror("Error", f"Translation error: {str(e)}")
            self.status_var.set("Translation failed.")
    
    def update_view(self):
        """Update the translation view based on selected mode"""
        # Clear previous translations
        for widget in self.translation_frame.winfo_children():
            widget.destroy()
        
        # Get Bengali text and split into lines
        bengali_text = self.bengali_text.get("1.0", tk.END).strip()
        lines = bengali_text.split('\n')
        lines = [line.strip() for line in lines if line.strip()]
        
        # Current view mode
        mode = self.view_mode.get()
        
        # Display translations
        for i, line in enumerate(lines):
            if line in self.translations:
                # Create a frame for this line
                line_frame = tk.Frame(self.translation_frame, bg="white", bd=1, relief=tk.GROOVE)
                line_frame.pack(fill=tk.X, padx=5, pady=5)
                
                # Line number
                tk.Label(line_frame, text=f"{i+1}.", bg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
                
                # Bengali text
                tk.Label(line_frame, text=line, bg="white", font=("Arial", 12), wraplength=400, justify=tk.LEFT).pack(anchor=tk.W, padx=5, pady=2)
                
                # Listen button
                listen_btn = tk.Button(line_frame, text="🔊", command=lambda l=line: self.play_audio(l, 'bn'),
                                     bg="#2196F3", fg="white", font=("Arial", 10))
                listen_btn.pack(side=tk.RIGHT, padx=5)
                
                # Hindi translation
                hindi_line = self.translations[line]['hindiLine']
                
                if mode == "line":
                    # Line view
                    hindi_frame = tk.Frame(line_frame, bg="white")
                    hindi_frame.pack(fill=tk.X, padx=5, pady=2)
                    
                    tk.Label(hindi_frame, text=hindi_line, bg="#e6f7ff", font=("Arial", 12), 
                           wraplength=400, justify=tk.LEFT).pack(anchor=tk.W, padx=5, pady=2, fill=tk.X)
                    
                    # Listen button for Hindi
                    tk.Button(hindi_frame, text="🔊", command=lambda l=hindi_line: self.play_audio(l, 'hi'),
                           bg="#2196F3", fg="white", font=("Arial", 10)).pack(side=tk.RIGHT, padx=5)
                    
                else:
                    # Word view
                    word_frame = tk.Frame(line_frame, bg="white")
                    word_frame.pack(fill=tk.X, padx=5, pady=2)
                    
                    for word_data in self.translations[line]['words']:
                        word_box = tk.Frame(word_frame, bg="#e6f7ff", bd=1, relief=tk.RAISED)
                        word_box.pack(side=tk.LEFT, padx=2, pady=2)
                        
                        tk.Label(word_box, text=word_data['bengali'], bg="#e6f7ff", font=("Arial", 11)).pack(anchor=tk.W)
                        tk.Label(word_box, text=word_data['hindi'], bg="#e6f7ff", fg="#0066cc", font=("Arial", 11)).pack(anchor=tk.W)
                        
                        # Listen button for word
                        tk.Button(word_box, text="🔊", command=lambda w=word_data['bengali']: self.play_audio(w, 'bn'),
                               bg="#2196F3", fg="white", font=("Arial", 8), width=2, height=1).pack(side=tk.RIGHT, padx=2)
        
        # Update scroll region
        self.translation_canvas.update_idletasks()
        self.translation_canvas.configure(scrollregion=self.translation_canvas.bbox("all"))
    
    def play_audio(self, text, language):
        """Generate and play audio for the text"""
        try:
            # Create a unique filename
            filename = f"{self.audio_dir}/{language}_{hash(text)}.mp3"
            
            # Generate audio if file doesn't exist
            if not os.path.exists(filename):
                self.status_var.set(f"Generating audio...")
                self.root.update()
                
                tts = gTTS(text=text, lang=language, slow=False)
                tts.save(filename)
            
            # Play the audio
            self.status_var.set(f"Playing audio...")
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            
            # Wait for audio to finish
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
                self.root.update()
            
            self.status_var.set("Ready")
        
        except Exception as e:
            messagebox.showerror("Error", f"Audio error: {str(e)}")
            self.status_var.set("Audio playback failed.")
    
    def clear_all(self):
        """Clear all inputs and translations"""
        self.bengali_text.delete("1.0", tk.END)
        self.translations = {}
        
        # Clear translation display
        for widget in self.translation_frame.winfo_children():
            widget.destroy()
        
        self.status_var.set("Ready")

def main():
    root = tk.Tk()
    app = BengaliHindiTranslator(root)
    root.mainloop()

if __name__ == "__main__":
    main()
