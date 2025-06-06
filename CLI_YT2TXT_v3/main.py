#!/usr/bin/env python3
"""
YouTube Transcript Processor - Main Entry Point

This application downloads YouTube transcripts, detects language,
translates content, and generates summaries using local LLM models.
"""

import os
import sys
from modules.transcript_downloader import TranscriptDownloader
from modules.language_detector import LanguageDetector
from modules.translator import Translator
from modules.llm_processor import LLMProcessor
from modules.file_utils import FileUtils

# Supported languages for translation
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'es': 'Spanish', 
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pl': 'Polish',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'ja': 'Japanese',
    'ko': 'Korean',
    'zh': 'Chinese'
}

# Summary types
SUMMARY_TYPES = {
    '1': 'brief',
    '2': 'detailed', 
    '3': 'bullet'
}

def print_banner():
    """Print application banner."""
    print("=" * 60)
    print("         YOUTUBE TRANSCRIPT PROCESSOR")
    print("=" * 60)
    print("Features:")
    print("• Download YouTube video transcripts")
    print("• Automatic language detection")
    print("• Multi-language translation")
    print("• AI-powered summarization with local LLMs")
    print("=" * 60)
    print()

def get_youtube_url():
    """Get and validate YouTube URL from user."""
    print("📹 STEP 1: YouTube Video URL")
    print("-" * 30)
    
    while True:
        url = input("Enter YouTube video URL: ").strip()
        if not url:
            print("❌ Please enter a valid URL.")
            continue
            
        # Basic URL validation
        if 'youtube.com' in url or 'youtu.be' in url:
            return url
        else:
            print("❌ Please enter a valid YouTube URL.")

def get_target_language():
    """Get target language selection from user."""
    print("\n🌍 STEP 2: Target Language Selection")
    print("-" * 40)
    print("Available languages:")
    
    # Display languages in a formatted way
    lang_items = list(SUPPORTED_LANGUAGES.items())
    for i in range(0, len(lang_items), 2):
        left = f"  {lang_items[i][0]}: {lang_items[i][1]}"
        if i + 1 < len(lang_items):
            right = f"{lang_items[i+1][0]}: {lang_items[i+1][1]}"
            print(f"{left:<25} {right}")
        else:
            print(left)
    
    while True:
        target_lang = input("\nSelect target language code: ").strip().lower()
        if target_lang in SUPPORTED_LANGUAGES:
            print(f"✅ Selected: {SUPPORTED_LANGUAGES[target_lang]}")
            return target_lang
        print("❌ Please select a valid language code from the list above.")

def get_summary_type():
    """Get summary type selection from user."""
    print("\n📝 STEP 3: Summary Type Selection")
    print("-" * 35)
    print("Summary options:")
    print("  1: Brief summary (2-3 sentences)")
    print("  2: Detailed summary with key points")
    print("  3: Bullet-point summary")
    
    while True:
        summary_choice = input("\nSelect summary type (1-3): ").strip()
        if summary_choice in SUMMARY_TYPES:
            summary_type = SUMMARY_TYPES[summary_choice]
            type_descriptions = {
                'brief': 'Brief summary (2-3 sentences)',
                'detailed': 'Detailed summary with key points',
                'bullet': 'Bullet-point summary'
            }
            print(f"✅ Selected: {type_descriptions[summary_type]}")
            return summary_type
        print("❌ Please select 1, 2, or 3.")

def get_llm_model(llm_processor):
    """Get LLM model selection from user."""
    print("\n🤖 STEP 4: LLM Model Selection")
    print("-" * 32)
    print("Checking available Ollama models...")
    
    models = llm_processor.get_available_models()
    if not models:
        print("❌ No Ollama models found!")
        print("\nTo fix this:")
        print("1. Make sure Ollama is installed and running")
        print("2. Install at least one model, for example:")
        print("   ollama pull llama2")
        print("   ollama pull mistral")
        print("   ollama pull codellama")
        return None
    
    print(f"✅ Found {len(models)} available model(s):")
    for i, model in enumerate(models, 1):
        print(f"  {i}: {model}")
    
    while True:
        try:
            choice = int(input(f"\nSelect model (1-{len(models)}): "))
            if 1 <= choice <= len(models):
                selected_model = models[choice - 1]
                print(f"✅ Selected: {selected_model}")
                return selected_model
            print(f"❌ Please enter a number between 1 and {len(models)}.")
        except ValueError:
            print("❌ Please enter a valid number.")

