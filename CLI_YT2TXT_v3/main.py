# -*- coding: utf-8 -*-
"""
Main entry point for the YouTube Summarizer application.
This script orchestrates the entire workflow from user input to final output.
"""

import sys
from src import ui, youtube_utils, text_processor, llm_handler, file_manager

def main():
    """
    Main function to run the application workflow.
    """
    ui.display_welcome_message()

    try:
        # 1. Get User Inputs
        url = ui.get_youtube_url()
        video_id = file_manager.get_video_id(url)
        if not video_id:
            ui.display_error("Could not parse a valid YouTube video ID from the URL.")
            sys.exit(1)

        target_language_code, target_language_name = ui.get_target_language()

        available_models = llm_handler.get_available_models()
        selected_model = ui.get_ollama_model(available_models)

        summary_type = ui.get_summary_type()

        # Create a unique directory for the video's output files
        output_dir = file_manager.create_output_directory(video_id)
        ui.display_feedback(f"Output files will be saved in: {output_dir}")

        # 2. Download Transcript
        ui.display_feedback("Downloading transcript...")
        transcript_text = youtube_utils.get_transcript(url)

        # 3. Detect Language and Save Original Transcript
        original_lang = text_processor.detect_language(transcript_text)
        ui.display_feedback(f"Detected original language: {original_lang}")
        file_manager.save_to_file(
            transcript_text,
            f"original_transcript_{original_lang}.txt",
            output_dir
        )

        # 4. Translate Full Transcript and Save
        ui.display_feedback(f"Translating full transcript to {target_language_name}...")
        translated_transcript = text_processor.translate_text(
            transcript_text, target_language_code
        )
        file_manager.save_to_file(
            translated_transcript,
            f"translated_transcript_{target_language_code}.txt",
            output_dir
        )

        # 5. Summarize Original Transcript and Save
        ui.display_feedback(f"Summarizing with '{selected_model}'...")
        original_summary = llm_handler.summarize_text(
            transcript=transcript_text,
            model=selected_model,
            summary_type=summary_type
        )
        file_manager.save_to_file(
            original_summary,
            f"summary_{original_lang}.txt",
            output_dir
        )

        # 6. Translate Summary and Save
        ui.display_feedback(f"Translating summary to {target_language_name}...")
        translated_summary = text_processor.translate_text(
            original_summary, target_language_code
        )
        file_manager.save_to_file(
            translated_summary,
            f"summary_{target_language_code}.txt",
            output_dir
        )

        # 7. Display Results
        ui.display_results(original_summary, translated_summary)

    except Exception as e:
        ui.display_error(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()