#!/usr/bin/env python3
"""
GUI File Explorer
A simple file explorer application built with Tkinter.
Features: Browse directories, view file details, and open files.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from datetime import datetime


class FileExplorer:
    """A simple GUI file explorer using Tkinter."""

    def __init__(self, root):
        """Initialize the file explorer with GUI components."""
        self.root = root
        self.root.title("File Explorer")
        self.root.geometry("800x600")

        # Current directory
        self.current_dir = os.path.expanduser("~")

        # Create toolbar
        toolbar = tk.Frame(root)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        tk.Button(toolbar, text="Up", command=self.go_up).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(toolbar, text="Home", command=self.go_home).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(toolbar, text="Open", command=self.open_file).pack(side=tk.LEFT, padx=5, pady=5)

        # Address bar
        self.address_var = tk.StringVar(value=self.current_dir)
        address_entry = tk.Entry(toolbar, textvariable=self.address_var)
        address_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        tk.Button(toolbar, text="Go", command=self.go_to_address).pack(side=tk.LEFT, padx=5, pady=5)

        # Create treeview for files
        self.tree = ttk.Treeview(root, columns=('size', 'modified'), show='headings')
        self.tree.heading('#0', text='Name')
        self.tree.heading('size', text='Size')
        self.tree.heading('modified', text='Modified')
        self.tree.column('#0', width=300)
        self.tree.column('size', width=100)
        self.tree.column('modified', width=150)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(root, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Bind events
        self.tree.bind('<Double-1>', self.on_double_click)
        self.tree.bind('<Return>', self.open_file)

        # Load initial directory
        self.load_directory()

    def load_directory(self):
        """Load the contents of the current directory."""
        try:
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Get directory contents
            items = os.listdir(self.current_dir)

            # Add parent directory
            if self.current_dir != os.path.sep:
                self.tree.insert('', 'end', text='..', values=('', ''))

            # Sort items: directories first, then files
            dirs = []
            files = []
            for item in items:
                if os.path.isdir(os.path.join(self.current_dir, item)):
                    dirs.append(item)
                else:
                    files.append(item)

            dirs.sort()
            files.sort()

            # Add directories
            for dir_name in dirs:
                path = os.path.join(self.current_dir, dir_name)
                try:
                    modified = datetime.fromtimestamp(os.path.getmtime(path)).strftime('%Y-%m-%d %H:%M')
                    self.tree.insert('', 'end', text=dir_name + '/', values=('', modified))
                except:
                    self.tree.insert('', 'end', text=dir_name + '/', values=('', ''))

            # Add files
            for file_name in files:
                path = os.path.join(self.current_dir, file_name)
                try:
                    size = os.path.getsize(path)
                    size_str = self.format_size(size)
                    modified = datetime.fromtimestamp(os.path.getmtime(path)).strftime('%Y-%m-%d %H:%M')
                    self.tree.insert('', 'end', text=file_name, values=(size_str, modified))
                except:
                    self.tree.insert('', 'end', text=file_name, values=('', ''))

        except PermissionError:
            messagebox.showerror("Error", "Permission denied")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def format_size(self, size):
        """Format file size in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    def go_up(self):
        """Go to parent directory."""
        parent = os.path.dirname(self.current_dir)
        if parent != self.current_dir:
            self.current_dir = parent
            self.address_var.set(self.current_dir)
            self.load_directory()

    def go_home(self):
        """Go to home directory."""
        self.current_dir = os.path.expanduser("~")
        self.address_var.set(self.current_dir)
        self.load_directory()

    def go_to_address(self):
        """Go to the directory specified in the address bar."""
        path = self.address_var.get()
        if os.path.isdir(path):
            self.current_dir = path
            self.load_directory()
        else:
            messagebox.showerror("Error", "Invalid directory")

    def on_double_click(self, event):
        """Handle double click on tree item."""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            name = item['text']
            if name == '..':
                self.go_up()
            elif name.endswith('/'):
                # Directory
                self.current_dir = os.path.join(self.current_dir, name[:-1])
                self.address_var.set(self.current_dir)
                self.load_directory()
            else:
                # File
                self.open_file()

    def open_file(self):
        """Open the selected file."""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            name = item['text']
            if not name.endswith('/') and name != '..':
                file_path = os.path.join(self.current_dir, name)
                try:
                    os.startfile(file_path)  # Windows
                except AttributeError:
                    import subprocess
                    subprocess.run(['xdg-open', file_path])  # Linux


def main():
    """Main function to run the file explorer."""
    root = tk.Tk()
    FileExplorer(root)
    root.mainloop()


if __name__ == "__main__":
    main()