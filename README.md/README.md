# 🌙 Midnight Commits: Python 2025 Sprint

> *"Consistently building, one night at a time."*

## 📖 About This Repository
This repository documents my **24-Day Python Sprint** (starting January 20, 2026). The goal is to build 3-4 complete, documented, and functional Python projects every single day, ranging from core utilities to advanced AI and Cloud deployments.

Each folder represents a specific day's theme, containing multiple isolated scripts and mini-apps.

**Current Status:** 🟢 Active (Day 3 Complete)

---

## 📂 Project Log

### **Phase 1: The Warm-Up (Scripting & Logic)**

| Day | Date | Theme | Projects & Files | Key Concepts |
| :--- | :--- | :--- | :--- | :--- |
| **01** | Jan 20 | **Core Utilities** | 1. **Robust Calculator** (`calculator.py`)<br>2. **Palindrome Checker** (`palindrome.py`)<br>3. **Password Generator** (`password_gen.py`)<br>4. **Currency Converter** (`currency.py`) | Error Handling (`try/except`), Input Sanitation, String Manipulation, `random` module. |
| **02** | Jan 21 | **Time & State** | 1. **Smart Timer** (`timer.py`, `timer_v2.py`)<br>2. **Guessing Game** (`guessing-game.py`, `guessing-gameV2.py`)<br>3. **To-Do List** (`to-do.py`) | `time.sleep`, `sys.stdout` (carriage return), List of Dictionaries, Global State persistence. |
| **03** | Jan 22 | **Game Logic** | 1. **Rock, Paper, Scissors** (`rsp.py`)<br>2. **Tic-Tac-Toe** (`tictactoe.py`)<br>3. **Adventure Engine** (`adventure.py`, `adventure-oop.py`) | 2D Arrays (Grids), Object-Oriented Programming (Classes/Objects), Complex Control Flow. |
# Day 4: File Operations & Automation 📂

**Date:** January 23, 2026  
**Focus:** Filesystem manipulation, handling binary data, and external library integrations.

## 📝 Projects Overview

Today's focus shifted from logic to **Utility**. These scripts interact with the Operating System to automate tedious tasks like renaming files, backing up data, and downloading media.

### 1. Universal Video Downloader (`video_downloader.py`)
A powerful CLI tool to scrape and download videos from major platforms (YouTube, TikTok, X, etc.).
* **Library:** `yt-dlp`
* **Key Logic:** Scrapes video metadata (Title, Views) before downloading. Handles stream extraction and file naming automatically.
* **Features:** User confirmation, progress tracking, and "best quality" auto-selection.

### 2. Bulk File Renamer (`renamer.py`)
Cleans up messy directories by renaming all files to a consistent format (e.g., `Holiday_1.jpg`, `Holiday_2.jpg`).
* **Library:** `os`
* **Key Logic:** Iterates through a directory, sorts files, and applies a sequential naming index while preserving file extensions.

### 3. Auto Backup Script (`backup.py`)
Creates a timestamped copy of an entire project folder.
* **Library:** `shutil`, `datetime`
* **Key Logic:** Uses `shutil.copytree` to recursively copy folder structures and appends `YYYY-MM-DD_HH-MM-SS` to the folder name to prevent overwrites.

### 4. PDF Merger (`pdf_merger.py`)
Combines multiple PDF documents into a single file.
* **Library:** `pypdf`
* **Key Logic:** Opens streams for multiple PDF files and appends them page-by-page into a `PdfWriter` object.

---

## ⚙️ Setup & Installation

Today's projects require external packages. Install them using pip:

```bash
pip install requests pypdf yt-dlp
---

## 🚀 How to Run

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/icedmist/midnight-commits.git](https://github.com/icedmist/midnight-commits.git)
   cd midnight-commits