import os
import time
import sqlite3

# 直接指向 C 槽根目錄
target_folder = r"C:\\"
db_name = "c_drive_index.db"

print(f"[*] 目標資料夾: {target_folder}")
print(f"[*] 資料庫名稱: {db_name}")

if os.path.exists(db_name):
    os.remove(db_name)

conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# 啟用高效能 WAL 模式與關閉同步（追求極限寫入速度）
cursor.execute("PRAGMA journal_mode = WAL;")
cursor.execute("PRAGMA synchronous = OFF;")

cursor.execute("""
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT,
    full_path TEXT,
    file_size INTEGER
);
""")
conn.commit()

print("[*] 正在對整顆 C 槽進行地毯式掃描（這可能需要幾十秒到幾分鐘，請耐心等候）...")

start_time = time.time()
file_count = 0
error_count = 0
batch_data = []
batch_size = 10000  # C 槽檔案多，把批次量放大到 10000 筆

# 啟動 OS 掃描管線
for root, dirs, files in os.walk(target_folder):
    for filename in files:
        full_path = os.path.join(root, filename)

        # 嚴格的防禦性機制：攔截所有系統拒絕、鎖定或路徑過長錯誤
        try:
            file_size = os.path.getsize(full_path)
        except (PermissionError, OSError):
            error_count += 1
            continue  # 直接跳過無法讀取的系統檔，不讓程式崩潰

        batch_data.append((filename, full_path, file_size))
        file_count += 1

        if len(batch_data) >= batch_size:
            cursor.executemany("INSERT INTO files (filename, full_path, file_size) VALUES (?, ?, ?);", batch_data)
            conn.commit()
            batch_data.clear()

# 寫入剩餘的尾數
if batch_data:
    cursor.executemany("INSERT INTO files (filename, full_path, file_size) VALUES (?, ?, ?);", batch_data)
    conn.commit()

scan_end_time = time.time()
print(f"[+] 掃描與寫入完成！成功收集 {file_count} 個檔案（略過 {error_count} 個系統保護檔）。")
print(f"[+] 總耗時: {scan_end_time - start_time:.4f} 秒")

# 建立 B-Tree 索引
print("[*] 正在為整顆 C 槽建構 B-Tree 導航網 (CREATE INDEX)...")
index_start_time = time.time()
cursor.execute("CREATE INDEX idx_filename ON files (filename);")
conn.commit()
print(f"[+] 索引建構完成！耗時: {time.time() - index_start_time:.4f} 秒")

# 測試極速查詢
print("-" * 50)
print("[*] 測試查詢：在整顆 C 槽中搜尋含有 '.exe' 的檔案...")
search_keyword = ".exe"
query_start = time.time()
cursor.execute("SELECT full_path FROM files WHERE filename LIKE ? LIMIT 5;", (f"%{search_keyword}%",))
results = cursor.fetchall()
query_end = time.time()

print(f"[*] 查詢耗時: {(query_end - query_start) * 1000:.4f} 毫秒")
print("[*] 搜尋結果前 5 筆：")
for row in results:
    print(f"  -> {row[0]}")

conn.close()