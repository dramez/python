#!/usr/bin/env python3
"""
YouTube Transcript Processor - Main Entry Point

This application downloads YouTube transcripts, detects language,
translates content, and generates summaries using local LLM models.
"""

import os
import sys
import re
from datetime import datetime
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

def sanitize_filename(text):
    """
    Sanitize text for use in filename.
    
    Args:
        text (str): Text to sanitize
        
    Returns:
        str: Sanitized text safe for filename
    """
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*%\[\]]', '_', text)
    # Remove multiple underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')
    # Limit length
    if len(sanitized) > 50:
        sanitized = sanitized[:50]
    return sanitized

def extract_video_id_from_url(url):
    """
    Extract video ID from YouTube URL for filename.
    
    Args:
        url (str): YouTube URL
        
    Returns:
        str: Video ID or sanitized URL portion
    """
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&\n?#]+)',
        r'youtube\.com/watch\?.*v=([^&\n?#]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    # If no video ID found, use sanitized URL
    return sanitize_filename(url)

def generate_filename_base(url, model_name):
    """
    Generate base filename with timestamp, URL, and model.
    
    Args:
        url (str): YouTube URL
        model_name (str): Ollama model name
        
    Returns:
        str: Base filename without extension
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    video_id = extract_video_id_from_url(url)
    sanitized_model = sanitize_filename(model_name)
    
    return f"{timestamp}_{video_id}_{sanitized_model}"

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
    
    # Generate filename base
    filename_base = generate_filename_base(url, selected_model)
    
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
        return False, None
    
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
    
    # Generate filenames with dynamic naming
    original_transcript_file = f'output/{filename_base}_original_transcript.txt'
    translated_transcript_file = f'output/{filename_base}_translated_transcript.txt'
    original_summary_file = f'output/{filename_base}_original_summary.txt'
    translated_summary_file = f'output/{filename_base}_translated_summary.txt'
    
    # Step 3: Save original transcript
    print("\n💾 STEP 3: Saving original transcript...")
    file_utils.save_transcript(transcript, original_transcript_file)
    
    # Step 4: Translate transcript if needed
    print(f"\n🌐 STEP 4: Translation to {SUPPORTED_LANGUAGES[target_lang]}...")
    if detected_lang != target_lang:
        print("   Translating transcript...")
        translated_transcript = translator.translate_text(transcript, target_lang)
        file_utils.save_transcript(translated_transcript, translated_transcript_file)
        print("✅ Translation completed")
    else:
        print("✅ Target language matches detected language, no translation needed")
        translated_transcript = transcript
        file_utils.save_transcript(transcript, translated_transcript_file)
    
    # Step 5: Generate summary
    print(f"\n🤖 STEP 5: Generating {summary_type} summary with {selected_model}...")
    summary = llm_processor.generate_summary(transcript, summary_type, selected_model)
    if not summary:
        print("❌ Failed to generate summary")
        return False, None
    
    file_utils.save_transcript(summary, original_summary_file)
    print("✅ Summary generated successfully")
    
    # Step 6: Translate summary if needed
    print(f"\n🌐 STEP 6: Summary translation...")
    if detected_lang != target_lang:
        print(f"   Translating summary to {SUPPORTED_LANGUAGES[target_lang]}...")
        translated_summary = translator.translate_text(summary, target_lang)
        file_utils.save_transcript(translated_summary, translated_summary_file)
        print("✅ Summary translation completed")
    else:
        print("✅ Summary already in target language")
        translated_summary = summary
        file_utils.save_transcript(summary, translated_summary_file)
    
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
    
    # Return file information
    files_created = {
        'original_transcript': original_transcript_file,
        'translated_transcript': translated_transcript_file,
        'original_summary': original_summary_file,
        'translated_summary': translated_summary_file
    }
    
    return True, files_created

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
        
        # Show filename preview
        filename_base = generate_filename_base(url, selected_model)
        print(f"📁 Files will be named: {filename_base}_[type].txt")
        
        confirm = input("\nProceed with processing? (y/n): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("❌ Processing cancelled by user.")
            return
        
        # Process transcript
        success, files_created = process_transcript(url, target_lang, summary_type, selected_model)
        
        if success and files_created:
            print("\n" + "=" * 60)
            print("                 FILES SAVED")
            print("=" * 60)
            print("📁 Files created:")
            for file_type, filepath in files_created.items():
                filename = os.path.basename(filepath)
                print(f"   • {filename}")
            
            print(f"\n📂 All files saved in 'output/' directory")
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