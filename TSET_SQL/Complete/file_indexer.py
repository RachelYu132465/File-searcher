import os
import time
import sqlite3
import tkinter as tk
from tkinter import filedialog

# Hide the main Tkinter window
root = tk.Tk()
root.withdraw()

# Pop up a native Windows folder selection dialog for the user to choose the target path
print("[*] Opening folder selection dialog...")
target_folder = filedialog.askdirectory(title="Select Target Folder to Index")

if not target_folder:
    print("[-] No folder selected. Exiting program.")
    exit()

db_name = "file_index.db"

print(f"[*] Target folder to index: {target_folder}")
print(f"[*] Database name: {db_name}")

# Remove old database if it exists to ensure a fresh snapshot
if os.path.exists(db_name):
    os.remove(db_name)

# Initialize SQLite connection
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# Enable WAL mode and disable synchronous writing for extreme performance
cursor.execute("PRAGMA journal_mode = WAL;")
cursor.execute("PRAGMA synchronous = OFF;")

# Create the main files table
cursor.execute("""
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT,
    full_path TEXT,
    file_size INTEGER
);
""")

# Create a metadata table to store the indexed root directory range
cursor.execute("""
CREATE TABLE IF NOT EXISTS metadata (
    key TEXT PRIMARY KEY,
    value TEXT
);
""")
cursor.execute("INSERT OR REPLACE INTO metadata (key, value) VALUES ('target_folder', ?);", (target_folder,))
conn.commit()

print("[*] Starting deep scan of the target folder...")

start_time = time.time()
file_count = 0
error_count = 0
batch_data = []
batch_size = 5000  # Batch size for bulk database commits

# Traverse directory tree using os.walk
for root_dir, dirs, files in os.walk(target_folder):
    for filename in files:
        full_path = os.path.join(root_dir, filename)

        # Defensive mechanism against permission errors or locked system files
        try:
            file_size = os.path.getsize(full_path)
        except (PermissionError, OSError):
            error_count += 1
            continue

        batch_data.append((filename, full_path, file_size))
        file_count += 1

        # Perform batch commit when batch size is reached
        if len(batch_data) >= batch_size:
            cursor.executemany("INSERT INTO files (filename, full_path, file_size) VALUES (?, ?, ?);", batch_data)
            conn.commit()
            batch_data.clear()

# Insert remaining records
if batch_data:
    cursor.executemany("INSERT INTO files (filename, full_path, file_size) VALUES (?, ?, ?);", batch_data)
    conn.commit()

scan_end_time = time.time()
print(f"[+] Scan and write completed! Collected {file_count} files (skipped {error_count} protected files).")
print(f"[+] Total time: {scan_end_time - start_time:.4f} seconds")

# Build B-Tree index for logarithmic search speed
print("[*] Building B-Tree navigation index (CREATE INDEX)...")
index_start_time = time.time()
cursor.execute("CREATE INDEX idx_filename ON files (filename);")
conn.commit()
print(f"[+] Index built successfully! Time: {time.time() - index_start_time:.4f} seconds")

conn.close()
print("[+] Indexing finished. You can now run searcher.py!")