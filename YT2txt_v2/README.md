# YouTube Video Transcript Summarizer & Translator

This Python application downloads a YouTube video transcript, automatically detects its language, translates it, and generates summaries using a local Ollama LLM.

## Features

-   Download YouTube video transcripts.
-   Automatic language detection of the transcript.
-   Translation of the transcript to a chosen target language.
-   Summarization of the transcript using a user-selected local Ollama LLM.
-   Choice of summary types: brief, detailed, or bullet-point.
-   Translation of the summary to the target language.
-   Saves original transcript, translated transcript, original summary, and translated summary to local files.
-   Displays original and translated summaries on screen.

## Setup

### Prerequisites

-   Python 3.7+
-   Pip (Python package installer)
-   Ollama installed and running with desired models downloaded.
    -   You can download Ollama from [https://ollama.ai/](https://ollama.ai/).
    -   Pull models using `ollama pull <model_name>` (e.g., `ollama pull llama3`).
    -   Ensure the Ollama server is running (usually at `http://localhost:11434`).

### Installation

1.  **Clone the repository or create the project directory:**
    If you have the files, place them in a directory named `youtube_summarizer`.

2.  **Navigate to the project directory:**
    ```bash
    cd youtube_summarizer
    ```

3.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Ensure Ollama is running** and you have at least one model downloaded (e.g., `llama3`, `mistral`). You can list your downloaded models by running `ollama list` in your terminal.

2.  **Run the main script:**
    ```bash
    python main.py
    ```

3.  **Follow the prompts:**
    -   Enter the YouTube video URL.
    -   Select a target language for translation.
    -   Enter the name of the Ollama model you wish to use (e.g., `llama3:latest`).
    -   Select the type of summary you want.

4.  **Output:**
    -   The application will display the original and translated summaries on the screen.
    -   The following files will be created in the project directory:
        -   `original_transcript.txt`
        -   `translated_transcript.txt`
        -   `original_summary.txt`
        -   `translated_summary.txt`

## Modules

-   `main.py`: Entry point of the application.
-   `youtube_downloader.py`: Handles downloading YouTube transcripts.
-   `language_detector.py`: Detects the language of the transcript.
-   `translator.py`: Translates text to the target language.
-   `llm_handler.py`: Interacts with the Ollama API for summarization.
-   `file_utils.py`: Utility functions for file operations.

## Troubleshooting

-   **Ollama Connection Issues**: Ensure the Ollama application is running and accessible at `http://localhost:11434`. Check your firewall settings if necessary.
-   **Model Not Found**: Make sure the Ollama model name you provide is correct and the model has been downloaded using `ollama pull <model_name>`.
-   **youtube-transcript-api errors**: Ensure the video URL is correct and the video has transcripts available. Some videos might have transcripts disabled or not available in a processable format.
-   **Translation/Language Detection errors**: These can occur due to network issues or API limitations of the underlying libraries.
