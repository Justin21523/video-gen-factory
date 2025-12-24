#!/usr/bin/env python3
"""
Video Generation Factory - 一键运行脚本
使用 ComfyUI API 自动提交 workflow 并监控生成进度
"""

import json
import requests
import time
import sys
import os
from pathlib import Path

# ComfyUI API 配置
COMFYUI_URL = "http://localhost:8188"
WORKFLOW_PATH = "/mnt/c/ai_projects/video-gen-factory/workflows/miguel_animatediff_final.json"
OUTPUT_DIR = "/mnt/c/ai_projects/video-gen-factory/output_videos"

def load_workflow():
    """加载 workflow JSON 文件"""
    print("📂 加载 Workflow...")
    with open(WORKFLOW_PATH, 'r') as f:
        workflow = json.load(f)
    print(f"✅ Workflow 已加载: {Path(WORKFLOW_PATH).name}")
    return workflow

def queue_prompt(workflow):
    """提交 workflow 到 ComfyUI 队列"""
    print("\n🚀 提交生成任务到 ComfyUI...")

    payload = {
        "prompt": workflow,
        "client_id": "video-gen-factory"
    }

    try:
        response = requests.post(f"{COMFYUI_URL}/prompt", json=payload)
        response.raise_for_status()
        result = response.json()
        prompt_id = result.get('prompt_id')
        print(f"✅ 任务已提交! Prompt ID: {prompt_id}")
        return prompt_id
    except requests.exceptions.ConnectionError:
        print("❌ 错误: 无法连接到 ComfyUI 服务器")
        print("   请确保 ComfyUI 正在运行 (http://localhost:8188)")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 提交失败: {e}")
        sys.exit(1)

def get_queue_status():
    """获取队列状态"""
    try:
        response = requests.get(f"{COMFYUI_URL}/queue")
        response.raise_for_status()
        return response.json()
    except:
        return None

def get_history(prompt_id):
    """获取任务历史"""
    try:
        response = requests.get(f"{COMFYUI_URL}/history/{prompt_id}")
        response.raise_for_status()
        return response.json()
    except:
        return None

def monitor_progress(prompt_id):
    """监控生成进度"""
    print("\n⏳ 监控生成进度...")
    print("   (这可能需要几分钟，请耐心等待)\n")

    start_time = time.time()
    last_status = None

    while True:
        # 检查队列状态
        queue = get_queue_status()
        if queue:
            running = queue.get('queue_running', [])
            pending = queue.get('queue_pending', [])

            # 检查是否在运行中
            is_running = any(item[1] == prompt_id for item in running)
            is_pending = any(item[1] == prompt_id for item in pending)

            if is_running:
                status = "🔄 正在生成中..."
            elif is_pending:
                status = f"⏸️  排队中 (队列位置: {len(pending)})"
            else:
                # 检查是否完成
                history = get_history(prompt_id)
                if history and prompt_id in history:
                    elapsed = time.time() - start_time
                    print(f"\n✅ 生成完成! 耗时: {elapsed:.1f} 秒")
                    print(f"📁 输出位置: {OUTPUT_DIR}")
                    return True
                status = "⏳ 等待中..."

            if status != last_status:
                elapsed = time.time() - start_time
                print(f"[{elapsed:.0f}s] {status}")
                last_status = status

        time.sleep(2)

def check_comfyui_running():
    """检查 ComfyUI 是否运行"""
    print("🔍 检查 ComfyUI 服务器状态...")
    try:
        response = requests.get(f"{COMFYUI_URL}/system_stats", timeout=5)
        response.raise_for_status()
        stats = response.json()

        # 显示系统信息
        devices = stats.get('devices', [])
        if devices:
            device = devices[0]
            vram_total = device.get('vram_total', 0) / (1024**3)
            vram_free = device.get('vram_free', 0) / (1024**3)
            print(f"✅ ComfyUI 运行正常")
            print(f"   GPU: {device.get('name', 'Unknown')}")
            print(f"   VRAM: {vram_free:.1f}GB 可用 / {vram_total:.1f}GB 总计")
        return True
    except:
        print("❌ ComfyUI 未运行!")
        print("\n请先启动 ComfyUI:")
        print("   cd /mnt/c/ai_tools/comfyui")
        print("   conda activate ai_env")
        print("   python main.py --listen 0.0.0.0 --port 8188")
        return False

def main():
    print("=" * 60)
    print("🎬 Video Generation Factory - Pixar 风格动画生成")
    print("=" * 60)
    print()

    # 检查 ComfyUI 是否运行
    if not check_comfyui_running():
        sys.exit(1)

    print()

    # 加载 workflow
    workflow = load_workflow()

    # 提交任务
    prompt_id = queue_prompt(workflow)

    # 监控进度
    success = monitor_progress(prompt_id)

    if success:
        print("\n" + "=" * 60)
        print("🎉 生成完成!")
        print("=" * 60)
        print("\n下一步:")
        print("1. 查看输出视频:")
        print(f"   {OUTPUT_DIR}/miguel_pixar_sdxl_*.mp4")
        print("\n2. 如果需要调整参数, 修改 workflow 文件:")
        print(f"   {WORKFLOW_PATH}")
        print("\n3. 再次运行此脚本生成新视频:")
        print("   python run_generation.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        sys.exit(0)
