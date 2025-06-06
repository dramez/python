# -*- coding: utf-8 -*-
"""
Handles language detection and translation tasks.
"""
from langdetect import detect, LangDetectException
from deep_translator import GoogleTranslator

def detect_language(text: str) -> str:
    """
    Detects the language of a given text.

    Args:
        text (str): The text to analyze.

    Returns:
        str: The detected language code (e.g., 'en').
    """
    try:
        return detect(text)
    except LangDetectException:
        return "unknown" # Return a default if detection fails

def translate_text(text: str, target_lang: str) -> str:
    """
    Translates text to a specified target language.

    Args:
        text (str): The text to translate.
        target_lang (str): The target language code (e.g., 'es').

    Returns:
        str: The translated text.
    """
    try:
        return GoogleTranslator(source='auto', target=target_lang).translate(text)
    except Exception as e:
        raise Exception(f"Failed to translate text: {e}")