#!/usr/bin/env python3
"""測試 SVD 批量生成系統設置"""

import os
import sys
import requests
from pathlib import Path


def test_comfyui_connection():
    """測試 ComfyUI 連接"""
    print("\n1️⃣  測試 ComfyUI 連接...")
    try:
        response = requests.get("http://127.0.0.1:8188/system_stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print("   ✅ ComfyUI 連接成功")
            print(f"   GPU: {stats['system']['cuda'].get('gpu_name', 'Unknown')}")
            print(f"   VRAM: {stats['system']['cuda'].get('vram_total', 0) / 1024:.1f} GB")
            return True
        else:
            print(f"   ❌ ComfyUI 響應錯誤: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ 無法連接到 ComfyUI: {e}")
        print("   提示: 請先啟動 ComfyUI (python main.py --port 8188)")
        return False


def test_svd_model():
    """檢查 SVD 模型是否存在"""
    print("\n2️⃣  檢查 SVD 模型...")
    model_paths = [
        "/mnt/c/ai_tools/comfyui/models/checkpoints/svd_xt_1_1.safetensors",
        "/mnt/c/ai_tools/comfyui/models/checkpoints/svd_xt.safetensors",
        "/mnt/c/ai_tools/comfyui/models/checkpoints/svd.safetensors"
    ]

    for model_path in model_paths:
        if os.path.exists(model_path):
            size_gb = os.path.getsize(model_path) / 1024**3
            print(f"   ✅ 找到 SVD 模型: {model_path}")
            print(f"   大小: {size_gb:.2f} GB")
            return True

    print("   ❌ 未找到 SVD 模型")
    print("   請下載模型:")
    print("   huggingface-cli download stabilityai/stable-video-diffusion-img2vid-xt-1-1")
    return False


def test_character_data():
    """檢查角色圖片數據"""
    print("\n3️⃣  檢查角色圖片數據...")
    data_dir = "/mnt/data/ai_data/synthetic_lora_data/generated_data"

    if not os.path.exists(data_dir):
        print(f"   ❌ 數據目錄不存在: {data_dir}")
        return False

    characters = [
        'miguel', 'alberto', 'luca', 'giulia',
        'ian_lightfoot', 'barley_lightfoot',
        'russell', 'elio'
    ]

    total_images = 0
    found_chars = 0

    for char in characters:
        char_dir = os.path.join(data_dir, char)
        if os.path.exists(char_dir):
            found_chars += 1
            char_images = 0
            for category in ['action', 'expression', 'pose']:
                img_dir = os.path.join(char_dir, category, 'images')
                if os.path.exists(img_dir):
                    images = [f for f in os.listdir(img_dir) if f.endswith('.png')]
                    char_images += len(images)
            total_images += char_images
            if char_images > 0:
                print(f"   ✅ {char}: {char_images} 張圖片")

    if found_chars > 0:
        print(f"\n   總計: {found_chars} 個角色, {total_images} 張圖片")
        return True
    else:
        print("   ❌ 未找到角色數據")
        return False


def test_workflow_generator():
    """測試 workflow 生成器"""
    print("\n4️⃣  測試 workflow 生成器...")
    try:
        from svd_workflow_generator import SVDWorkflowGenerator

        generator = SVDWorkflowGenerator()
        workflow = generator.generate_workflow(
            input_image="test.png",
            output_prefix="test"
        )

        if '1' in workflow and workflow['1']['class_type'] == 'ImageOnlyCheckpointLoader':
            print("   ✅ Workflow 生成器工作正常")
            print(f"   節點數: {len(workflow)}")
            return True
        else:
            print("   ❌ Workflow 格式錯誤")
            return False
    except Exception as e:
        print(f"   ❌ Workflow 生成器錯誤: {e}")
        return False


def test_directories():
    """檢查必要的目錄"""
    print("\n5️⃣  檢查必要目錄...")
    dirs_to_check = {
        'ComfyUI input': '/mnt/c/ai_tools/comfyui/input',
        'ComfyUI output': '/mnt/c/ai_tools/comfyui/output',
        'Workflow templates': '/mnt/c/ai_projects/video-gen-factory/workflows'
    }

    all_exist = True
    for name, path in dirs_to_check.items():
        if os.path.exists(path):
            print(f"   ✅ {name}: {path}")
        else:
            print(f"   ❌ {name} 不存在: {path}")
            all_exist = False

    return all_exist


def main():
    """主測試程序"""
    print("=" * 80)
    print("🔍 SVD 批量生成系統 - 設置測試")
    print("=" * 80)

    tests = [
        ("ComfyUI 連接", test_comfyui_connection),
        ("SVD 模型", test_svd_model),
        ("角色數據", test_character_data),
        ("Workflow 生成器", test_workflow_generator),
        ("目錄結構", test_directories)
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"   ❌ 測試失敗: {e}")
            results[test_name] = False

    print("\n" + "=" * 80)
    print("📊 測試結果總結")
    print("=" * 80)

    passed = sum(1 for r in results.values() if r)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{status} - {test_name}")

    print(f"\n通過率: {passed}/{total} ({passed/total*100:.0f}%)")

    if passed == total:
        print("\n🎉 所有測試通過！系統已準備就緒。")
        print("\n下一步:")
        print("  1. 測試單個視頻: python svd_batch_generate.py --characters miguel --max-videos 1 --wait")
        print("  2. 批量生成: python svd_batch_generate.py --wait")
        return 0
    else:
        print("\n⚠️  部分測試失敗，請先解決問題。")
        print("\n詳細說明請參考: SVD_BATCH_README.md")
        return 1


if __name__ == '__main__':
    sys.exit(main())
