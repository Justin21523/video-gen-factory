#!/usr/bin/env python3
"""驗證 workflow 並獲取詳細錯誤訊息"""

import requests
import json

from vgf_paths import comfyui_url, workflow_path

# 載入生成的 workflow
with open(workflow_path("debug_last_submit.json"), 'r', encoding='utf-8') as f:
    data = json.load(f)

workflow = data.get('prompt', data)

print("檢查 workflow 結構...")

if isinstance(workflow, dict) and 'nodes' in workflow and 'links' in workflow:
    # UI workflow 格式
    print(f"格式: UI workflow")
    print(f"節點數量: {len(workflow.get('nodes', []))}")
    print(f"連結數量: {len(workflow.get('links', []))}")

    for node in workflow.get('nodes', []):
        node_id = node.get('id')
        node_type = node.get('type')
        print(f"\n節點 {node_id}: {node_type}")

        if 'widgets_values' in node:
            print(f"  widgets_values: {node['widgets_values']}")

        if 'inputs' in node:
            for inp in node['inputs']:
                if inp.get('link') is not None:
                    print(f"  輸入: {inp['name']} <- link {inp['link']}")
elif isinstance(workflow, dict):
    # API workflow 格式 (node_id -> {class_type, inputs})
    print("格式: API workflow")
    print(f"節點數量: {len(workflow)}")
    for node_id, node in sorted(workflow.items(), key=lambda kv: int(kv[0]) if str(kv[0]).isdigit() else str(kv[0])):
        class_type = node.get('class_type')
        inputs = node.get('inputs', {})
        print(f"\n節點 {node_id}: {class_type}")
        if isinstance(inputs, dict) and inputs:
            keys = ", ".join(sorted(inputs.keys()))
            print(f"  inputs: {keys}")
else:
    print("⚠️  無法辨識 workflow 格式")

# 嘗試使用 ComfyUI API 驗證
print("\n" + "="*60)
print("提交到 ComfyUI 進行驗證...")
print("="*60)

payload = {
    "prompt": workflow,
    "client_id": "validator"
}

try:
    response = requests.post(
        f"{comfyui_url()}/prompt",
        json=payload,
        headers={"Content-Type": "application/json"}
    )

    print(f"\nHTTP 狀態碼: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"\nResponse body:")
    print(response.text)

    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ 驗證成功!")
        if 'prompt_id' in result:
            print(f"Prompt ID: {result['prompt_id']}")
        print(json.dumps(result, indent=2))
    else:
        print(f"\n❌ 驗證失敗")

except Exception as e:
    print(f"\n❌ 例外: {e}")
    import traceback
    traceback.print_exc()
