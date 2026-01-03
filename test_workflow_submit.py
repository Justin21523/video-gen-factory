#!/usr/bin/env python3
"""測試 workflow 提交"""

import json
import requests

from vgf_paths import comfyui_url, workflow_path

# 讀取原始 workflow
with open(workflow_path("miguel_cogvideox_base.json"), 'r', encoding='utf-8') as f:
    workflow = json.load(f)

# 提交到 ComfyUI
payload = {
    "prompt": workflow,
    "client_id": "test_client"
}

print("提交 workflow 到 ComfyUI...")
response = requests.post(f"{comfyui_url()}/prompt", json=payload)

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
