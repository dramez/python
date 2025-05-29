"""
Metadata Reader Module
Handles reading audio metadata using mutagen library.
"""

import os
from typing import Dict, Optional
from mutagen import File
from mutagen.id3 import ID3NoHeaderError


class MetadataReader:
    """Handles reading metadata from audio files."""

    SUPPORTED_FORMATS = {'.mp3', '.ogg', '.flac', '.m4a', '.aac', '.wav'}

    @classmethod
    def is_supported_format(cls, file_path: str) -> bool:
        """Check if file format is supported."""
        return os.path.splitext(file_path.lower())[1] in cls.SUPPORTED_FORMATS

    @classmethod
    def read_metadata(cls, file_path: str) -> Dict[str, str]:
        """Read metadata from audio file."""
        metadata = {
            'title': '',
            'artist': '',
            'album': '',
            'genre': '',
            'year': '',
            'track_number': '',
            'comment': '',
            'file_path': file_path
        }

        if not os.path.exists(file_path):
            return metadata

        try:
            audio_file = File(file_path)
            if audio_file is None:
                return metadata

            # Handle different tag formats
            if hasattr(audio_file, 'tags') and audio_file.tags:
                tags = audio_file.tags

                # Define tag mappings for different formats
                tag_mappings = {
                    'title': ['TIT2', 'TITLE', '\xa9nam'],
                    'artist': ['TPE1', 'ARTIST', '\xa9ART'],
                    'album': ['TALB', 'ALBUM', '\xa9alb'],
                    'genre': ['TCON', 'GENRE', '\xa9gen'],
                    'year': ['TDRC', 'TYER', 'DATE', '\xa9day'],
                    'track_number': ['TRCK', 'TRACKNUMBER', 'trkn'],
                    'comment': ['COMM::eng', 'COMMENT', '\xa9cmt']
                }

                # Try to extract metadata using known tag names
                for field, tag_names in tag_mappings.items():
                    for tag_name in tag_names:
                        if tag_name in tags:
                            try:
                                value = tags[tag_name]
                                if isinstance(value, list) and len(value) > 0:
                                    value = value[0]
                                
                                # Handle special cases
                                if field == 'track_number':
                                    value_str = str(value)
                                    if '/' in value_str:
                                        value_str = value_str.split('/')[0]
                                    metadata[field] = value_str
                                elif field == 'year':
                                    # Extract year from date strings
                                    value_str = str(value)
                                    if len(value_str) >= 4 and value_str[:4].isdigit():
                                        metadata[field] = value_str[:4]
                                    else:
                                        metadata[field] = value_str
                                else:
                                    metadata[field] = str(value)
                                break  # Found a value, stop looking for this field
                            except (IndexError, TypeError, ValueError):
                                continue

                # Fallback: try generic tag names for any remaining empty fields
                for key, value in tags.items():
                    try:
                        if isinstance(value, list) and len(value) > 0:
                            value = value[0]
                        
                        key_lower = str(key).lower()
                        value_str = str(value)

                        # Only fill empty fields
                        if 'title' in key_lower and not metadata['title']:
                            metadata['title'] = value_str
                        elif 'artist' in key_lower and not metadata['artist']:
                            metadata['artist'] = value_str
                        elif 'album' in key_lower and not metadata['album']:
                            metadata['album'] = value_str
                        elif 'genre' in key_lower and not metadata['genre']:
                            metadata['genre'] = value_str
                        elif any(x in key_lower for x in ['date', 'year']) and not metadata['year']:
                            if len(value_str) >= 4 and value_str[:4].isdigit():
                                metadata['year'] = value_str[:4]
                            else:
                                metadata['year'] = value_str
                        elif 'track' in key_lower and not metadata['track_number']:
                            if '/' in value_str:
                                value_str = value_str.split('/')[0]
                            metadata['track_number'] = value_str
                        elif 'comment' in key_lower and not metadata['comment']:
                            metadata['comment'] = value_str
                    except (TypeError, ValueError, AttributeError):
                        continue

        except (ID3NoHeaderError, Exception) as e:
            print(f"Error reading metadata from {file_path}: {e}")

        return metadata

    @classmethod
    def get_audio_files(cls, directory: str) -> list:
        """Get all supported audio files from directory."""
        audio_files = []

        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    if cls.is_supported_format(file_path):
                        audio_files.append(file_path)
        except OSError as e:
            print(f"Error scanning directory {directory}: {e}")

        return audio_files