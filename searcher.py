import os
import sqlite3
import time
import tkinter as tk
from tkinter import simpledialog, messagebox
from tkinter import ttk
db_name = "file_index.db"

# Hide the main Tkinter root window
root = tk.Tk()
root.withdraw()

# Check if the database exists
if not os.path.exists(db_name):
    messagebox.showerror("Error", "Database 'file_index.db' not found!\nPlease run 'indexer.exe' first.")
    exit()

# Connect to database and retrieve the original indexed root path range
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

cursor.execute("SELECT value FROM metadata WHERE key = 'target_folder';")
row = cursor.fetchone()
if not row:
    messagebox.showerror("Error", "Metadata not found in database.")
    conn.close()
    exit()

indexed_root = row[0]

# Pop up an input dialog for the user to enter the search directory path
search_path = simpledialog.askstring(
    "Search Path",
    f"Enter the directory path you want to search in:\n(Indexed root: {indexed_root})"
)
if not search_path:
    conn.close()
    exit()

# Pop up an input dialog for the user to enter the search keyword
keyword = simpledialog.askstring(
    "Search Keyword",
    "Enter the keyword to search for (e.g., .py, filename):"
)
if not keyword:
    conn.close()
    exit()

# Normalize paths to ensure accurate string and boundary comparison
normalized_indexed = os.path.normpath(indexed_root).lower()
normalized_search = os.path.normpath(search_path.strip()).lower()

# Check if the user-specified search path is within the indexed range
try:
    common_path = os.path.commonpath([normalized_indexed, normalized_search])
    is_within_range = (common_path == normalized_indexed)
except ValueError:
    is_within_range = False

# Warning popup if the search path is outside the indexed directory scope
if not is_within_range:
    messagebox.showwarning(
        "Out of Range Warning",
        f"The search path is NOT within the indexed range!\n\nIndexed root: {indexed_root}"
    )
    conn.close()
    exit()

# Execute ultra-fast search
start_time = time.time()

search_pattern_path = f"{search_path.strip()}%"
search_pattern_keyword = f"%{keyword.strip()}%"


cursor.execute("""
    SELECT filename, full_path, file_size 
    FROM files 
    WHERE full_path LIKE ? AND filename LIKE ? 
    LIMIT 20;
""", (search_pattern_path, search_pattern_keyword))

results = cursor.fetchall()
end_time = time.time()
conn.close()

if not results:
    messagebox.showinfo("Search Results", "No matching files found.")
else:
    elapsed_ms = (end_time - start_time) * 1000
    txt_filename = "search_results.txt"

    # 寫入純文字檔
    with open(txt_filename, "w", encoding="utf-8") as f:
        f.write(f"Found {len(results)} results (Query time: {elapsed_ms:.2f} ms):\n\n")
        for row in results:
            size_mb = row[2] / (1024 * 1024)
            f.write(f"File: {row[0]}\n")
            f.write(f"Path: {row[1]}\n")
            f.write(f"Size: {size_mb:.2f} MB\n")
            f.write("-" * 50 + "\n")

    # 彈出視窗告知檔案路徑
    full_txt_path = os.path.abspath(txt_filename)
    messagebox.showinfo(
        "Search Results",
        f"Found {len(results)} relevant data!\n\nThe results are saved at:\n{full_txt_path}"
    )

    # (Windows 限定) 自動幫使用者用記事本打開這個 TXT 檔，方便直接複製
    os.startfile(txt_filename)