## requirements.txt

```txt
mutagen>=1.46.0
tkinter
```

## README.md

```markdown
# Audio Metadata Manager

A GUI application for scanning audio files, reading their metadata tags, and managing them in a SQLite database.

## Features

- **Multi-format Support**: Read metadata from MP3, OGG, FLAC, M4A/AAC, and WAV files
- **Database Management**: Store and manage audio metadata in SQLite databases
- **Batch Processing**: Scan entire directories and automatically extract metadata
- **Search & Filter**: Search entries by title, artist, album, genre, or comments
- **Export Functionality**: Export metadata to CSV format
- **Modern GUI**: Clean, themed interface built with tkinter
- **Metadata Editing**: Add, edit, and delete metadata entries manually
- **Auto-fill**: Automatically populate metadata from audio files

## Supported Audio Formats

- MP3 (ID3v1/ID3v2 tags)
- OGG Vorbis
- FLAC
- M4A/AAC
- WAV

## Requirements

- Python 3.6 or higher
- tkinter (usually included with Python)
- mutagen library for audio metadata reading

## Installation

1. Clone or download the project files
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Starting the Application

```bash
python app.py
```

### Basic Workflow

1. **Create or Open Database**
   - Go to `Database` → `New Database` to create a new SQLite database
   - Or `Database` → `Open Database` to open an existing one

2. **Load Audio Files**
   - Use `File` → `Load Audio Files` to select a directory containing audio files
   - The application will scan recursively and extract metadata automatically

3. **Manage Entries**
   - **Add**: Use `Edit` → `Add Entry` or toolbar button to manually add entries
   - **Edit**: Double-click an entry or use `Edit` → `Edit Entry`
   - **Delete**: Select entry and use `Edit` → `Delete Entry`
   - **Search**: Use `Edit` → `Search` to find specific entries

4. **Export Data**
   - Use `File` → `Export to CSV` to save current data to CSV format

### Menu Structure

#### File Menu
- **Load Audio Files**: Scan directory for audio files and extract metadata
- **Export to CSV**: Export current database contents to CSV
- **Exit**: Close the application

#### Database Menu
- **New Database**: Create a new SQLite database
- **Open Database**: Open an existing database
- **Close Database**: Close current database connection
- **Delete Database**: Delete the current database file

#### Edit Menu
- **Add Entry**: Manually add a new metadata entry
- **Edit Entry**: Edit selected entry
- **Delete Entry**: Delete selected entry
- **Search**: Search entries by various fields
- **Refresh**: Refresh the display

#### Help Menu
- **About**: Show application information

## File Structure

```
audio-metadata-manager/
├── app.py          # Main application file
├── db.py           # Database management
├── id3tag.py       # Metadata reading from audio files
├── dialogs.py      # GUI dialog windows
├── utils.py        # Utility functions
├── requirements.txt # Python dependencies
└── README.md       # This file
```

## Database Schema

The application uses SQLite with the following table structure:

```sql
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
);
```

## Features in Detail

### Automatic Metadata Extraction
- Reads ID3v1/ID3v2 tags from MP3 files
- Supports Vorbis comments in OGG and FLAC files
- Handles iTunes-style tags in M4A files
- Gracefully handles missing or corrupted tags

### Search Functionality
- Search across all fields or specific fields
- Case-insensitive partial matching
- Real-time results display

### Data Validation
- Year validation (1900-2100)
- Track number validation
- Automatic sanitization of metadata values

### Export Options
- CSV export with proper encoding
- Preserves all metadata fields
- User-selectable file location

## Troubleshooting

### Common Issues

1. **"No module named 'mutagen'" error**
   - Install mutagen: `pip install mutagen`

2. **Files not being detected**
   - Ensure files have supported extensions (.mp3, .ogg, .flac, .m4a, .aac, .wav)
   - Check file permissions

3. **Metadata not loading correctly**
   - Some files may have non-standard or corrupted tags
   - Try the "Auto-fill from File" feature in the edit dialog

4. **Database connection issues**
   - Ensure you have write permissions in the selected directory
   - Close any other applications that might be using the database file

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the application.

## License

This project is open source. Please check the license file for details.

## Version History

- **v1.0**: Initial release with core functionality
  - Multi-format audio file support
  - SQLite database management
  - GUI interface with search and export features
```

These files provide comprehensive documentation for setting up and using the Audio Metadata Manager application, including installation instructions, usage guidelines, and troubleshooting information.