def process_transcript(url, target_lang, summary_type, selected_model):
    """Process the transcript through all steps."""
    # Initialize components
    downloader = TranscriptDownloader()
    detector = LanguageDetector()
    translator = Translator()
    llm_processor = LLMProcessor()
    file_utils = FileUtils()
    
    # Ensure output directory exists
    os.makedirs('output', exist_ok=True)
    
    print("\n" + "=" * 60)
    print("                    PROCESSING")
    print("=" * 60)
    
    # Step 1: Download transcript
    print("\n📥 STEP 1: Downloading transcript...")
    transcript = downloader.download_transcript(url)
    if not transcript:
        print("❌ Failed to download transcript.")
        print("   Possible reasons:")
        print("   • Video has no available transcript")
        print("   • Video is private or restricted")
        print("   • Invalid URL")
        return False
    
    print(f"✅ Transcript downloaded successfully ({len(transcript)} characters)")
    
    # Step 2: Detect language
    print("\n🔍 STEP 2: Detecting language...")
    detected_lang = detector.detect_language(transcript)
    if detected_lang == 'unknown':
        print("⚠️  Could not detect language, assuming English")
        detected_lang = 'en'
    else:
        lang_name = SUPPORTED_LANGUAGES.get(detected_lang, detected_lang)
        print(f"✅ Detected language: {lang_name} ({detected_lang})")
    
    # Step 3: Save original transcript
    print("\n💾 STEP 3: Saving original transcript...")
    file_utils.save_transcript(transcript, 'output/original_transcript.txt')
    
    # Step 4: Translate transcript if needed
    print(f"\n🌐 STEP 4: Translation to {SUPPORTED_LANGUAGES[target_lang]}...")
    if detected_lang != target_lang:
        print("   Translating transcript...")
        translated_transcript = translator.translate_text(transcript, target_lang)
        file_utils.save_transcript(translated_transcript, 'output/translated_transcript.txt')
        print("✅ Translation completed")
    else:
        print("✅ Target language matches detected language, no translation needed")
        translated_transcript = transcript
        file_utils.save_transcript(transcript, 'output/translated_transcript.txt')
    
    # Step 5: Generate summary
    print(f"\n🤖 STEP 5: Generating {summary_type} summary with {selected_model}...")
    summary = llm_processor.generate_summary(transcript, summary_type, selected_model)
    if not summary:
        print("❌ Failed to generate summary")
        return False
    
    file_utils.save_transcript(summary, 'output/original_summary.txt')
    print("✅ Summary generated successfully")
    
    # Step 6: Translate summary if needed
    print(f"\n🌐 STEP 6: Summary translation...")
    if detected_lang != target_lang:
        print(f"   Translating summary to {SUPPORTED_LANGUAGES[target_lang]}...")
        translated_summary = translator.translate_text(summary, target_lang)
        file_utils.save_transcript(translated_summary, 'output/translated_summary.txt')
        print("✅ Summary translation completed")
    else:
        print("✅ Summary already in target language")
        translated_summary = summary
        file_utils.save_transcript(summary, 'output/translated_summary.txt')
    
    # Display results
    print("\n" + "=" * 60)
    print("                     RESULTS")
    print("=" * 60)
    
    print(f"\n📄 ORIGINAL SUMMARY ({SUPPORTED_LANGUAGES.get(detected_lang, detected_lang).upper()}):")
    print("-" * 50)
    print(summary)
    
    if detected_lang != target_lang:
        print(f"\n📄 TRANSLATED SUMMARY ({SUPPORTED_LANGUAGES[target_lang].upper()}):")
        print("-" * 50)
        print(translated_summary)
    
    print("\n" + "=" * 60)
    print("                 FILES SAVED")
    print("=" * 60)
    print("📁 All files saved in 'output/' directory:")
    print("   • original_transcript.txt")
    print("   • translated_transcript.txt")
    print("   • original_summary.txt")
    print("   • translated_summary.txt")
    
    return True

def main():
    """Main application workflow."""
    try:
        # Print banner
        print_banner()
        
        # Initialize LLM processor early to check availability
        llm_processor = LLMProcessor()
        
        # Get user input
        url = get_youtube_url()
        target_lang = get_target_language()
        summary_type = get_summary_type()
        selected_model = get_llm_model(llm_processor)
        
        if not selected_model:
            print("\n❌ Cannot proceed without an available LLM model.")
            sys.exit(1)
        
        # Confirm settings
        print("\n" + "=" * 60)
        print("                CONFIGURATION")
        print("=" * 60)
        print(f"📹 Video URL: {url}")
        print(f"🌍 Target Language: {SUPPORTED_LANGUAGES[target_lang]}")
        print(f"📝 Summary Type: {summary_type}")
        print(f"🤖 LLM Model: {selected_model}")
        
        confirm = input("\nProceed with processing? (y/n): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("❌ Processing cancelled by user.")
            return
        
        # Process transcript
        success = process_transcript(url, target_lang, summary_type, selected_model)
        
        if success:
            print("\n🎉 Processing completed successfully!")
        else:
            print("\n❌ Processing failed. Please check the errors above.")
            sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user (Ctrl+C).")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        print("\nIf this error persists, please check:")
        print("• Internet connection")
        print("• Ollama service is running")
        print("• All dependencies are installed")
        sys.exit(1)

if __name__ == "__main__":
    main()