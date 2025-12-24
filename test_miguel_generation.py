#!/usr/bin/env python3
"""測試 Miguel 視頻生成"""

import json
import requests
import time

# 載入生成的 workflow
with open('/mnt/c/ai_projects/video-gen-factory/workflows/generated_test_api.json', 'r') as f:
    workflow = json.load(f)

print("提交 Miguel 視頻生成 workflow...")
print(f"節點數: {len(workflow)}")
print(f"幀數: {workflow['63']['inputs']['num_frames']}")
print(f"Prompt: {workflow['30']['inputs']['prompt'][:80]}...")
print("="*60)

# 提交到 ComfyUI
payload = {
    "prompt": workflow,
    "client_id": "miguel_test"
}

response = requests.post("http://127.0.0.1:8188/prompt", json=payload)

print(f"\nHTTP 狀態碼: {response.status_code}")

if response.status_code == 200:
    result = response.json()
    if 'prompt_id' in result:
        prompt_id = result['prompt_id']
        print(f"✅ 成功提交！Prompt ID: {prompt_id}")
        print(f"佇列編號: {result.get('number')}")

        # 監控進度
        print("\n監控生成進度...")
        print("="*60)

        start_time = time.time()
        last_status = None

        while True:
            try:
                queue_response = requests.get("http://127.0.0.1:8188/queue")
                queue = queue_response.json()

                running = queue.get('queue_running', [])
                pending = queue.get('queue_pending', [])

                status = f"{len(running)} running, {len(pending)} pending"

                if status != last_status:
                    elapsed = int(time.time() - start_time)
                    print(f"[{elapsed}s] {status}")
                    last_status = status

                # 檢查是否完成
                if len(running) == 0 and len(pending) == 0:
                    elapsed = int(time.time() - start_time)
                    print(f"\n✅ 生成完成！總耗時: {elapsed}秒 ({elapsed//60}分{elapsed%60}秒)")

                    # 檢查輸出檔案
                    print("\n檢查輸出檔案...")
                    import subprocess
                    result = subprocess.run(
                        ['ls', '-lht', '/mnt/c/ai_tools/comfyui/output/miguel_dancing_test*.mp4'],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        print(result.stdout)
                    else:
                        print("⚠️  找不到輸出檔案")
                    break

                time.sleep(5)

            except KeyboardInterrupt:
                print("\n⏸️  監控已停止")
                break

    elif 'error' in result:
        print(f"\n❌ 驗證錯誤: {result['error']}")
        if 'node_errors' in result:
            for node_id, error in result['node_errors'].items():
                print(f"\n節點 {node_id} 錯誤:")
                print(json.dumps(error, indent=2))
else:
    print(f"❌ 提交失敗")
    print(response.text)
