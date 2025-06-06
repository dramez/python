"""
LLM Processor Module

Handles interaction with local LLM models via Ollama for summarization.
"""

import ollama
import requests

class LLMProcessor:
    """Processes text using local LLM models via Ollama."""
    
    def __init__(self):
        """Initialize LLM processor."""
        self.client = ollama.Client()
    
    def get_available_models(self):
        """
        Get list of available Ollama models.
        
        Returns:
            list: List of available model names
        """
        try:
            models = self.client.list()
            return [model['name'] for model in models['models']]
        except Exception as e:
            print(f"Error getting models: {str(e)}")
            return []
    
    def generate_summary(self, text, summary_type, model_name):
        """
        Generate summary using specified LLM model.
        
        Args:
            text (str): Text to summarize
            summary_type (str): Type of summary ('brief', 'detailed', 'bullet')
            model_name (str): Name of the Ollama model to use
            
        Returns:
            str: Generated summary or None if failed
        """
        try:
            # Create prompt based on summary type
            prompt = self._create_prompt(text, summary_type)
            
            # Generate summary using Ollama
            response = self.client.chat(
                model=model_name,
                messages=[
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ]
            )
            
            summary = response['message']['content'].strip()
            return summary
            
        except Exception as e:
            print(f"Error generating summary: {str(e)}")
            return None
    
    def _create_prompt(self, text, summary_type):
        """
        Create appropriate prompt based on summary type.
        
        Args:
            text (str): Text to summarize
            summary_type (str): Type of summary
            
        Returns:
            str: Formatted prompt
        """
        base_prompt = f"Please summarize the following text:\n\n{text}\n\n"
        
        if summary_type == 'brief':
            return base_prompt + "Provide a brief summary in 2-3 sentences that captures the main points."
        
        elif summary_type == 'detailed':
            return base_prompt + "Provide a detailed summary with key points, important details, and main conclusions."
        
        elif summary_type == 'bullet':
            return base_prompt + "Provide a bullet-point summary with the main points listed clearly."
        
        else:
            return base_prompt + "Provide a concise summary of the main points."