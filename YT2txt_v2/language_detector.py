# language_detector.py

from langdetect import detect, LangDetectException

def detect_language(text: str) -> str:
    """
    Detects the language of the given text.

    Args:
        text (str): The text to analyze.

    Returns:
        str: The detected language code (e.g., 'en', 'es'), or None if detection fails.
    """
    try:
        # Ensure text is not too short for reliable detection
        if not text or len(text.strip()) < 20: # langdetect might struggle with very short text
            print("Warning: Text is too short for reliable language detection. Assuming English.")
            return 'en' # Default or handle as an error

        lang_code = detect(text)
        print(f"Detected language: {lang_code}")
        return lang_code
    except LangDetectException:
        print("Error: Could not detect language. The text might be too short or ambiguous.")
        print("Assuming English ('en') as a fallback.")
        return 'en' # Fallback language
    except Exception as e:
        print(f"An unexpected error occurred during language detection: {e}")
        return None
