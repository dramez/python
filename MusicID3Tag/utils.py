"""
Utility Functions Module
Contains helper functions for the application.
"""

import csv
import os
from typing import List, Tuple
from tkinter import filedialog, messagebox


class FileUtils:
    """File utility functions."""

    @staticmethod
    def export_to_csv(data: List[Tuple], filename: str = None) -> bool:
        """Export data to CSV file."""
        if not filename:
            filename = filedialog.asksaveasfilename(
                title="Export to CSV",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )

        if not filename:
            return False

        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)

                # Write header
                header = ['ID', 'Title', 'Artist', 'Album', 'Genre', 'Year', 'Track Number', 'Comment', 'File Path']
                writer.writerow(header)

                # Write data
                for row in data:
                    writer.writerow(row)

            return True
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {e}")
            return False

    @staticmethod
    def get_safe_filename(filename: str) -> str:
        """Get a safe filename by removing invalid characters."""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename

    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size in human readable format."""
        if size_bytes == 0:
            return "0 B"

        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1

        return f"{size_bytes:.1f} {size_names[i]}"


class ValidationUtils:
    """Validation utility functions."""

    @staticmethod
    def is_valid_year(year_str: str) -> bool:
        """Check if year string is valid."""
        if not year_str:
            return True  # Empty is valid

        try:
            year = int(year_str)
            return 1900 <= year <= 2100
        except ValueError:
            return False

    @staticmethod
    def is_valid_track_number(track_str: str) -> bool:
        """Check if track number string is valid."""
        if not track_str:
            return True  # Empty is valid

        try:
            # Handle "track/total" format
            if '/' in track_str:
                track_str = track_str.split('/')[0]

            track = int(track_str)
            return 1 <= track <= 999
        except ValueError:
            return False

    @staticmethod
    def sanitize_metadata(metadata: dict) -> dict:
        """Sanitize metadata values."""
        sanitized = {}

        for key, value in metadata.items():
            if isinstance(value, str):
                # Remove null characters and excessive whitespace
                value = value.replace('\x00', '').strip()
                # Limit length
                if len(value) > 500:
                    value = value[:500]

            sanitized[key] = value

        return sanitized