"""
Language Detector Module

Detects the language of text using langdetect library.
"""

from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

class LanguageDetector:
    """Detects language of text content."""
    
    def __init__(self):
        """Initialize language detector with consistent results."""
        # Set seed for consistent results
        DetectorFactory.seed = 0
    
    def detect_language(self, text):
        """
        Detect the language of given text.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            str: Language code (e.g., 'en', 'es', 'fr') or 'unknown'
        """
        try:
            if not text or len(text.strip()) < 10:
                return 'unknown'
            
            # Clean text for better detection
            cleaned_text = self._clean_text(text)
            
            # Detect language
            detected_lang = detect(cleaned_text)
            
            return detected_lang
            
        except LangDetectException as e:
            print(f"Language detection error: {str(e)}")
            return 'unknown'
        except Exception as e:
            print(f"Unexpected error in language detection: {str(e)}")
            return 'unknown'
    
    def _clean_text(self, text):
        """
        Clean text for better language detection.
        
        Args:
            text (str): Raw text
            
        Returns:
            str: Cleaned text
        """
        # Remove extra whitespace and normalize
        cleaned = ' '.join(text.split())
        
        # Take a sample if text is very long (for performance)
        if len(cleaned) > 1000:
            cleaned = cleaned[:1000]
        
        return cleaned