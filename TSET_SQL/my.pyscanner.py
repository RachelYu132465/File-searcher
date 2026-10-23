import os
import time

# 設定你要掃描的目標資料夾 (先用你目前的專案資料夾測試)
# 字串前面的 r 代表 Raw String，這樣 Windows 的反斜線 \ 就不會報錯
target_folder = r"C:\Users\User\Desktop\search_friend_Line_app"

print(f"啟動作業系統感測器，目標：{target_folder}")
print("-" * 50)

start_time = time.time()
file_count = 0

# os.walk 會回傳三個東西：目前所在的資料夾路徑 (root)、裡面的子資料夾 (dirs)、裡面的檔案 (files)
for root, dirs, files in os.walk(target_folder):
    for filename in files:
        file_count += 1

        # 組合出檔案的「絕對實體路徑」
        full_path = os.path.join(root, filename)

        # 呼叫 OS 取得檔案的實體大小 (Bytes)
        file_size = os.path.getsize(full_path)

        # 印出前 10 個檔案來看看就好，以免畫面洗版
        if file_count <= 10:
            print(f"找到實體檔案: {filename} (大小: {file_size} Bytes)")

print("-" * 50)
print(f"掃描完畢！共發現 {file_count} 個實體檔案。")
print(f"OS 掃描耗時: {time.time() - start_time:.4f} 秒")