"""
Audio Metadata Manager
Main application module with GUI interface.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from typing import Optional

from db import DatabaseManager
from id3tag import MetadataReader
from dialogs import MetadataDialog, AboutDialog, SearchDialog
from utils import FileUtils, ValidationUtils


class AudioMetadataManager:
    """Main application class for Audio Metadata Manager."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Audio Metadata Manager")
        self.root.geometry("1200x700")

        # Apply modern theme
        style = ttk.Style()
        style.theme_use('clam')

        # Initialize components
        self.db_manager = DatabaseManager()
        self.current_data = []

        # Create GUI
        self.create_menu()
        self.create_widgets()
        self.update_status()

    def create_menu(self):
        """Create application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load Audio Files", command=self.load_audio_files)
        file_menu.add_separator()
        file_menu.add_command(label="Export to CSV", command=self.export_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Database menu
        db_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Database", menu=db_menu)
        db_menu.add_command(label="New Database", command=self.new_database)
        db_menu.add_command(label="Open Database", command=self.open_database)
        db_menu.add_separator()
        db_menu.add_command(label="Close Database", command=self.close_database)
        db_menu.add_command(label="Delete Database", command=self.delete_database)

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Add Entry", command=self.add_entry)
        edit_menu.add_command(label="Edit Entry", command=self.edit_entry)
        edit_menu.add_command(label="Delete Entry", command=self.delete_entry)
        edit_menu.add_separator()
        edit_menu.add_command(label="Search", command=self.search_entries)
        edit_menu.add_command(label="Refresh", command=self.refresh_display)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def create_widgets(self):
        """Create main application widgets."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Toolbar
        toolbar_frame = ttk.Frame(main_frame)
        toolbar_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Button(toolbar_frame, text="New DB", command=self.new_database).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_frame, text="Open DB", command=self.open_database).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_frame, text="Load Files", command=self.load_audio_files).pack(side=tk.LEFT, padx=2)
        ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        ttk.Button(toolbar_frame, text="Add", command=self.add_entry).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_frame, text="Edit", command=self.edit_entry).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_frame, text="Delete", command=self.delete_entry).pack(side=tk.LEFT, padx=2)
        ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        ttk.Button(toolbar_frame, text="Search", command=self.search_entries).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_frame, text="Refresh", command=self.refresh_display).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_frame, text="Export CSV", command=self.export_csv).pack(side=tk.LEFT, padx=2)

        # Treeview frame
        tree_frame = ttk.Frame(main_frame)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Create treeview
        columns = ('ID', 'Title', 'Artist', 'Album', 'Genre', 'Year', 'Track', 'Comment', 'File Path')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)

        # Configure columns
        self.tree.heading('ID', text='ID')
        self.tree.heading('Title', text='Title')
        self.tree.heading('Artist', text='Artist')
        self.tree.heading('Album', text='Album')
        self.tree.heading('Genre', text='Genre')
        self.tree.heading('Year', text='Year')
        self.tree.heading('Track', text='Track')
        self.tree.heading('Comment', text='Comment')
        self.tree.heading('File Path', text='File Path')

        # Set column widths
        self.tree.column('ID', width=50, minwidth=50)
        self.tree.column('Title', width=150, minwidth=100)
        self.tree.column('Artist', width=120, minwidth=80)
        self.tree.column('Album', width=120, minwidth=80)
        self.tree.column('Genre', width=80, minwidth=60)
        self.tree.column('Year', width=60, minwidth=50)
        self.tree.column('Track', width=60, minwidth=50)
        self.tree.column('Comment', width=100, minwidth=80)
        self.tree.column('File Path', width=200, minwidth=150)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Grid treeview and scrollbars
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # Bind double-click event
        self.tree.bind('<Double-1>', lambda event: self.edit_entry())

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

    def new_database(self):
        """Create a new database."""
        file_path = filedialog.asksaveasfilename(
            title="Create New Database",
            defaultextension=".db",
            filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")]
        )

        if file_path:
            if self.db_manager.create_database(file_path):
                self.refresh_display()
                self.update_status()
                messagebox.showinfo("Success", "Database created successfully!")
            else:
                messagebox.showerror("Error", "Failed to create database!")

    def open_database(self):
        """Open an existing database."""
        file_path = filedialog.askopenfilename(
            title="Open Database",
            filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")]
        )

        if file_path:
            if self.db_manager.load_database(file_path):
                self.refresh_display()
                self.update_status()
                messagebox.showinfo("Success", "Database loaded successfully!")
            else:
                messagebox.showerror("Error", "Failed to load database!")

    def close_database(self):
        """Close current database."""
        if self.db_manager.is_connected():
            self.db_manager.close_database()
            self.refresh_display()
            self.update_status()
            messagebox.showinfo("Info", "Database closed.")
        else:
            messagebox.showwarning("Warning", "No database is currently open!")

    def delete_database(self):
        """Delete current database file."""
        if not self.db_manager.is_connected():
            messagebox.showwarning("Warning", "No database is currently open!")
            return

        db_info = self.db_manager.get_database_info()
        db_path = db_info.get('path', '')

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the database?\n{db_path}"):
            if self.db_manager.delete_database(db_path):
                self.refresh_display()
                self.update_status()
                messagebox.showinfo("Success", "Database deleted successfully!")
            else:
                messagebox.showerror("Error", "Failed to delete database!")

    def load_audio_files(self):
        """Load audio files from directory."""
        if not self.db_manager.is_connected():
            messagebox.showwarning("Warning", "Please create or open a database first!")
            return

        directory = filedialog.askdirectory(title="Select Directory with Audio Files")
        if not directory:
            return

        try:
            audio_files = MetadataReader.get_audio_files(directory)
            if not audio_files:
                messagebox.showinfo("Info", "No supported audio files found in the selected directory!")
                return

            # Progress tracking
            total_files = len(audio_files)
            processed = 0
            errors = 0

            # Create progress window
            progress_window = tk.Toplevel(self.root)
            progress_window.title("Loading Audio Files")
            progress_window.geometry("400x150")
            progress_window.transient(self.root)
            progress_window.grab_set()

            progress_frame = ttk.Frame(progress_window, padding="20")
            progress_frame.pack(fill=tk.BOTH, expand=True)

            progress_label = ttk.Label(progress_frame, text="Processing audio files...")
            progress_label.pack(pady=10)

            progress_bar = ttk.Progressbar(progress_frame, length=300, mode='determinate')
            progress_bar.pack(pady=10)
            progress_bar['maximum'] = total_files

            status_label = ttk.Label(progress_frame, text="")
            status_label.pack()

            # Process files
            for i, file_path in enumerate(audio_files):
                try:
                    metadata = MetadataReader.read_metadata(file_path)
                    if self.db_manager.insert_metadata(metadata):
                        processed += 1
                    else:
                        errors += 1

                    # Update progress
                    progress_bar['value'] = i + 1
                    status_label.config(text=f"Processed: {processed}, Errors: {errors}")
                    progress_window.update()

                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
                    errors += 1

            progress_window.destroy()

            # Show results
            self.refresh_display()
            self.update_status()
            messagebox.showinfo("Complete",
                              f"Processing complete!\n"
                              f"Total files: {total_files}\n"
                              f"Successfully processed: {processed}\n"
                              f"Errors: {errors}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load audio files: {e}")

    def add_entry(self):
        """Add new metadata entry."""
        if not self.db_manager.is_connected():
            messagebox.showwarning("Warning", "Please create or open a database first!")
            return

        dialog = MetadataDialog(self.root, "Add New Entry")
        self.root.wait_window(dialog.dialog)

        if dialog.result:
            if self.db_manager.insert_metadata(dialog.result):
                self.refresh_display()
                self.update_status()
                messagebox.showinfo("Success", "Entry added successfully!")
            else:
                messagebox.showerror("Error", "Failed to add entry!")

    def edit_entry(self):
        """Edit selected metadata entry."""
        if not self.db_manager.is_connected():
            messagebox.showwarning("Warning", "Please load or create a database first!")
            return

        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an entry to edit!")
            return

        try:
            # Get selected item data
            item = self.tree.item(selection[0])
            values = item['values']

            # Ensure we have enough values
            if len(values) < 9:
                messagebox.showerror("Error", "Invalid entry data!")
                return

            # Map treeview values to metadata dictionary
            # Treeview columns: ID, Title, Artist, Album, Genre, Year, Track, Comment, File Path
            metadata = {
                'title': str(values[1]) if len(values) > 1 else '',
                'artist': str(values[2]) if len(values) > 2 else '',
                'album': str(values[3]) if len(values) > 3 else '',
                'genre': str(values[4]) if len(values) > 4 else '',
                'year': str(values[5]) if len(values) > 5 else '',
                'track_number': str(values[6]) if len(values) > 6 else '',
                'comment': str(values[7]) if len(values) > 7 else '',
                'file_path': str(values[8]) if len(values) > 8 else ''
            }

            dialog = MetadataDialog(self.root, "Edit Entry", metadata)
            self.root.wait_window(dialog.dialog)

            if dialog.result:
                entry_id = values[0]
                if self.db_manager.update_metadata(entry_id, dialog.result):
                    self.refresh_display()
                    self.update_status()
                    messagebox.showinfo("Success", "Entry updated successfully!")
                else:
                    messagebox.showerror("Error", "Failed to update entry!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to edit entry: {e}")

    def delete_entry(self):
        """Delete selected metadata entry."""
        if not self.db_manager.is_connected():
            messagebox.showwarning("Warning", "Please load or create a database first!")
            return

        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an entry to delete!")
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected entry?"):
            try:
                item = self.tree.item(selection[0])
                entry_id = item['values'][0]

                if self.db_manager.delete_metadata(entry_id):
                    self.refresh_display()
                    self.update_status()
                    messagebox.showinfo("Success", "Entry deleted successfully!")
                else:
                    messagebox.showerror("Error", "Failed to delete entry!")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete entry: {e}")

    def search_entries(self):
        """Search for entries."""
        if not self.db_manager.is_connected():
            messagebox.showwarning("Warning", "Please load or create a database first!")
            return

        dialog = SearchDialog(self.root)
        self.root.wait_window(dialog.dialog)

        if dialog.result:
            search_term = dialog.result['search_term']
            field = dialog.result['field']

            results = self.db_manager.search_metadata(search_term, field)
            self.display_data(results)
            self.status_var.set(f"Search results: {len(results)} entries found")

    def export_csv(self):
        """Export current data to CSV."""
        if not self.current_data:
            messagebox.showwarning("Warning", "No data to export!")
            return

        if FileUtils.export_to_csv(self.current_data):
            messagebox.showinfo("Success", "Data exported successfully!")

    def refresh_display(self):
        """Refresh the display with current database data."""
        # Clear current items
        for item in self.tree.get_children():
            self.tree.delete(item)

        if self.db_manager.is_connected():
            self.current_data = self.db_manager.get_all_metadata()
            self.display_data(self.current_data)
        else:
            self.current_data = []

    def display_data(self, data):
        """Display data in the treeview."""
        # Clear current items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Insert new data
        # Database columns: id, title, artist, album, genre, year, track_number, comment, file_path
        # Treeview columns: ID, Title, Artist, Album, Genre, Year, Track, Comment, File Path
        for row in data:
            if len(row) >= 9:  # Ensure we have all columns
                # Map database row to treeview columns in correct order
                display_row = (
                    row[0],  # ID
                    row[1],  # Title
                    row[2],  # Artist
                    row[3],  # Album
                    row[4],  # Genre
                    row[5],  # Year
                    row[6],  # Track Number
                    row[7],  # Comment
                    row[8]   # File Path
                )
                self.tree.insert('', tk.END, values=display_row)

    def update_status(self):
        """Update status bar."""
        if self.db_manager.is_connected():
            db_info = self.db_manager.get_database_info()
            entry_count = db_info.get('entry_count', 0)
            db_path = db_info.get('path', '')
            self.status_var.set(f"Database: {os.path.basename(db_path)} | Entries: {entry_count}")
        else:
            self.status_var.set("No database loaded")

    def show_about(self):
        """Show about dialog."""
        AboutDialog(self.root)

    def debug_database_content(self):
        """Debug method to check database content."""
        if not self.db_manager.is_connected():
            print("No database connected")
            return

        try:
            cursor = self.db_manager.connection.cursor()
            cursor.execute("PRAGMA table_info(audio_metadata)")
            columns = cursor.fetchall()
            print("Database columns:")
            for col in columns:
                print(f"  {col[1]} ({col[2]})")

            cursor.execute("SELECT * FROM audio_metadata LIMIT 3")
            rows = cursor.fetchall()
            print("\nFirst 3 rows:")
            for i, row in enumerate(rows):
                print(f"Row {i+1}: {row}")

        except Exception as e:
            print(f"Debug error: {e}")

    def run(self):
        """Start the application."""
        self.root.mainloop()


def main():
    """Main function to run the application."""
    app = AudioMetadataManager()
    app.run()


if __name__ == "__main__":
    main()