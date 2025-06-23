"""
File Utilities Module

Handles file I/O operations for saving transcripts and summaries.
"""

import os
from datetime import datetime

class FileUtils:
    """Utility class for file operations."""
    
    def __init__(self):
        """Initialize file utilities."""
        pass
    
    def save_transcript(self, content, filepath):
        """
        Save content to a file with timestamp header.
        
        Args:
            content (str): Content to save
            filepath (str): Full path where to save the file
        """
        try:
            # Ensure directory exists
            directory = os.path.dirname(filepath)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            # Add timestamp header
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            header = f"Generated on: {timestamp}\n{'='*50}\n\n"
            
            # Write content to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(header + content)
            
            filename = os.path.basename(filepath)
            print(f"   Saved: {filename}")
            
        except Exception as e:
            print(f"Error saving file {filepath}: {str(e)}")
    
    def read_file(self, filepath):
        """
        Read content from a file.
        
        Args:
            filepath (str): Path to the file to read
            
        Returns:
            str: File content or None if failed
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file {filepath}: {str(e)}")
            return None
    
    def file_exists(self, filepath):
        """
        Check if file exists.
        
        Args:
            filepath (str): Path to check
            
        Returns:
            bool: True if file exists, False otherwise
        """
        return os.path.exists(filepath)