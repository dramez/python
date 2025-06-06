# YouTube Transcript Processor

A Python application that downloads YouTube video transcripts, detects language, translates content, and generates summaries using local LLM models via Ollama.

## Features

- Download YouTube video transcripts
- Automatic language detection
- Translation to multiple languages
- Local LLM integration via Ollama
- Multiple summary types (brief, detailed, bullet-point)
- File-based output management

## Prerequisites

1. **Python 3.8+**
2. **Ollama installed and running**
   - Install Ollama from: https://ollama.ai/
   - Pull at least one model (e.g., `ollama pull llama2`)

## Installation

1. Clone or download this project
2. Install dependencies:
   ```bash
   pip install -r requirements.txt

Usage

    Start Ollama service:

    bash

Copy Code
ollama serve

Run the application:

bash

    Copy Code
    python main.py

    Follow the interactive prompts:
        Enter YouTube video URL
        Select target language
        Choose LLM model
        Select summary type

Output Files

All output files are saved in the output/ directory:

    original_transcript.txt - Original transcript
    translated_transcript.txt - Translated transcript
    original_summary.txt - Summary in original language
    translated_summary.txt - Translated summary

Supported Languages

    English (en)
    Spanish (es)
    French (fr)
    German (de)
    Italian (it)
    Polish (pl)
    Portuguese (pt)
    Russian (ru)
    Japanese (ja)
    Korean (ko)
    Chinese (zh)

Troubleshooting

    Ensure Ollama is running before starting the application
    Check that you have at least one Ollama model installed
    Verify YouTube URL is valid and has available transcripts
    Check internet connection for translation services


## requirements.txt

youtube-transcript-api==0.6.1
langdetect==1.0.9
deep-translator==1.11.4
requests==2.31.0
ollama==0.1.7