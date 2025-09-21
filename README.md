# FB Page Mange

A desktop tool for managing Facebook pages (accounts, pages, schedules, recycle bin, etc.).

## Project Overview
- Built using **Python 3.10+** and **PyQt6**
- Entry point: `main.py`
- Uses SQLite database (`pagedata.db`) for storage

## Folder Structure
- `database/` → DB connection, read, write
- `dialogs/` → popup dialogs (account, page, bulk edit, recycle bin, etc.)
- `handlers/` → logic controllers (main_handler, dialog_handler, menu_handler, etc.)
- `ui_components/` → reusable UI pieces (sortable_table, etc.)
- `utils/` → logger & settings handler
- `views/` → split and unified views
- `main.py` → start the app
- `requirements.txt` → install dependencies
- `README_FOR_AI.md` → extended project notes for AI
- `file_list.txt` → full file list for reference

## Installation
Install dependencies:
```powershell
pip install -r requirements.txt
