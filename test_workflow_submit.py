#!/usr/bin/env python3
"""測試 workflow 提交"""

import json
import requests

# 讀取原始 workflow
with open('/mnt/c/ai_projects/video-gen-factory/workflows/miguel_cogvideox_base.json', 'r') as f:
    workflow = json.load(f)

# 提交到 ComfyUI
payload = {
    "prompt": workflow,
    "client_id": "test_client"
}

print("提交 workflow 到 ComfyUI...")
response = requests.post("http://127.0.0.1:8188/prompt", json=payload)

print(f"Status code: {response.status_code}")
print(f"Response: {response.text[:1000]}")

if response.status_code == 200:
    result = response.json()
    if 'prompt_id' in result:
        print(f"\n✅ 成功! Prompt ID: {result['prompt_id']}")
    else:
        print(f"\n❌ 失敗: {result}")
else:
    print(f"\n❌ HTTP 錯誤: {response.status_code}")
    # 嘗試解析錯誤訊息
    try:
        error = response.json()
        print(f"錯誤詳情: {json.dumps(error, indent=2)}")
    except:
        pass
