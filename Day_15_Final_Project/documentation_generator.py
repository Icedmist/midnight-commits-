#!/usr/bin/env python3
"""
Documentation Generator - Day 15 Final Project
Automatically generates comprehensive documentation for the entire project.
"""

import argparse
import ast
import inspect
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

import markdown


class DocumentationGenerator:
    """
    Generates comprehensive documentation for the Midnight Commits project.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.output_dir = project_root / "docs"
        self.output_dir.mkdir(exist_ok=True)
        self.project_data = {}

    def generate_full_documentation(self) -> Path:
        """
        Generate complete documentation suite.

        Returns:
            Path to main documentation file
        """
        print("🔍 Analyzing project structure...")
        self._analyze_project()

        print("📝 Generating API documentation...")
        self._generate_api_docs()

        print("📊 Generating project overview...")
        self._generate_project_overview()

        print("📈 Generating statistics...")
        self._generate_statistics()

        print("🔗 Generating cross-references...")
        self._generate_cross_references()

        print("📖 Generating main documentation...")
        main_doc = self._generate_main_documentation()

        print("📚 Generating table of contents...")
        self._generate_table_of_contents()

        print(f"✅ Documentation generated in: {self.output_dir}")
        return main_doc

    def _analyze_project(self):
        """Analyze the entire project structure."""
        self.project_data = {
            'days': {},
            'total_files': 0,
            'total_lines': 0,
            'languages': {},
            'dependencies': set(),
            'functions': [],
            'classes': [],
            'modules': []
        }

        # Analyze each day directory
        for day_dir in sorted(self.project_root.glob("Day_*/")):
            day_name = day_dir.name
            day_data = self._analyze_day(day_dir)
            self.project_data['days'][day_name] = day_data

        # Analyze main files
        main_files = ['books_data.csv', 'main-README.md', 'README.md']
        for file in main_files:
            file_path = self.project_root / file
            if file_path.exists():
                self._analyze_file(file_path, 'main')

    def _analyze_day(self, day_dir: Path) -> Dict[str, Any]:
        """Analyze a single day directory."""
        day_data = {
            'name': day_dir.name,
            'files': [],
            'total_lines': 0,
            'functions': [],
            'classes': [],
            'description': self._extract_day_description(day_dir)
        }

        for file_path in day_dir.glob("*.py"):
            if file_path.name == "__init__.py":
                continue

            file_data = self._analyze_python_file(file_path)
            day_data['files'].append(file_data)
            day_data['total_lines'] += file_data['lines']
            day_data['functions'].extend(file_data['functions'])
            day_data['classes'].extend(file_data['classes'])

        return day_data

    def _analyze_python_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a Python file for documentation."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            file_data = {
                'name': file_path.name,
                'path': str(file_path.relative_to(self.project_root)),
                'lines': len(content.splitlines()),
                'functions': [],
                'classes': [],
                'imports': [],
                'docstring': self._extract_module_docstring(tree)
            }

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_data = {
                        'name': node.name,
                        'line': node.lineno,
                        'args': [arg.arg for arg in node.args.args],
                        'docstring': ast.get_docstring(node) or ""
                    }
                    file_data['functions'].append(func_data)
                    self.project_data['functions'].append(func_data)

                elif isinstance(node, ast.ClassDef):
                    class_data = {
                        'name': node.name,
                        'line': node.lineno,
                        'methods': [],
                        'docstring': ast.get_docstring(node) or ""
                    }

                    # Extract methods
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method_data = {
                                'name': item.name,
                                'line': item.lineno,
                                'args': [arg.arg for arg in item.args.args],
                                'docstring': ast.get_docstring(item) or ""
                            }
                            class_data['methods'].append(method_data)

                    file_data['classes'].append(class_data)
                    self.project_data['classes'].append(class_data)

                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        file_data['imports'].append(alias.name)

                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        file_data['imports'].append(f"{module}.{alias.name}")

            self.project_data['total_files'] += 1
            self.project_data['total_lines'] += file_data['lines']

            return file_data

        except Exception as e:
            print(f"Warning: Could not analyze {file_path}: {e}")
            return {
                'name': file_path.name,
                'path': str(file_path.relative_to(self.project_root)),
                'lines': 0,
                'functions': [],
                'classes': [],
                'imports': [],
                'docstring': ""
            }

    def _extract_module_docstring(self, tree: ast.AST) -> str:
        """Extract module-level docstring."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Str):
                return node.value.s
        return ""

    def _extract_day_description(self, day_dir: Path) -> str:
        """Extract day description from __init__.py or directory name."""
        init_file = day_dir / "__init__.py"
        if init_file.exists():
            try:
                with open(init_file, 'r') as f:
                    content = f.read()
                    # Look for description in comments or docstring
                    lines = content.split('\n')
                    for line in lines[:10]:  # Check first 10 lines
                        line = line.strip()
                        if line.startswith('"""') or line.startswith("'''"):
                            # Extract until closing quotes
                            desc = line.replace('"""', '').replace("'''", '').strip()
                            if desc:
                                return desc
            except:
                pass

        # Fallback: parse directory name
        day_match = re.match(r'Day_(\d+)_(.+)', day_dir.name)
        if day_match:
            day_num = day_match.group(1)
            theme = day_match.group(2).replace('_', ' ')
            return f"Day {day_num}: {theme}"

        return day_dir.name

    def _analyze_file(self, file_path: Path, category: str):
        """Analyze non-Python files."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = len(content.splitlines())

            self.project_data['total_files'] += 1
            self.project_data['total_lines'] += lines

        except:
            pass

    def _generate_api_docs(self):
        """Generate API documentation."""
        api_doc = self.output_dir / "api_reference.md"

        with open(api_doc, 'w') as f:
            f.write("# API Reference\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            for day_name, day_data in self.project_data['days'].items():
                f.write(f"## {day_name}\n\n")
                if day_data['description']:
                    f.write(f"{day_data['description']}\n\n")

                for file_data in day_data['files']:
                    f.write(f"### {file_data['name']}\n\n")

                    if file_data['docstring']:
                        f.write(f"{file_data['docstring']}\n\n")

                    if file_data['classes']:
                        f.write("#### Classes\n\n")
                        for cls in file_data['classes']:
                            f.write(f"**{cls['name']}**\n\n")
                            if cls['docstring']:
                                f.write(f"{cls['docstring']}\n\n")

                            if cls['methods']:
                                f.write("Methods:\n\n")
                                for method in cls['methods']:
                                    args_str = ", ".join(method['args'])
                                    f.write(f"- `{method['name']}({args_str})`\n")
                                    if method['docstring']:
                                        f.write(f"  {method['docstring'][:100]}...\n")
                                f.write("\n")

                    if file_data['functions']:
                        f.write("#### Functions\n\n")
                        for func in file_data['functions']:
                            args_str = ", ".join(func['args'])
                            f.write(f"- `{func['name']}({args_str})`\n")
                            if func['docstring']:
                                f.write(f"  {func['docstring'][:100]}...\n")
                        f.write("\n")

                    f.write("---\n\n")

    def _generate_project_overview(self):
        """Generate project overview documentation."""
        overview_doc = self.output_dir / "project_overview.md"

        with open(overview_doc, 'w') as f:
            f.write("# Project Overview\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## Project Structure\n\n")
            f.write("```\n")
            f.write("midnight-commits/\n")

            for day_name in sorted(self.project_data['days'].keys()):
                day_data = self.project_data['days'][day_name]
                f.write(f"├── {day_name}/\n")
                f.write("│   ├── __init__.py\n")
                for file_data in day_data['files']:
                    f.write(f"│   ├── {file_data['name']}\n")
                f.write("│\n")

            f.write("├── docs/\n")
            f.write("├── main-README.md\n")
            f.write("├── books_data.csv\n")
            f.write("└── README.md\n")
            f.write("```\n\n")

            f.write("## Day Summaries\n\n")
            for day_name, day_data in self.project_data['days'].items():
                f.write(f"### {day_name}\n\n")
                f.write(f"- **Description**: {day_data['description']}\n")
                f.write(f"- **Files**: {len(day_data['files'])}\n")
                f.write(f"- **Lines of Code**: {day_data['total_lines']}\n")
                f.write(f"- **Functions**: {len(day_data['functions'])}\n")
                f.write(f"- **Classes**: {len(day_data['classes'])}\n\n")

    def _generate_statistics(self):
        """Generate project statistics."""
        stats_doc = self.output_dir / "statistics.md"

        with open(stats_doc, 'w') as f:
            f.write("# Project Statistics\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            # Overall stats
            f.write("## Overall Statistics\n\n")
            f.write(f"- **Total Files**: {self.project_data['total_files']}\n")
            f.write(f"- **Total Lines of Code**: {self.project_data['total_lines']}\n")
            f.write(f"- **Total Functions**: {len(self.project_data['functions'])}\n")
            f.write(f"- **Total Classes**: {len(self.project_data['classes'])}\n")
            f.write(f"- **Days Completed**: {len(self.project_data['days'])}\n\n")

            # Per-day stats
            f.write("## Per-Day Statistics\n\n")
            f.write("| Day | Files | Lines | Functions | Classes |\n")
            f.write("|-----|-------|-------|-----------|--------|\n")

            for day_name, day_data in self.project_data['days'].items():
                f.write(f"| {day_name} | {len(day_data['files'])} | {day_data['total_lines']} | {len(day_data['functions'])} | {len(day_data['classes'])} |\n")

            f.write("\n")

            # Code distribution
            f.write("## Code Distribution\n\n")
            total_lines = self.project_data['total_lines']
            if total_lines > 0:
                f.write("### Lines of Code by Day\n\n")
                for day_name, day_data in self.project_data['days'].items():
                    percentage = (day_data['total_lines'] / total_lines) * 100
                    f.write(f"- **{day_name}**: {day_data['total_lines']} lines ({percentage:.1f}%)\n")

    def _generate_cross_references(self):
        """Generate cross-reference documentation."""
        xref_doc = self.output_dir / "cross_references.md"

        with open(xref_doc, 'w') as f:
            f.write("# Cross References\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            # Function cross-references
            f.write("## Function Index\n\n")
            functions_by_name = {}
            for func in self.project_data['functions']:
                name = func['name']
                if name not in functions_by_name:
                    functions_by_name[name] = []
                functions_by_name[name].append(func)

            for func_name in sorted(functions_by_name.keys()):
                f.write(f"### {func_name}\n\n")
                for func in functions_by_name[func_name]:
                    f.write(f"- Defined in: `{func.get('file', 'unknown')}` at line {func['line']}\n")
                    if func['docstring']:
                        f.write(f"  - {func['docstring'][:50]}...\n")
                f.write("\n")

            # Class cross-references
            f.write("## Class Index\n\n")
            classes_by_name = {}
            for cls in self.project_data['classes']:
                name = cls['name']
                if name not in classes_by_name:
                    classes_by_name[name] = []
                classes_by_name[name].append(cls)

            for class_name in sorted(classes_by_name.keys()):
                f.write(f"### {class_name}\n\n")
                for cls in classes_by_name[class_name]:
                    f.write(f"- Defined in: `{cls.get('file', 'unknown')}` at line {cls['line']}\n")
                    if cls['docstring']:
                        f.write(f"  - {cls['docstring'][:50]}...\n")
                f.write("\n")

    def _generate_main_documentation(self) -> Path:
        """Generate main documentation file."""
        main_doc = self.output_dir / "README.md"

        with open(main_doc, 'w') as f:
            f.write("# Midnight Commits - Complete Documentation\n\n")
            f.write("![Project Status](https://img.shields.io/badge/status-complete-success)\n")
            f.write("![Python Version](https://img.shields.io/badge/python-3.8+-blue)\n")
            f.write("![License](https://img.shields.io/badge/license-MIT-green)\n\n")

            f.write("## Overview\n\n")
            f.write("Midnight Commits is a comprehensive 24-day Python learning project that demonstrates ")
            f.write("progressive mastery of Python programming concepts, from basic utilities to ")
            f.write("advanced topics like concurrency, security, and machine learning.\n\n")

            f.write("## Project Structure\n\n")
            f.write("The project is organized into 24 days, each focusing on a specific theme:\n\n")

            days = [
                ("Days 1-7", "Basic Python concepts and utilities"),
                ("Days 8-10", "Web scraping, networking, and testing"),
                ("Days 11-14", "GUI, machine learning, security, and concurrency"),
                ("Day 15", "Final project integration and deployment")
            ]

            for period, description in days:
                f.write(f"- **{period}**: {description}\n")

            f.write("\n## Quick Start\n\n")
            f.write("```bash\n")
            f.write("# Clone the repository\n")
            f.write("git clone https://github.com/midnight-commits/midnight-commits.git\n")
            f.write("cd midnight-commits\n\n")
            f.write("# Install dependencies\n")
            f.write("pip install -r requirements.txt\n\n")
            f.write("# Run any day's script\n")
            f.write("python Day_01_Time_State/timer.py --help\n")
            f.write("```\n\n")

            f.write("## Documentation Sections\n\n")
            f.write("- [Project Overview](project_overview.md) - Detailed project structure\n")
            f.write("- [API Reference](api_reference.md) - Complete API documentation\n")
            f.write("- [Statistics](statistics.md) - Project metrics and analytics\n")
            f.write("- [Cross References](cross_references.md) - Function and class index\n\n")

            f.write("## Key Features\n\n")
            f.write("- ✅ **24 Complete Days** of Python projects\n")
            f.write("- ✅ **Progressive Complexity** from basics to advanced topics\n")
            f.write("- ✅ **Real-world Applications** with practical CLI tools\n")
            f.write("- ✅ **Comprehensive Documentation** with auto-generated docs\n")
            f.write("- ✅ **Modular Architecture** with reusable components\n")
            f.write("- ✅ **Error Handling** and logging throughout\n")
            f.write("- ✅ **Testing & Validation** in each component\n\n")

            f.write("## Technology Stack\n\n")
            f.write("### Core Libraries\n")
            f.write("- **Web Scraping**: requests, beautifulsoup4, selenium\n")
            f.write("- **Data Science**: pandas, numpy, scikit-learn, matplotlib\n")
            f.write("- **Security**: cryptography, bcrypt, argon2\n")
            f.write("- **GUI**: tkinter, PIL\n")
            f.write("- **Async**: asyncio, aiohttp\n")
            f.write("- **System**: os, pathlib, subprocess\n\n")

            f.write("### Development Tools\n")
            f.write("- **Testing**: unittest, logging\n")
            f.write("- **Documentation**: Markdown, automated generation\n")
            f.write("- **Deployment**: setuptools, PyInstaller, Docker\n\n")

            f.write("## Project Statistics\n\n")
            f.write(f"- **Total Files**: {self.project_data['total_files']}\n")
            f.write(f"- **Lines of Code**: {self.project_data['total_lines']}\n")
            f.write(f"- **Python Functions**: {len(self.project_data['functions'])}\n")
            f.write(f"- **Python Classes**: {len(self.project_data['classes'])}\n")
            f.write(f"- **Days Completed**: {len(self.project_data['days'])}\n\n")

            f.write("## Contributing\n\n")
            f.write("1. Fork the repository\n")
            f.write("2. Create a feature branch\n")
            f.write("3. Make your changes\n")
            f.write("4. Add tests if applicable\n")
            f.write("5. Run the documentation generator\n")
            f.write("6. Submit a pull request\n\n")

            f.write("## License\n\n")
            f.write("This project is licensed under the MIT License - see the LICENSE file for details.\n\n")

            f.write("---\n\n")
            f.write(f"*Documentation generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")

        return main_doc

    def _generate_table_of_contents(self):
        """Generate table of contents for all documentation."""
        toc_doc = self.output_dir / "table_of_contents.md"

        with open(toc_doc, 'w') as f:
            f.write("# Table of Contents\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## Main Documentation\n\n")
            f.write("- [README](README.md) - Main project documentation\n")
            f.write("- [Project Overview](project_overview.md) - Project structure and organization\n")
            f.write("- [API Reference](api_reference.md) - Complete API documentation\n")
            f.write("- [Statistics](statistics.md) - Project metrics and analytics\n")
            f.write("- [Cross References](cross_references.md) - Function and class index\n\n")

            f.write("## Day Documentation\n\n")
            for day_name, day_data in self.project_data['days'].items():
                f.write(f"### {day_name}\n\n")
                f.write(f"- **Description**: {day_data['description']}\n")
                f.write("- Files:\n")

                for file_data in day_data['files']:
                    f.write(f"  - [{file_data['name']}](../{day_data['name']}/{file_data['name']})\n")
                    if file_data['docstring']:
                        f.write(f"    - {file_data['docstring'][:50]}...\n")

                f.write("\n")


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="Documentation Generator for Midnight Commits"
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root directory"
    )
    parser.add_argument(
        "--output",
        help="Output directory for documentation"
    )

    args = parser.parse_args()

    # Initialize documentation generator
    project_root = Path(args.project_root).resolve()
    if args.output:
        output_dir = Path(args.output)
    else:
        output_dir = project_root / "docs"

    generator = DocumentationGenerator(project_root)
    if args.output:
        generator.output_dir = output_dir
        generator.output_dir.mkdir(exist_ok=True)

    try:
        main_doc = generator.generate_full_documentation()
        print(f"✓ Documentation generated successfully")
        print(f"Main documentation: {main_doc}")
        print(f"Output directory: {generator.output_dir}")

    except Exception as e:
        print(f"✗ Documentation generation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()