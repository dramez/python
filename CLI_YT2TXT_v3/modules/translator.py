"""
Translator Module

Handles text translation using deep-translator library.
"""

from deep_translator import GoogleTranslator
import time

class Translator:
    """Translates text between languages."""
    
    def __init__(self):
        """Initialize translator."""
        pass
    
    def translate_text(self, text, target_language, chunk_size=4500):
        """
        Translate text to target language.
        
        Args:
            text (str): Text to translate
            target_language (str): Target language code
            chunk_size (int): Size of text chunks for translation
            
        Returns:
            str: Translated text or original text if translation fails
        """
        try:
            if not text or not text.strip():
                return text
            
            # Split text into chunks to handle length limits
            chunks = self._split_text(text, chunk_size)
            translated_chunks = []
            
            translator = GoogleTranslator(target=target_language)
            
            for i, chunk in enumerate(chunks):
                try:
                    # Add small delay between requests to avoid rate limiting
                    if i > 0:
                        time.sleep(0.5)
                    
                    translated_chunk = translator.translate(chunk)
                    translated_chunks.append(translated_chunk)
                    
                except Exception as e:
                    print(f"Warning: Failed to translate chunk {i+1}: {str(e)}")
                    translated_chunks.append(chunk)  # Use original if translation fails
            
            return ' '.join(translated_chunks)
            
        except Exception as e:
            print(f"Translation error: {str(e)}")
            return text  # Return original text if translation fails
    
    def _split_text(self, text, chunk_size):
        """
        Split text into chunks for translation.
        
        Args:
            text (str): Text to split
            chunk_size (int): Maximum size per chunk
            
        Returns:
            list: List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        sentences = text.split('. ')
        current_chunk = ""
        
        for sentence in sentences:
            # If adding this sentence would exceed chunk size
            if len(current_chunk) + len(sentence) + 2 > chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = sentence + '. '
                else:
                    # Single sentence is too long, split it
                    chunks.append(sentence[:chunk_size])
                    current_chunk = sentence[chunk_size:] + '. '
            else:
                current_chunk += sentence + '. '
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks