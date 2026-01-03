#!/usr/bin/env python3
"""測試 API 格式 workflow"""

import json
import requests

from vgf_paths import comfyui_url, workflow_path

# 載入 API 格式 workflow
with open(workflow_path("miguel_cogvideox_base_api.json"), 'r', encoding='utf-8') as f:
    api_workflow = json.load(f)

print(f"載入 workflow: {len(api_workflow)} 個節點")

# 提交到 ComfyUI
payload = {
    "prompt": api_workflow,
    "client_id": "test"
}

print("\n提交到 ComfyUI...")
response = requests.post(f"{comfyui_url()}/prompt", json=payload)

print(f"狀態碼: {response.status_code}")
print(f"回應: {response.text}")

if response.status_code == 200:
    result = response.json()
    if 'prompt_id' in result:
        print(f"\n✅ 成功！Prompt ID: {result['prompt_id']}")
    elif 'error' in result:
        print(f"\n❌ 錯誤: {result['error']}")
        if 'node_errors' in result:
            for node_id, error in result['node_errors'].items():
                print(f"   節點 {node_id}: {error}")
    else:
        print(f"\n結果: {json.dumps(result, indent=2)}")
