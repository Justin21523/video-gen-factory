#!/usr/bin/env python3
"""驗證 workflow 並獲取詳細錯誤訊息"""

import requests
import json

# 載入生成的 workflow
with open('/mnt/c/ai_projects/video-gen-factory/workflows/debug_last_submit.json', 'r') as f:
    data = json.load(f)

workflow = data['prompt']

# 嘗試驗證每個節點
print("檢查 workflow 結構...")
print(f"節點數量: {len(workflow['nodes'])}")
print(f"連結數量: {len(workflow['links'])}")

# 檢查每個節點的必要欄位
for node in workflow['nodes']:
    node_id = node.get('id')
    node_type = node.get('type')
    print(f"\n節點 {node_id}: {node_type}")

    # 檢查是否有 widgets_values
    if 'widgets_values' in node:
        print(f"  widgets_values: {node['widgets_values']}")

    # 檢查輸入連結
    if 'inputs' in node:
        for inp in node['inputs']:
            if inp.get('link') is not None:
                print(f"  輸入: {inp['name']} <- link {inp['link']}")

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
        "http://127.0.0.1:8188/prompt",
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
