# YouTube Transcript Summarizer & Translator

This command-line application allows you to download the transcript of any YouTube video, summarize it using a locally running Ollama LLM, and translate both the transcript and the summary into a language of your choice.

## Features

-   Downloads video transcripts directly from YouTube.
-   Automatically detects the original language of the transcript.
-   Lets you choose a target language for translation from a predefined list.
-   Integrates with your local Ollama instance, allowing you to select any of your available models for summarization.
-   Offers multiple summary formats: brief, detailed, or bullet points.
-   Saves all artifacts (original transcript, translated transcript, original summary, translated summary) to a local `output` directory.
-   Displays the original and translated summaries directly in your terminal.

## Prerequisites

-   Python 3.8 or higher.
-   [Ollama](https://ollama.com/) installed and running on your local machine.
-   At least one model pulled in Ollama (e.g., `ollama pull llama3`).

## Setup

1.  **Clone the repository or download the source code:**
    ```bash
    git clone <repository_url>
    cd youtube-summarizer
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## How to Run

1.  **Ensure Ollama is running:**
    Open a separate terminal and simply run the command `ollama serve` or ensure the desktop application is running.

2.  **Run the main script:**
    ```bash
    python main.py
    ```

3.  **Follow the on-screen prompts:**
    -   Enter the YouTube video URL.
    -   Choose a target language.
    -   Select an available Ollama model.
    -   Pick a summary type.

The application will then process the video and display the summaries. The output files will be saved in the `output/` directory.