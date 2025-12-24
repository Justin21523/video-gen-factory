#!/usr/bin/env python3
"""測試 ComfyUI API 基本功能"""

import requests
import json

url = "http://127.0.0.1:8188"

print("測試 1: 檢查系統狀態...")
try:
    r = requests.get(f"{url}/system_stats")
    print(f"✅ 系統狀態 OK: {r.status_code}")
    stats = r.json()
    print(f"   ComfyUI 版本: {stats['system']['comfyui_version']}")
    print(f"   GPU: {stats['devices'][0]['name']}")
except Exception as e:
    print(f"❌ 失敗: {e}")

print("\n測試 2: 獲取佇列狀態...")
try:
    r = requests.get(f"{url}/queue")
    print(f"✅ 佇列狀態 OK: {r.status_code}")
    queue = r.json()
    print(f"   運行中: {len(queue.get('queue_running', []))}")
    print(f"   待處理: {len(queue.get('queue_pending', []))}")
except Exception as e:
    print(f"❌ 失敗: {e}")

print("\n測試 3: 獲取節點定義...")
try:
    r = requests.get(f"{url}/object_info")
    print(f"✅ 節點定義 OK: {r.status_code}")
    nodes = r.json()

    # 檢查關鍵節點是否存在
    key_nodes = [
        'LoadImage',
        'DownloadAndLoadCogVideoModel',
        'CogVideoTextEncode',
        'CogVideoSampler',
        'CogVideoDecode',
        'VHS_VideoCombine'
    ]

    print("   檢查關鍵節點:")
    for node_name in key_nodes:
        if node_name in nodes:
            print(f"      ✅ {node_name}")
        else:
            print(f"      ❌ {node_name} - 缺失！")

except Exception as e:
    print(f"❌ 失敗: {e}")

print("\n測試完成!")
