# -*- coding: utf-8 -*-
"""
Handles all interactions with the Ollama API for model listing and summarization.
"""
import ollama
import sys

def get_available_models() -> list:
    """
    Fetches the list of locally available Ollama models.

    Returns:
        list: A list of model names.
    """
    try:
        models_info = ollama.list()
        return [model['name'] for model in models_info['models']]
    except Exception as e:
        print(f"[ERROR] Could not connect to Ollama. Please ensure Ollama is running. Details: {e}")
        sys.exit(1)

def summarize_text(transcript: str, model: str, summary_type: str) -> str:
    """
    Summarizes the transcript using a specified Ollama model.

    Args:
        transcript (str): The video transcript to summarize.
        model (str): The name of the Ollama model to use.
        summary_type (str): The desired type of summary.

    Returns:
        str: The generated summary.
    """
    prompt_instruction = f"""
    Based on the following transcript, provide a "{summary_type}".
    The summary should be concise, in the same language as the transcript, and accurately reflect the main points.
    Do not add any extra commentary or introductory phrases like "Here is the summary:".
    
    Transcript:
    ---
    {transcript}
    ---
    """
    
    try:
        response = ollama.chat(
            model=model,
            messages=[{'role': 'user', 'content': prompt_instruction}]
        )
        return response['message']['content'].strip()
    except Exception as e:
        raise Exception(f"Failed to get summary from Ollama model '{model}': {e}")