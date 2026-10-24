import os
import sqlite3
import time
import tkinter as tk
from tkinter import simpledialog, messagebox

db_name = "file_index.db"

# 隱藏主視窗
root = tk.Tk()
root.withdraw()

# 檢查資料庫是否存在
if not os.path.exists(db_name):
    messagebox.showerror("Error", "Database 'file_index.db' not found!\nPlease run 'indexer.exe' first.")
    exit()

conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# 取得初始掃描範圍
cursor.execute("SELECT value FROM metadata WHERE key = 'target_folder';")
row = cursor.fetchone()
if not row:
    messagebox.showerror("Error", "Metadata not found in database.")
    conn.close()
    exit()
indexed_root = row[0]

# 1. 讓使用者輸入搜尋路徑
search_path = simpledialog.askstring("Search Path", f"Enter search path (Indexed root: {indexed_root}):")
if not search_path:
    conn.close()
    exit()

# 2. 讓使用者輸入關鍵字
keyword = simpledialog.askstring("Search Keyword", "Enter keyword (e.g., .py, report, data):")
if not keyword:
    conn.close()
    exit()

# 執行無上限極速搜尋 (移除 LIMIT)
start_time = time.time()
search_pattern_path = f"{search_path.strip()}%"
search_pattern_keyword = f"%{keyword.strip()}%"

cursor.execute("""
    SELECT filename, full_path, file_size 
    FROM files 
    WHERE full_path LIKE ? AND filename LIKE ?;
""", (search_pattern_path, search_pattern_keyword))

results = cursor.fetchall()
end_time = time.time()
conn.close()

# 3. 匯出純文字檔與提示
if not results:
    messagebox.showinfo("Search Results", "No matching files found.")
else:
    elapsed_ms = (end_time - start_time) * 1000
    txt_filename = "search_results.txt"

    with open(txt_filename, "w", encoding="utf-8") as f:
        f.write(f"Found {len(results)} results (Query time: {elapsed_ms:.2f} ms):\n\n")
        for row in results:
            size_mb = row[2] / (1024 * 1024)
            f.write(f"File: {row[0]}\n")
            f.write(f"Path: {row[1]}\n")
            f.write(f"Size: {size_mb:.2f} MB\n")
            f.write("-" * 50 + "\n")

    full_txt_path = os.path.abspath(txt_filename)
    messagebox.showinfo(
        "Search Results",
        f"Found {len(results)} relevant data!\n\nThe results are saved at:\n{full_txt_path}"
    )

    # 自動使用記事本打開結果，方便直接全選或複製
    os.startfile(txt_filename)