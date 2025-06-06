# -*- coding: utf-8 -*-
"""
Handles all user interaction, including prompts and displaying results.
"""

LANGUAGES = {
    'en': 'English', 'es': 'Spanish', 'fr': 'French', 'de': 'German',
    'it': 'Italian', 'pl': 'Polish', 'pt': 'Portuguese', 'ru': 'Russian',
    'ja': 'Japanese', 'ko': 'Korean', 'zh': 'Chinese'
}

SUMMARY_TYPES = {
    '1': 'Brief summary (2-3 sentences)',
    '2': 'Detailed summary with key points',
    '3': 'Bullet-point summary'
}

def display_welcome_message():
    """Prints a welcome message to the console."""
    print("\n--- YouTube Transcript Summarizer & Translator ---")
    print("Welcome! This tool will download, summarize, and translate a YouTube video transcript.")

def get_youtube_url():
    """Prompts the user to enter a YouTube video URL."""
    return input("\nPlease enter the YouTube video URL: ")

def get_target_language():
    """Prompts the user to select a target language for translation."""
    print("\nPlease select a target language for translation:")
    for code, name in LANGUAGES.items():
        print(f"  {code}: {name}")
    
    while True:
        choice = input("Enter the language code (e.g., 'es' for Spanish): ").lower()
        if choice in LANGUAGES:
            return choice, LANGUAGES[choice]
        print("Invalid code. Please try again.")

def get_ollama_model(models):
    """Prompts the user to select an available Ollama model."""
    print("\nPlease select an Ollama model to use for summarization:")
    for i, model in enumerate(models, 1):
        print(f"  {i}: {model}")
    
    while True:
        try:
            choice = int(input(f"Enter the number of the model (1-{len(models)}): "))
            if 1 <= choice <= len(models):
                return models[choice - 1]
            else:
                print("Invalid number. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def get_summary_type():
    """Prompts the user to select the type of summary."""
    print("\nPlease select the type of summary you want:")
    for key, value in SUMMARY_TYPES.items():
        print(f"  {key}: {value}")
    
    while True:
        choice = input(f"Enter your choice (1-{len(SUMMARY_TYPES)}): ")
        if choice in SUMMARY_TYPES:
            return SUMMARY_TYPES[choice]
        print("Invalid choice. Please try again.")

def display_results(original_summary, translated_summary):
    """Displays the final summaries to the user."""
    print("\n" + "="*50)
    print("                  RESULTS                  ")
    print("="*50 + "\n")
    
    print("--- Original Summary ---")
    print(original_summary)
    print("\n" + "-"*50 + "\n")
    
    print("--- Translated Summary ---")
    print(translated_summary)
    print("\n" + "="*50)
    print("All files have been saved to the 'output' directory.")

def display_feedback(message):
    """Prints a status/feedback message."""
    print(f"[INFO] {message}")

def display_error(message):
    """Prints an error message."""
    print(f"[ERROR] {message}")