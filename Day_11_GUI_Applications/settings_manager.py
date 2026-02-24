#!/usr/bin/env python3
"""
GUI Settings Manager
A settings management application with a graphical interface.
Features: Manage application settings, save/load configurations, and apply changes.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os


class SettingsManager:
    """A GUI application for managing settings."""

    def __init__(self, root):
        """Initialize the settings manager."""
        self.root = root
        self.root.title("Settings Manager")
        self.root.geometry("500x600")

        # Default settings
        self.settings = {
            'theme': 'light',
            'font_size': 12,
            'auto_save': True,
            'notifications': True,
            'language': 'en',
            'backup_frequency': 'daily'
        }

        # Settings file
        self.settings_file = os.path.join(os.path.expanduser("~"), '.app_settings.json')

        # Load existing settings
        self.load_settings()

        # Create GUI
        self.create_widgets()

    def create_widgets(self):
        """Create the GUI widgets."""
        # Notebook for different setting categories
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # General tab
        general_frame = ttk.Frame(notebook)
        notebook.add(general_frame, text='General')

        # Theme
        ttk.Label(general_frame, text="Theme:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.theme_var = tk.StringVar(value=self.settings['theme'])
        theme_combo = ttk.Combobox(general_frame, textvariable=self.theme_var,
                                  values=['light', 'dark', 'auto'])
        theme_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        # Font size
        ttk.Label(general_frame, text="Font Size:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.font_size_var = tk.IntVar(value=self.settings['font_size'])
        font_spin = tk.Spinbox(general_frame, from_=8, to=24, textvariable=self.font_size_var)
        font_spin.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        # Auto save
        self.auto_save_var = tk.BooleanVar(value=self.settings['auto_save'])
        ttk.Checkbutton(general_frame, text="Auto Save", variable=self.auto_save_var).grid(
            row=2, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)

        # Notifications tab
        notifications_frame = ttk.Frame(notebook)
        notebook.add(notifications_frame, text='Notifications')

        # Notifications enabled
        self.notifications_var = tk.BooleanVar(value=self.settings['notifications'])
        ttk.Checkbutton(notifications_frame, text="Enable Notifications",
                       variable=self.notifications_var).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

        # Backup frequency
        ttk.Label(notifications_frame, text="Backup Frequency:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.backup_var = tk.StringVar(value=self.settings['backup_frequency'])
        backup_combo = ttk.Combobox(notifications_frame, textvariable=self.backup_var,
                                   values=['never', 'daily', 'weekly', 'monthly'])
        backup_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        # Language tab
        language_frame = ttk.Frame(notebook)
        notebook.add(language_frame, text='Language')

        ttk.Label(language_frame, text="Language:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.language_var = tk.StringVar(value=self.settings['language'])
        lang_combo = ttk.Combobox(language_frame, textvariable=self.language_var,
                                 values=['en', 'es', 'fr', 'de', 'it', 'pt'])
        lang_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        # Buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Button(button_frame, text="Save Settings", command=self.save_settings).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Load Settings", command=self.load_settings_file).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Reset to Defaults", command=self.reset_defaults).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Apply", command=self.apply_settings).pack(side=tk.RIGHT, padx=5)

    def save_settings(self):
        """Save current settings to file."""
        # Update settings from GUI
        self.settings['theme'] = self.theme_var.get()
        self.settings['font_size'] = self.font_size_var.get()
        self.settings['auto_save'] = self.auto_save_var.get()
        self.settings['notifications'] = self.notifications_var.get()
        self.settings['language'] = self.language_var.get()
        self.settings['backup_frequency'] = self.backup_var.get()

        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
            messagebox.showinfo("Success", "Settings saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")

    def load_settings(self):
        """Load settings from file."""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                self.settings.update(loaded_settings)
            except Exception as e:
                messagebox.showwarning("Warning", f"Failed to load settings: {str(e)}")

    def load_settings_file(self):
        """Load settings from a user-selected file."""
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    loaded_settings = json.load(f)
                self.settings.update(loaded_settings)
                self.update_gui()
                messagebox.showinfo("Success", "Settings loaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load settings: {str(e)}")

    def reset_defaults(self):
        """Reset settings to defaults."""
        self.settings = {
            'theme': 'light',
            'font_size': 12,
            'auto_save': True,
            'notifications': True,
            'language': 'en',
            'backup_frequency': 'daily'
        }
        self.update_gui()
        messagebox.showinfo("Reset", "Settings reset to defaults!")

    def update_gui(self):
        """Update GUI elements with current settings."""
        self.theme_var.set(self.settings['theme'])
        self.font_size_var.set(self.settings['font_size'])
        self.auto_save_var.set(self.settings['auto_save'])
        self.notifications_var.set(self.settings['notifications'])
        self.language_var.set(self.settings['language'])
        self.backup_var.set(self.settings['backup_frequency'])

    def apply_settings(self):
        """Apply the current settings (placeholder for actual application logic)."""
        messagebox.showinfo("Apply", "Settings applied! (This is a placeholder)")


def main():
    """Main function to run the settings manager."""
    root = tk.Tk()
    SettingsManager(root)
    root.mainloop()


if __name__ == "__main__":
    main()