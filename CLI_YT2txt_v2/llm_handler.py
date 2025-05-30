# llm_handler.py

import requests
import json

OLLAMA_API_URL = "http://localhost:11434/api/generate"

def get_ollama_models():
    """
    Attempts to list available Ollama models.
    Note: This function tries to connect to the Ollama API.
    The user should ideally provide the model name they've confirmed is available.
    """
    try:
        response = requests.get("http://localhost:11434/api/tags")
        response.raise_for_status()
        models = response.json().get("models", [])
        return [model['name'] for model in models]
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to Ollama server at http://localhost:11434.")
        print("Please ensure Ollama is running.")
        return []
    except Exception as e:
        print(f"Error fetching Ollama models: {e}")
        return []

def generate_summary_prompt(text: str, summary_type: str, original_language_code: str) -> str:
    """
    Generates a prompt for the LLM based on the summary type.
    """
    # You might want to refine these prompts for better results
    # or even translate the instruction part of the prompt if the model is not multilingual
    # or if you want the instruction in the same language as the text.
    # For simplicity, instructions are in English.

    # Hint to the model about the language of the text, if known
    lang_hint = f"The following text is in {original_language_code}." if original_language_code else "The following text is in an unknown language."

    if summary_type == "brief":
        return (
            f"{lang_hint} "
            "Provide a concise, brief summary (2-3 sentences) of the following text. "
            "Focus on the main topic and key conclusions. "
            "The summary should be in the same language as the original text provided below.\n\n"
            f"Text:\n\"\"\"\n{text}\n\"\"\""
        )
    elif summary_type == "detailed":
        return (
            f"{lang_hint} "
            "Provide a detailed summary of the following text, highlighting the key points and main arguments. "
            "The summary should be comprehensive yet easy to understand. "
            "The summary should be in the same language as the original text provided below.\n\n"
            f"Text:\n\"\"\"\n{text}\n\"\"\""
        )
    elif summary_type == "bullet":
        return (
            f"{lang_hint} "
            "Provide a summary of the following text in bullet-point format. "
            "Each bullet point should capture a key piece of information or a main idea. "
            "The summary should be in the same language as the original text provided below.\n\n"
            f"Text:\n\"\"\"\n{text}\n\"\"\""
        )
    else:
        # Default to a generic summary if type is unknown
        return (
            f"{lang_hint} "
            "Summarize the following text. "
            "The summary should be in the same language as the original text provided below.\n\n"
            f"Text:\n\"\"\"\n{text}\n\"\"\""
        )

def summarize_text_with_ollama(text: str, model_name: str, summary_type: str, original_language_code: str) -> str:
    """
    Summarizes text using a specified Ollama model.

    Args:
        text (str): The text to summarize.
        model_name (str): The name of the Ollama model to use (e.g., 'llama3:latest').
        summary_type (str): 'brief', 'detailed', or 'bullet'.
        original_language_code (str): The language code of the original text (e.g., 'en', 'es').

    Returns:
        str: The generated summary, or None if an error occurs.
    """
    if not text:
        print("Warning: No text provided for summarization.")
        return ""

    prompt = generate_summary_prompt(text, summary_type, original_language_code)

    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False  # Get the full response at once
    }

    print(f"Summarizing text using Ollama model: {model_name} with type: {summary_type}...")
    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors

        response_data = response.json()
        summary = response_data.get("response", "").strip()

        if not summary:
            print("Error: Ollama returned an empty summary.")
            print("Full Ollama response:", response_data) # For debugging
            return None

        print("Summarization successful.")
        return summary
    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to Ollama server at {OLLAMA_API_URL}.")
        print("Please ensure Ollama is running and the model is available.")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"Error: HTTP error from Ollama: {e.response.status_code} - {e.response.text}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while communicating with Ollama: {e}")
        return None
