"""
Dialog Windows Module
Contains dialog classes for user interactions.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Dict, Optional
from id3tag import MetadataReader


class MetadataDialog:
    """Dialog for adding/editing metadata entries."""

    def __init__(self, parent, title: str, metadata: Dict = None):
        self.result: Optional[Dict] = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x450")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)

        # Center dialog on parent
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))

        # Create widgets first
        self.create_widgets(metadata or {})

        # Wait for the window to be visible before setting grab
        self.dialog.update_idletasks()
        self.dialog.deiconify()
        self.dialog.lift()
        self.dialog.focus_force()

        # Set grab after window is visible
        try:
            self.dialog.grab_set()
        except tk.TclError:
            # If grab fails, continue without it
            pass

    def create_widgets(self, metadata: Dict):
        """Create dialog widgets."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Entry fields
        self.entries = {}
        fields = [
            ('Title:', 'title'),
            ('Artist:', 'artist'),
            ('Album:', 'album'),
            ('Genre:', 'genre'),
            ('Year:', 'year'),
            ('Track Number:', 'track_number'),
            ('Comment:', 'comment'),
            ('File Path:', 'file_path')
        ]

        for i, (label_text, field_name) in enumerate(fields):
            ttk.Label(main_frame, text=label_text).grid(
                row=i, column=0, sticky=tk.W, pady=5
            )

            if field_name == 'comment':
                # Multi-line text widget for comments
                text_widget = tk.Text(main_frame, height=3, width=40)
                text_widget.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=5)
                text_widget.insert('1.0', metadata.get(field_name, ''))
                self.entries[field_name] = text_widget
            else:
                entry = ttk.Entry(main_frame, width=40)
                entry.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=5)
                entry.insert(0, metadata.get(field_name, ''))
                self.entries[field_name] = entry

        # File path browse button
        browse_frame = ttk.Frame(main_frame)
        browse_frame.grid(row=len(fields), column=1, sticky=(tk.W, tk.E), pady=5)

        ttk.Button(
            browse_frame,
            text="Browse...",
            command=self.browse_file
        ).pack(side=tk.RIGHT)

        # Auto-fill button
        ttk.Button(
            browse_frame,
            text="Auto-fill from File",
            command=self.auto_fill_metadata
        ).pack(side=tk.RIGHT, padx=(0, 5))

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=len(fields) + 1, column=0, columnspan=2, pady=20)

        ttk.Button(
            button_frame,
            text="OK",
            command=self.ok_clicked
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Cancel",
            command=self.cancel_clicked
        ).pack(side=tk.LEFT, padx=5)

        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)

    def browse_file(self):
        """Open file dialog to select audio file."""
        file_path = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[
                ("Audio Files", "*.mp3 *.ogg *.flac *.m4a *.aac *.wav"),
                ("All Files", "*.*")
            ]
        )

        if file_path:
            self.entries['file_path'].delete(0, tk.END)
            self.entries['file_path'].insert(0, file_path)

    def auto_fill_metadata(self):
        """Auto-fill metadata from selected file."""
        file_path = self.entries['file_path'].get().strip()

        if not file_path:
            messagebox.showwarning("Warning", "Please select a file first!")
            return

        if MetadataReader.is_supported_format(file_path):
            metadata = MetadataReader.read_metadata(file_path)
            for field, value in metadata.items():
                if field != 'file_path' and value:
                    if field == 'comment':
                        self.entries[field].delete('1.0', tk.END)
                        self.entries[field].insert('1.0', value)
                    else:
                        self.entries[field].delete(0, tk.END)
                        self.entries[field].insert(0, value)
        else:
            messagebox.showwarning("Warning", "Unsupported file format!")

    def ok_clicked(self):
        """Handle OK button click."""
        self.result = {}
        for field, widget in self.entries.items():
            if field == 'comment':
                self.result[field] = widget.get('1.0', tk.END).strip()
            else:
                self.result[field] = widget.get().strip()

        self.dialog.destroy()

    def cancel_clicked(self):
        """Handle Cancel button click."""
        self.result = None
        self.dialog.destroy()


class AboutDialog:
    """About dialog for the application."""

    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("About Audio Metadata Manager")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center dialog on parent
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + 100,
            parent.winfo_rooty() + 100
        ))

        self.create_widgets()

    def create_widgets(self):
        """Create about dialog widgets."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="Audio Metadata Manager",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 10))

        # Version
        version_label = ttk.Label(main_frame, text="Version 1.0")
        version_label.pack()

        # Description
        description = """
A GUI application for scanning audio files, reading their
metadata tags, and managing them in a SQLite database.

Supported Formats:
• MP3, OGG, FLAC, M4A/AAC, WAV

Features:
• Read ID3/audio metadata automatically
• SQLite database management
• Export to CSV
• Modern themed interface
        """

        desc_label = ttk.Label(main_frame, text=description, justify=tk.LEFT)
        desc_label.pack(pady=10)

        # Close button
        ttk.Button(
            main_frame,
            text="Close",
            command=self.dialog.destroy
        ).pack(pady=10)


class SearchDialog:
    """Search dialog for finding entries."""

    def __init__(self, parent):
        self.result: Optional[Dict] = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Search Entries")
        self.dialog.geometry("350x200")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center dialog on parent
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + 100,
            parent.winfo_rooty() + 100
        ))

        self.create_widgets()

    def create_widgets(self):
        """Create search dialog widgets."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Search term
        ttk.Label(main_frame, text="Search term:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.search_entry = ttk.Entry(main_frame, width=30)
        self.search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)

        # Search field
        ttk.Label(main_frame, text="Search in:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.field_var = tk.StringVar(value="all")
        field_combo = ttk.Combobox(
            main_frame,
            textvariable=self.field_var,
            values=["all", "title", "artist", "album", "genre", "comment"],
            state="readonly",
            width=27
        )
        field_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)

        ttk.Button(
            button_frame,
            text="Search",
            command=self.search_clicked
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Cancel",
            command=self.cancel_clicked
        ).pack(side=tk.LEFT, padx=5)

        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)

        # Focus on search entry
        self.search_entry.focus()

    def search_clicked(self):
        """Handle search button click."""
        search_term = self.search_entry.get().strip()
        if not search_term:
            messagebox.showwarning("Warning", "Please enter a search term!")
            return

        field = self.field_var.get()
        if field == "all":
            field = None

        self.result = {
            'search_term': search_term,
            'field': field
        }
        self.dialog.destroy()

    def cancel_clicked(self):
        """Handle cancel button click."""
        self.result = None
        self.dialog.destroy()