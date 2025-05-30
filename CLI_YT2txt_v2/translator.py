# translator.py

from deep_translator import GoogleTranslator

def translate_text(text: str, target_language: str, source_language: str = 'auto') -> str | None:
    """
    Translates text to the target language.

    Args:
        text (str): The text to translate.
        target_language (str): The target language code (e.g., 'en', 'es').
        source_language (str): The source language code. Defaults to 'auto'.

    Returns:
        str: The translated text, or None if translation fails.
    """
    if not text:
        print("Warning: No text provided for translation.")
        return "" # Return empty string for empty input, consistent with no error
    try:
        print(f"Translating text from '{source_language}' to '{target_language}'...")
        # The actual translation call
        translated_text = GoogleTranslator(source=source_language, target=target_language).translate(text)

        if translated_text is None: # Some translators might return None on failure
             print("Error: Translation API returned None. This might indicate an issue with the input or service.")
             return None
        print("Translation successful.")
        return translated_text
    except Exception as e:
        # Avoid printing the full exception 'e' directly as it might contain the input text.
        # Instead, print a generic message and the type of error.
        # For more detailed debugging, one might log 'e' to a file.
        error_type = type(e).__name__
        print(f"Error during translation: An error of type '{error_type}' occurred.")
        print("This could be due to various reasons such as network issues, API limits, or unsupported content/language pair.")
        # If you need to see the original error for debugging, you could uncomment the next line
        # but be aware it might print parts of the transcript.
        # print(f"Original error details (may contain input text): {e}")
        return None