# -*- coding: utf-8 -*-
"""
Handles all file I/O operations, such as saving transcripts and summaries.
"""
import os
import re

def get_video_id(url: str) -> str | None:
    """
    Extracts the YouTube video ID from a URL.
    Handles standard, short, and embed URLs.
    """
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:youtu\.be\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11}).*'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def create_output_directory(video_id: str) -> str:
    """
    Creates a directory for storing output files if it doesn't exist.
    A subdirectory is created for each video ID to keep files organized.
    
    Args:
        video_id (str): The unique ID of the YouTube video.

    Returns:
        str: The path to the created directory.
    """
    base_dir = "output"
    video_dir = os.path.join(base_dir, video_id)
    os.makedirs(video_dir, exist_ok=True)
    return video_dir

def save_to_file(content: str, filename: str, output_dir: str):
    """
    Saves content to a file in the specified output directory.

    Args:
        content (str): The text content to save.
        filename (str): The name of the file.
        output_dir (str): The directory to save the file in.
    """
    filepath = os.path.join(output_dir, filename)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[INFO] Successfully saved file: {filepath}")
    except IOError as e:
        print(f"[ERROR] Could not write to file {filepath}: {e}")