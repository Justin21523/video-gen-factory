#!/usr/bin/env python3
"""視頻放大工具 - 使用 Real-ESRGAN 4x 放大"""

import os
import json
import requests
import time
import shutil
from pathlib import Path

from vgf_paths import comfyui_url as default_comfyui_url, workflow_path


class VideoUpscaler:
    """視頻放大器"""

    def __init__(
        self,
        comfyui_url: str | None = None,
        template_path: str | None = None,
        comfyui_input_dir: str | None = None,
        comfyui_output_dir: str | None = None,
    ):
        self.comfyui_url = (comfyui_url or default_comfyui_url()).rstrip("/")
        self.comfyui_input_dir = comfyui_input_dir or os.environ.get("COMFYUI_INPUT_DIR", "/mnt/c/ai_tools/comfyui/input")
        self.output_dir = comfyui_output_dir or os.environ.get("COMFYUI_OUTPUT_DIR", "/mnt/c/ai_tools/comfyui/output")

        template = workflow_path(template_path or "video_upscale_template.json")
        with open(template, 'r', encoding='utf-8') as f:
            self.template = json.load(f)

        print(f"✓ 載入視頻放大 workflow 模板")

    def copy_video_to_comfyui(self, video_path: str) -> str:
        """複製視頻到 ComfyUI input 目錄"""
        video_name = os.path.basename(video_path)
        dest_path = os.path.join(self.comfyui_input_dir, video_name)

        if os.path.exists(dest_path):
            os.remove(dest_path)

        shutil.copy2(video_path, dest_path)
        return video_name

    def upscale_video(
        self,
        video_path: str,
        output_prefix: str = "upscaled",
        upscale_strategy: str = "2x+2x",  # "2x+2x" 或 "4x" 或 "2x"
        output_fps: int = 60,
        output_crf: int = 15
    ) -> dict:
        """
        放大單個視頻

        Args:
            upscale_strategy: 放大策略
                - "2x+2x": 分兩階段放大（推薦，避免OOM）
                - "4x": 一次性4x放大（需要大量VRAM）
                - "2x": 僅2x放大
        """

        # 複製視頻到 ComfyUI
        video_name = self.copy_video_to_comfyui(video_path)

        # 根據策略選擇模型
        strategy_config = {
            "2x+2x": {
                "first_model": "RealESRGAN_x2plus.pth",
                "second_model": "RealESRGAN_x2plus.pth",
                "stages": 2,
                "description": "分階段 2x+2x = 4x（記憶體友好）"
            },
            "4x": {
                "first_model": "RealESRGAN_x4plus_anime_6B.pth",
                "second_model": None,
                "stages": 1,
                "description": "一次性 4x 放大（高 VRAM 需求）"
            },
            "2x": {
                "first_model": "RealESRGAN_x2plus.pth",
                "second_model": None,
                "stages": 1,
                "description": "2x 放大"
            }
        }

        config = strategy_config.get(upscale_strategy, strategy_config["2x+2x"])

        print(f"\n放大視頻: {video_name}")
        print(f"  策略: {config['description']}")
        print(f"  輸出前綴: {output_prefix}")
        print(f"  輸出 fps: {output_fps}")

        if config["stages"] == 2:
            # 分兩階段放大
            return self._upscale_two_stage(
                video_name, output_prefix,
                config["first_model"], config["second_model"],
                output_fps, output_crf
            )
        else:
            # 單階段放大
            return self._upscale_single_stage(
                video_name, output_prefix,
                config["first_model"],
                output_fps, output_crf
            )

    def _upscale_single_stage(
        self, video_name: str, output_prefix: str,
        model: str, output_fps: int, output_crf: int
    ) -> dict:
        """單階段放大"""
        workflow = self.template.copy()
        workflow['1']['inputs']['video'] = video_name
        workflow['2']['inputs']['model_name'] = model
        workflow['4']['inputs']['frame_rate'] = output_fps
        workflow['4']['inputs']['filename_prefix'] = output_prefix
        workflow['4']['inputs']['crf'] = output_crf

        return self._submit_workflow(workflow, output_prefix)

    def _upscale_two_stage(
        self, video_name: str, output_prefix: str,
        first_model: str, second_model: str,
        output_fps: int, output_crf: int
    ) -> dict:
        """分兩階段放大（2x + 2x = 4x）"""

        # 第一階段：2x 放大
        print("  📊 第一階段：2x 放大")
        stage1_prefix = f"{output_prefix}_stage1_2x"

        workflow1 = self.template.copy()
        workflow1['1']['inputs']['video'] = video_name
        workflow1['2']['inputs']['model_name'] = first_model
        workflow1['4']['inputs']['frame_rate'] = output_fps
        workflow1['4']['inputs']['filename_prefix'] = stage1_prefix
        workflow1['4']['inputs']['crf'] = output_crf

        result1 = self._submit_workflow(workflow1, stage1_prefix)

        if not result1.get('success'):
            return result1

        # 等待第一階段完成
        print("  ⏳ 等待第一階段完成...")
        self.wait_for_completion(timeout=1800)  # 30分鐘

        # 第二階段：再 2x 放大
        print("  📊 第二階段：再 2x 放大（總共 4x）")

        # 找到第一階段輸出的視頻
        stage1_video = self._find_latest_output(stage1_prefix)
        if not stage1_video:
            return {'success': False, 'error': '找不到第一階段輸出'}

        workflow2 = self.template.copy()
        workflow2['1']['inputs']['video'] = os.path.basename(stage1_video)
        workflow2['2']['inputs']['model_name'] = second_model
        workflow2['4']['inputs']['frame_rate'] = output_fps
        workflow2['4']['inputs']['filename_prefix'] = output_prefix
        workflow2['4']['inputs']['crf'] = output_crf

        return self._submit_workflow(workflow2, output_prefix)

    def _submit_workflow(self, workflow: dict, output_prefix: str) -> dict:
        """提交 workflow 到 ComfyUI"""
        payload = {
            "prompt": workflow,
            "client_id": "video_upscaler"
        }

        response = requests.post(f"{self.comfyui_url}/prompt", json=payload)

        if response.status_code == 200:
            result = response.json()
            if 'prompt_id' in result:
                print(f"  ✅ 提交成功！Prompt ID: {result['prompt_id']}")
                return {
                    'success': True,
                    'prompt_id': result['prompt_id'],
                    'output_prefix': output_prefix
                }
            else:
                print(f"  ❌ 提交失敗: {result}")
                return {'success': False, 'error': result}
        else:
            print(f"  ❌ HTTP 錯誤: {response.status_code}")
            return {'success': False, 'error': response.text}

    def _find_latest_output(self, prefix: str) -> str:
        """找到最新的輸出視頻"""
        output_dir = self.output_dir if hasattr(self, 'output_dir') else "/mnt/c/ai_tools/comfyui/output"

        matching_files = []
        for f in os.listdir(output_dir):
            if f.startswith(prefix) and f.endswith('.mp4'):
                full_path = os.path.join(output_dir, f)
                matching_files.append((full_path, os.path.getmtime(full_path)))

        if not matching_files:
            return None

        # 返回最新的文件
        latest = max(matching_files, key=lambda x: x[1])
        return latest[0]

    def wait_for_completion(self, timeout: int = 3600):
        """等待放大完成"""
        print("\n⏳ 等待放大完成...")
        start_time = time.time()

        while True:
            try:
                response = requests.get(f"{self.comfyui_url}/queue")
                queue = response.json()

                running = queue.get('queue_running', [])
                pending = queue.get('queue_pending', [])

                if len(running) == 0 and len(pending) == 0:
                    elapsed = int(time.time() - start_time)
                    print(f"\n✅ 放大完成！耗時: {elapsed}秒")
                    break

                if time.time() - start_time > timeout:
                    print(f"\n⚠️  超時！")
                    break

                time.sleep(5)

            except KeyboardInterrupt:
                print("\n⏸️  已停止")
                break
            except Exception as e:
                print(f"⚠️  錯誤: {e}")
                time.sleep(5)


def main():
    """測試放大功能"""
    import argparse

    parser = argparse.ArgumentParser(description='視頻放大工具')
    parser.add_argument('--input', required=True, help='輸入視頻路徑')
    parser.add_argument('--output-prefix', default='upscaled', help='輸出前綴')
    parser.add_argument('--wait', action='store_true', help='等待完成')

    args = parser.parse_args()

    upscaler = VideoUpscaler()
    result = upscaler.upscale_video(
        video_path=args.input,
        output_prefix=args.output_prefix
    )

    if args.wait and result.get('success'):
        upscaler.wait_for_completion()


if __name__ == '__main__':
    main()
