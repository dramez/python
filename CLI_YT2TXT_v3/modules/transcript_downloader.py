"""
Transcript Downloader Module

Handles downloading transcripts from YouTube videos using youtube-transcript-api.
"""

from youtube_transcript_api import YouTubeTranscriptApi
import re

class TranscriptDownloader:
    """Downloads transcripts from YouTube videos."""
    
    def __init__(self):
        """Initialize the transcript downloader."""
        pass
    
    def extract_video_id(self, url):
        """
        Extract video ID from YouTube URL.
        
        Args:
            url (str): YouTube video URL
            
        Returns:
            str: Video ID or None if not found
        """
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&\n?#]+)',
            r'youtube\.com/watch\?.*v=([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def download_transcript(self, url):
        """
        Download transcript from YouTube video.
        
        Args:
            url (str): YouTube video URL
            
        Returns:
            str: Full transcript text or None if failed
        """
        try:
            # Extract video ID
            video_id = self.extract_video_id(url)
            if not video_id:
                raise ValueError("Invalid YouTube URL")
            
            # Get transcript
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            
            # Combine all transcript segments
            full_transcript = ' '.join([entry['text'] for entry in transcript_list])
            
            return full_transcript.strip()
            
        except Exception as e:
            print(f"Error downloading transcript: {str(e)}")
            return None