# -*- coding: utf-8 -*-
"""
Handles downloading transcripts from YouTube.
"""
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

def get_transcript(video_url: str) -> str:
    """
    Downloads the transcript for a given YouTube video URL.

    Args:
        video_url (str): The URL of the YouTube video.

    Returns:
        str: The full transcript as a single string.

    Raises:
        Exception: If the transcript cannot be fetched.
    """
    try:
        video_id = video_url.split("v=")[1].split("&")[0]
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Combine transcript parts into a single string
        full_transcript = " ".join([item['text'] for item in transcript_list])
        return full_transcript
        
    except (TranscriptsDisabled, NoTranscriptFound):
        raise Exception(f"Transcripts are disabled or not available for this video: {video_url}")
    except IndexError:
        raise Exception("Invalid YouTube URL. Could not extract video ID.")
    except Exception as e:
        raise Exception(f"An error occurred while fetching the transcript: {e}")