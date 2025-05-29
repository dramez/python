"""
Database Manager Module
Handles all SQLite database operations for audio metadata.
"""

import sqlite3
import os
from typing import List, Dict, Optional, Tuple


class DatabaseManager:
    """Handles all database operations for audio metadata."""

    def __init__(self):
        self.db_path: Optional[str] = None
        self.connection: Optional[sqlite3.Connection] = None

    def create_database(self, db_path: str) -> bool:
        """Create a new SQLite database with audio metadata table."""
        try:
            self.connection = sqlite3.connect(db_path)
            self.db_path = db_path

            cursor = self.connection.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audio_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    artist TEXT,
                    album TEXT,
                    genre TEXT,
                    year TEXT,
                    track_number TEXT,
                    comment TEXT,
                    file_path TEXT UNIQUE
                )
            ''')
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Database creation error: {e}")
            return False

    def load_database(self, db_path: str) -> bool:
        """Load an existing SQLite database."""
        try:
            if not os.path.exists(db_path):
                return False

            self.connection = sqlite3.connect(db_path)
            self.db_path = db_path

            # Verify table exists and has correct schema
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='audio_metadata'
            ''')

            if not cursor.fetchone():
                # Create table if it doesn't exist
                cursor.execute('''
                    CREATE TABLE audio_metadata (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT,
                        artist TEXT,
                        album TEXT,
                        genre TEXT,
                        year TEXT,
                        track_number TEXT,
                        comment TEXT,
                        file_path TEXT UNIQUE
                    )
                ''')
                self.connection.commit()
            else:
                # Check if all required columns exist
                cursor.execute("PRAGMA table_info(audio_metadata)")
                columns = [column[1] for column in cursor.fetchall()]
                required_columns = ['id', 'title', 'artist', 'album', 'genre', 'year', 'track_number', 'comment', 'file_path']

                # Add missing columns if any
                for col in required_columns:
                    if col not in columns and col != 'id':
                        cursor.execute(f"ALTER TABLE audio_metadata ADD COLUMN {col} TEXT")
                        self.connection.commit()

            return True
        except sqlite3.Error as e:
            print(f"Database loading error: {e}")
            return False

    def close_database(self):
        """Close current database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.db_path = None

    def delete_database(self, db_path: str) -> bool:
        """Delete database file from disk."""
        try:
            if self.db_path == db_path:
                self.close_database()

            if os.path.exists(db_path):
                os.remove(db_path)
                return True
            return False
        except OSError as e:
            print(f"Database deletion error: {e}")
            return False

    def insert_metadata(self, metadata: Dict) -> bool:
        """Insert or update audio metadata in database."""
        if not self.connection:
            return False

        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO audio_metadata
                (title, artist, album, genre, year, track_number, comment, file_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metadata.get('title', ''),
                metadata.get('artist', ''),
                metadata.get('album', ''),
                metadata.get('genre', ''),
                metadata.get('year', ''),
                metadata.get('track_number', ''),
                metadata.get('comment', ''),
                metadata.get('file_path', '')
            ))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Insert error: {e}")
            return False

    def get_all_metadata(self) -> List[Tuple]:
        """Retrieve all metadata entries from database."""
        if not self.connection:
            return []

        try:
            cursor = self.connection.cursor()
            # Explicitly specify column order to match treeview
            cursor.execute('''
                SELECT id, title, artist, album, genre, year, track_number, comment, file_path
                FROM audio_metadata
                ORDER BY artist, album, track_number
            ''')
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Retrieval error: {e}")
            return []

    def update_metadata(self, entry_id: int, metadata: Dict) -> bool:
        """Update existing metadata entry."""
        if not self.connection:
            return False

        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                UPDATE audio_metadata
                SET title=?, artist=?, album=?, genre=?, year=?,
                    track_number=?, comment=?, file_path=?
                WHERE id=?
            ''', (
                metadata.get('title', ''),
                metadata.get('artist', ''),
                metadata.get('album', ''),
                metadata.get('genre', ''),
                metadata.get('year', ''),
                metadata.get('track_number', ''),
                metadata.get('comment', ''),
                metadata.get('file_path', ''),
                entry_id
            ))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Update error: {e}")
            return False

    def delete_metadata(self, entry_id: int) -> bool:
        """Delete metadata entry by ID."""
        if not self.connection:
            return False

        try:
            cursor = self.connection.cursor()
            cursor.execute('DELETE FROM audio_metadata WHERE id=?', (entry_id,))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Delete error: {e}")
            return False

    def is_connected(self) -> bool:
        """Check if database is connected."""
        return self.connection is not None

    def get_database_info(self) -> Dict:
        """Get information about current database."""
        if not self.connection:
            return {'connected': False}

        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT COUNT(*) FROM audio_metadata')
            count = cursor.fetchone()[0]

            return {
                'path': self.db_path,
                'entry_count': count,
                'connected': True
            }
        except sqlite3.Error:
            return {'connected': False}

    def get_metadata_by_id(self, entry_id: int) -> Optional[Tuple]:
        """Get metadata entry by ID."""
        if not self.connection:
            return None

        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT id, title, artist, album, genre, year, track_number, comment, file_path
                FROM audio_metadata WHERE id=?
            ''', (entry_id,))
            return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Retrieval error: {e}")
            return None

    def search_metadata(self, search_term: str, field: str = None) -> List[Tuple]:
        """Search metadata entries."""
        if not self.connection:
            return []

        try:
            cursor = self.connection.cursor()

            if field and field in ['title', 'artist', 'album', 'genre', 'year', 'comment']:
                # Search in specific field
                query = f'''
                    SELECT id, title, artist, album, genre, year, track_number, comment, file_path
                    FROM audio_metadata
                    WHERE {field} LIKE ?
                    ORDER BY artist, album, track_number
                '''
                cursor.execute(query, (f'%{search_term}%',))
            else:
                # Search in all text fields
                query = '''
                    SELECT id, title, artist, album, genre, year, track_number, comment, file_path
                    FROM audio_metadata
                    WHERE title LIKE ? OR artist LIKE ? OR album LIKE ?
                    OR genre LIKE ? OR comment LIKE ?
                    ORDER BY artist, album, track_number
                '''
                search_pattern = f'%{search_term}%'
                cursor.execute(query, (search_pattern, search_pattern, search_pattern,
                                     search_pattern, search_pattern))

            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Search error: {e}")
            return []

    def get_statistics(self) -> Dict:
        """Get database statistics."""
        if not self.connection:
            return {}

        try:
            cursor = self.connection.cursor()

            # Total entries
            cursor.execute('SELECT COUNT(*) FROM audio_metadata')
            total_entries = cursor.fetchone()[0]

            # Unique artists
            cursor.execute('SELECT COUNT(DISTINCT artist) FROM audio_metadata WHERE artist != ""')
            unique_artists = cursor.fetchone()[0]

            # Unique albums
            cursor.execute('SELECT COUNT(DISTINCT album) FROM audio_metadata WHERE album != ""')
            unique_albums = cursor.fetchone()[0]

            # Unique genres
            cursor.execute('SELECT COUNT(DISTINCT genre) FROM audio_metadata WHERE genre != ""')
            unique_genres = cursor.fetchone()[0]

            return {
                'total_entries': total_entries,
                'unique_artists': unique_artists,
                'unique_albums': unique_albums,
                'unique_genres': unique_genres
            }
        except sqlite3.Error as e:
            print(f"Statistics error: {e}")
            return {}