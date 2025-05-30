# main.py

import youtube_downloader
import language_detector
import translator
import llm_handler
import file_utils
import datetime

# Supported languages for translation
SUPPORTED_LANGUAGES = {
    'en': 'English', 'es': 'Spanish', 'fr': 'French', 'de': 'German',
    'it': 'Italian', 'pl': 'Polish', 'pt': 'Portuguese', 'ru': 'Russian',
    'ja': 'Japanese', 'ko': 'Korean', 'zh': 'Chinese (Simplified)'
}

# Summary types
SUMMARY_TYPES = {
    "1": "brief",
    "2": "detailed",
    "3": "bullet"
}

def get_user_inputs():
    """Gets all necessary inputs from the user."""
    print("\nWelcome to the YouTube Video Summarizer and Translator!")
    print("======================================================")

    video_url = input("Enter the YouTube video URL: ").strip()
    while not video_url:
        video_url = input("URL cannot be empty. Please enter the YouTube video URL: ").strip()

    print("\nAvailable target languages for translation:")
    for code, name in SUPPORTED_LANGUAGES.items():
        print(f"  {code}: {name}")
    target_lang_code = ""
    while target_lang_code not in SUPPORTED_LANGUAGES:
        target_lang_code = input(f"Select a target language code (e.g., 'es' for Spanish): ").strip().lower()
        if target_lang_code not in SUPPORTED_LANGUAGES:
            print("Invalid language code. Please choose from the list.")

    print("\nAttempting to fetch available Ollama models...")
    available_models = llm_handler.get_ollama_models()
    ollama_model_name_input = "" # Renamed to avoid conflict with variable name in process_video
    if available_models:
        print("Available Ollama models found on your system:")
        for i, model_name_option in enumerate(available_models):
            print(f"  {i + 1}: {model_name_option}")
        print(f"  0: Enter model name manually")
        while True:
            try:
                choice = input(f"Select the number of the Ollama model to use (or 0 to enter manually): ").strip()
                choice_num = int(choice)
                if choice_num == 0:
                    ollama_model_name_input = input("Enter the Ollama model name (e.g., 'llama3:latest'): ").strip()
                    while not ollama_model_name_input:
                        ollama_model_name_input = input("Ollama model name cannot be empty. Please enter a model name: ").strip()
                    break
                elif 1 <= choice_num <= len(available_models):
                    ollama_model_name_input = available_models[choice_num - 1]
                    print(f"Selected model: {ollama_model_name_input}")
                    break
                else:
                    print(f"Invalid selection. Please enter a number between 0 and {len(available_models)}.")
            except ValueError:
                print("Invalid input. Please enter a number.")
    else:
        print("Could not automatically fetch Ollama models. Please ensure Ollama is running.")
        ollama_model_name_input = input("Enter the Ollama model name to use for summarization (e.g., 'llama3:latest'): ").strip()
        while not ollama_model_name_input:
            ollama_model_name_input = input("Ollama model name cannot be empty. Please enter a model name: ").strip()

    print("\nSelect the type of summary:")
    for key, desc_key in SUMMARY_TYPES.items():
        desc_text = ""
        if desc_key == "brief": desc_text = "Brief summary (2-3 sentences)"
        elif desc_key == "detailed": desc_text = "Detailed summary with key points"
        elif desc_key == "bullet": desc_text = "Bullet-point summary"
        print(f"  {key}: {desc_text}")
    summary_choice_key = ""
    while summary_choice_key not in SUMMARY_TYPES:
        summary_choice_key = input("Choose a summary type (enter the number): ").strip()
        if summary_choice_key not in SUMMARY_TYPES:
            print("Invalid choice. Please enter a valid number for the summary type.")
    summary_type = SUMMARY_TYPES[summary_choice_key]

    return video_url, target_lang_code, ollama_model_name_input, summary_type # Return ollama_model_name_input

