## Ultra-Fast File Searcher ⚡
1. Improve the efficiency of local file searching. Compared to the native Windows search (the search bar at File Explorer), this tool finds files up to **6x faster**.

2. The tool utilizes SQLite's dual fuzzy matching (`LIKE`) to filter results based on both the specified directory path and the keyword.

## Quick Start
1. Place `file_indexer.exe`, `searcher.exe`, and `file_index.db` in the same directory.
2. Run `file_indexer.exe` to select a target folder and build the initial database.
3. Run `searcher.exe` to instantly find your files, no need to include file extension.

## For Beginner
* Open 'dist' file, there is exe which can run the program directly.
  
## What It Can Find (Success Scenarios)✅ 
* Search:**`.py`** Result: **`main.py`、 `python`**(Fuzzy Matching);
* **Directory Support:** You can search for folder names directly.
* **Case-Insensitive.** 

## Core Logic: B-Tree over NTFS
Traditional Windows search relies on real-time traversal of the NTFS file system or the heavy built-in Windows indexer, which can be sluggish and resource-intensive.

This tool bypasses NTFS entirely during the search phase. `file_indexer` captures a lightweight snapshot of your directory tree and structures it inside a local SQLite database. By applying a **B-Tree index** (`CREATE INDEX`) directly on the filenames, `searcher` retrieves matches with **O(log N) time complexity**. It effectively replaces heavy NTFS I/O operations with lightning-fast database queries.

## Features
* **Extreme Speed**: Uses SQLite with WAL (Write-Ahead Logging) mode and B-Tree indexing for millisecond-level path retrieval.
* **Independent Execution**: Separated into two lightweight modules (Indexer and Searcher) to ensure search performance isn't dragged down by background scanning.
* **GUI Integration**: Clean and native-feeling folder selection and search interface built with Tkinter.
* **Safe Scanning**: Built-in error handling to gracefully skip locked or system-protected files without crashing.

## How It Works
The project consists of two main components:
1. `file_indexer.exe`: Scans your target directory and builds a snapshot of all files into `file_index.db`.
2. `searcher.exe`: Reads the database to provide instant fuzzy search results based on your keywords.


## Why A File Might Be Missing (Common Causes)⚠️
* **Static Snapshot Dependency:** The searcher reads from `file_index.db`, which is a static snapshot. Any files created, renamed, or moved **after** you last ran `file_indexer.exe` will not be found. Re-run the indexer to refresh the snapshot.
* **Result Query Limit:** By default, the database query might be capped (e.g., `LIMIT 20`) to ensure extreme performance. If a file is the 21st match, it will be hidden.
* **Permission Blocks:** System-protected files or files currently locked by other applications are intentionally skipped during the indexing phase to prevent program crashes.
* **Typographical Errors in Path/Keyword:** Extra trailing spaces in your keyword (e.g., `" .txt"`) or incorrect slash formats in the search path will cause the SQL strict matching to fail.

## Notes
* Recursive Path Coverage: If you set the search path to `C:\Project`, it will match all files nested deep within its subdirectories (e.g., `C:\Project\A\B\test.txt`).
  
