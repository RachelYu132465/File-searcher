import sqlite3
import time

conn = sqlite3.connect("speed_test.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS test_log (id INTEGER PRIMARY KEY, data TEXT)")

# --- 測試 A：SSD 的地獄（Auto-Commit，沒有 Buffer 緩衝）---
print("開始測試 A：逐筆硬碟寫入...")
start_time = time.time()
for i in range(100000):
    cursor.execute("INSERT INTO test_log (data) VALUES ('SSD_Test')")
    conn.commit()  # 致命語法：每一次迴圈都強迫 SSD 整塊抹除與寫入！
print(f"測試 A 耗時: {time.time() - start_time:.2f} 秒")

# --- 測試 B：RAM 的魔法（Transaction， Dirty Pages 累積）---
print("開始測試 B：記憶體緩衝寫入...")
start_time = time.time()
for i in range(100000):
    cursor.execute("INSERT INTO test_log (data) VALUES ('RAM_Test')")
# 只有在迴圈結束後，才執行一次 commit
conn.commit()      # 魔法語法：在 RAM 裡累積 10 萬筆 Dirty Pages，最後一次性整批沖刷回硬碟
print(f"測試 B 耗時: {time.time() - start_time:.2f} 秒")

conn.close()