def process_video():
    """Handles the processing for a single video."""
    # Unpack ollama_model_name from get_user_inputs
    video_url, target_lang_code, ollama_model, summary_type = get_user_inputs()

    current_time = datetime.datetime.now()
    timestamp = current_time.strftime("%Y%m%d_%H%M%S")

    # Sanitize the chosen ollama_model name for use in filenames (done in file_utils now)
    # but we need the original name for the llm_handler and the sanitized one for constructing example filenames
    sanitized_ollama_model_for_print = file_utils.sanitize_model_name(ollama_model)


    print("\n--- Starting Process ---")

    # Step 1: Download Transcript
    print("\nStep 1: Downloading Transcript...")
    original_transcript, video_id = youtube_downloader.get_youtube_transcript(video_url)

    if not original_transcript:
        print(f"Exiting current video processing due to transcript download failure for video ID: {video_id if video_id else 'unknown'}.")
        return

    if not video_id:
        video_id = "unknownID"
        print(f"Warning: Video ID could not be determined. Using '{video_id}' for filenames.")

    # Step 2: Detect Language
    print("\nStep 2: Detecting Transcript Language...")
    original_lang_code = language_detector.detect_language(original_transcript)
    if not original_lang_code:
        print("Could not detect transcript language. Assuming 'en' (English) for proceeding.")
        original_lang_code = 'en'
    else:
        print(f"Detected original language: {original_lang_code} ({SUPPORTED_LANGUAGES.get(original_lang_code, 'Unknown')})")

    # Step 3: Save Original Transcript
    print("\nStep 3: Saving Original Transcript...")
    file_utils.save_to_file(original_transcript, "original_transcript", video_id, timestamp, ollama_model)

    # Step 4: Translate Full Original Transcript
    print(f"\nStep 4: Translating Full Original Transcript from '{original_lang_code}' to '{target_lang_code}'...")
    translated_full_transcript = translator.translate_text(
        original_transcript, target_lang_code, source_language=original_lang_code
    )

    # Step 5: Save Translated Full Original Transcript
    if translated_full_transcript is not None:
        print("\nStep 5: Saving Translated Full Original Transcript...")
        file_utils.save_to_file(translated_full_transcript, "translated_full_transcript", video_id, timestamp, ollama_model)
    else:
        print("Full original transcript translation failed. The translated full transcript file will not be saved.")

    # Step 6: Summarize Original Transcript
    print("\nStep 6: Summarizing Original Transcript (in its original language)...")
    # Use the original ollama_model name for the API call
    original_summary = llm_handler.summarize_text_with_ollama(
        original_transcript, ollama_model, summary_type, original_lang_code
    )
    translated_summary = None

    if not original_summary:
        print("Original summarization failed. Cannot proceed with summary display or translation.")
    else:
        print("\n--- Original Summary (in original language) ---")
        print(original_summary)
        print("-----------------------------------------------")
        # Step 7: Save Original Summary
        print("\nStep 7: Saving Original Summary...")
        file_utils.save_to_file(original_summary, "original_summary", video_id, timestamp, ollama_model)

        # Step 8: Translate Summary
        print(f"\nStep 8: Translating Summary from '{original_lang_code}' to '{target_lang_code}'...")
        translated_summary = translator.translate_text(
            original_summary, target_lang_code, source_language=original_lang_code
        )

        if translated_summary is not None:
            print("\n--- Translated Summary ---")
            print(translated_summary)
            print("--------------------------")
            # Step 9: Save Translated Summary
            print("\nStep 9: Saving Translated Summary...")
            file_utils.save_to_file(translated_summary, "translated_summary", video_id, timestamp, ollama_model)
        else:
            print("Summary translation failed. Translated summary will not be displayed or saved.")

    print("\n--- Process Complete for this video ---")
    print(f"Output files are saved in the '{file_utils.OUTPUT_DIR}' directory.")
    print("Files generated for this video (if process completed for them):")

    base_filename_prefix = f"{video_id if video_id else 'unknownID'}_{timestamp}_{sanitized_ollama_model_for_print}"

    if video_id and original_transcript:
        print(f"- {base_filename_prefix}_original_transcript.txt")
        if translated_full_transcript is not None:
            print(f"- {base_filename_prefix}_translated_full_transcript.txt")
        else:
            print(f"- (File {base_filename_prefix}_translated_full_transcript.txt was NOT generated)")

        if original_summary is not None:
            print(f"- {base_filename_prefix}_original_summary.txt")
            if translated_summary is not None:
                print(f"- {base_filename_prefix}_translated_summary.txt")
            else:
                print(f"- (File {base_filename_prefix}_translated_summary.txt was NOT generated)")
        else:
            print(f"- (Files starting with {base_filename_prefix}_original_summary... were NOT generated)")
    else:
        print("- No files generated as transcript download failed at the start.")


def main():
    """Main function to run the application and loop for multiple URLs."""
    while True:
        process_video()

        while True:
            another = input("\nDo you want to process another YouTube URL? (y/n): ").strip().lower()
            if another in ['y', 'yes']:
                break
            elif another in ['n', 'no']:
                print("Exiting program. Goodbye!")
                return
            else:
                print("Invalid input. Please enter 'y' or 'n'.")

if __name__ == "__main__":
    main()