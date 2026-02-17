"""
JSON API Response Parser & Formatter
Parses, validates, and pretty-prints JSON data from APIs
"""

import json
import sys
from typing import Any, Dict, List
from pathlib import Path


class JSONParser:
    """Handle JSON parsing, validation, and formatting"""
    
    def __init__(self):
        self.data = None
        self.filepath = None
    
    def load_from_file(self, filepath: str) -> bool:
        """Load JSON from file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            self.filepath = filepath
            print(f"✅ Loaded JSON from: {filepath}")
            return True
        except FileNotFoundError: