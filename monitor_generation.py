#!/usr/bin/env python3
"""監控視頻生成進度"""

import time
import requests
import sys

prompt_id = sys.argv[1] if len(sys.argv) > 1 else None

print("🎬 監控視頻生成進度...")
print(f"Prompt ID: {prompt_id}")
print("="*60)

start_time = time.time()
last_status = None

while True:
    try:
        # 獲取佇列狀態
        response = requests.get("http://127.0.0.1:8188/queue")
        queue = response.json()

        running = queue.get('queue_running', [])
        pending = queue.get('queue_pending', [])

        status = f"{len(running)} running, {len(pending)} pending"

        # 只在狀態改變時打印
        if status != last_status:
            elapsed = int(time.time() - start_time)
            print(f"[{elapsed}s] {status}")
            last_status = status

            # 如果有詳細資訊，顯示
            if running:
                for item in running:
                    if len(item) >= 2:
                        print(f"   ⏳ 處理中: {item[1]}")

        # 檢查是否完成
        if len(running) == 0 and len(pending) == 0:
            elapsed = int(time.time() - start_time)
            print(f"\n✅ 生成完成！總耗時: {elapsed}秒 ({elapsed//60}分{elapsed%60}秒)")
            break

        time.sleep(3)

    except KeyboardInterrupt:
        print("\n⏸️  監控已停止")
        break
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        time.sleep(5)
