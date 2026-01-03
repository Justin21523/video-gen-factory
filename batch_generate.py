#!/usr/bin/env python3
"""
批量視頻生成腳本
Batch Video Generation CLI for ComfyUI

使用方式:
  python batch_generate.py --character miguel                    # 生成 Miguel 的所有場景
  python batch_generate.py --character miguel --scene dancing    # 只生成特定場景
  python batch_generate.py --all                                 # 生成所有角色的所有場景
  python batch_generate.py --dry-run                             # 預覽不執行
"""

import argparse
import yaml
import json
import time
import requests
import sys
from pathlib import Path
from typing import List, Dict, Any
from workflow_generator import WorkflowGenerator
from vgf_paths import LEGACY_VGF_ROOT, comfyui_url as default_comfyui_url, project_root, rewrite_paths, workflow_path


class BatchGenerator:
    def __init__(self, comfyui_url: str | None = None):
        self.comfyui_url = comfyui_url or default_comfyui_url()
        self.client_id = "batch-video-generator"
        self.generator = WorkflowGenerator(
            template_path=str(workflow_path("miguel_cogvideox_base.json"))
        )

    def load_character_config(self, config_path: str) -> Dict[str, Any]:
        """載入角色配置檔"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def queue_workflow(self, workflow: Dict[str, Any]) -> str:
        """提交 workflow 到 ComfyUI"""
        workflow = rewrite_paths(workflow, {LEGACY_VGF_ROOT: str(project_root())})
        payload = {
            "prompt": workflow,
            "client_id": self.client_id
        }

        # Debug: 儲存 workflow 用於檢查
        debug_path = workflow_path("debug_last_submit.json")
        with open(debug_path, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=2)

        response = requests.post(f"{self.comfyui_url}/prompt", json=payload)

        try:
            result = response.json()
        except json.JSONDecodeError as e:
            print(f"❌ JSON 解析錯誤: {e}")
            print(f"Response text: {response.text[:500]}")
            raise Exception(f"無法解析 ComfyUI 回應: {e}")

        if 'prompt_id' in result:
            return result['prompt_id']
        else:
            raise Exception(f"提交失敗: {result}")

    def get_queue_status(self) -> Dict[str, Any]:
        """獲取當前佇列狀態"""
        response = requests.get(f"{self.comfyui_url}/queue")
        return response.json()

    def wait_for_completion(self, prompt_id: str, timeout: int = 600):
        """等待生成完成"""
        start_time = time.time()
        print(f"⏳ 等待生成完成 (prompt_id: {prompt_id})")

        while True:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"生成超時 ({timeout}秒)")

            queue_status = self.get_queue_status()

            # 檢查是否還在佇列中
            queue_running = queue_status.get('queue_running', [])
            queue_pending = queue_status.get('queue_pending', [])

            is_running = any(item[1] == prompt_id for item in queue_running)
            is_pending = any(item[1] == prompt_id for item in queue_pending)

            if not is_running and not is_pending:
                print("✅ 生成完成！")
                return True

            # 顯示進度
            elapsed = int(time.time() - start_time)
            print(f"⏳ 進行中... ({elapsed}秒)", end='\r')
            time.sleep(2)

    def generate_scene(
        self,
        character_config: Dict[str, Any],
        scene: Dict[str, Any],
        dry_run: bool = False
    ) -> str:
        """生成單個場景"""
        char_info = character_config['character']
        gen_settings = character_config['generation_settings']

        # 組合完整 prompt
        full_prompt = f"{char_info['base_description']}, {scene['prompt']}"

        # 組合完整 negative prompt（base_negative + scene negative）
        base_negative = char_info.get('base_negative', '')
        scene_negative = scene.get('negative', '')

        if base_negative and scene_negative:
            full_negative = f"{base_negative}, {scene_negative}"
        elif base_negative:
            full_negative = base_negative
        else:
            full_negative = scene_negative

        # 產生 workflow
        workflow = self.generator.generate_workflow(
            character_name=char_info['name'],
            prompt=full_prompt,
            negative_prompt=full_negative,
            reference_image=char_info['reference_images'][0],
            output_prefix=f"{gen_settings['output_prefix']}_{scene['id']}",
            seed=scene['seed'],
            steps=gen_settings['steps'],
            cfg=gen_settings['cfg'],
            width=gen_settings['width'],
            height=gen_settings['height']
        )

        if dry_run:
            print(f"\n[DRY RUN] 會生成以下內容:")
            print(f"  角色: {char_info['name']}")
            print(f"  場景: {scene['id']}")
            print(f"  Prompt: {full_prompt}")
            print(f"  輸出: {gen_settings['output_prefix']}_{scene['id']}.mp4")
            return None

        # 提交到 ComfyUI
        print(f"\n{'='*60}")
        print(f"🎬 開始生成: {char_info['name']} - {scene['id']}")
        print(f"{'='*60}")

        prompt_id = self.queue_workflow(workflow)
        print(f"✓ 已提交到佇列: {prompt_id}")

        # 等待完成
        self.wait_for_completion(prompt_id)

        return prompt_id

    def generate_character(
        self,
        character_name: str,
        scene_filter: str = None,
        dry_run: bool = False
    ):
        """生成單個角色的所有（或指定）場景"""
        config_path = project_root() / "characters" / f"{character_name}.yaml"

        if not config_path.exists():
            print(f"❌ 找不到角色配置: {config_path}")
            return

        print(f"\n📋 載入角色配置: {character_name}")
        config = self.load_character_config(str(config_path))

        scenes = config['character']['scenes']

        # 過濾場景
        if scene_filter:
            scenes = [s for s in scenes if scene_filter in s['id']]
            if not scenes:
                print(f"❌ 找不到符合的場景: {scene_filter}")
                return

        print(f"📊 共 {len(scenes)} 個場景待生成")

        # 逐個生成
        results = []
        for i, scene in enumerate(scenes, 1):
            print(f"\n[{i}/{len(scenes)}] 處理場景: {scene['id']}")
            try:
                prompt_id = self.generate_scene(config, scene, dry_run)
                results.append({
                    'scene': scene['id'],
                    'status': 'success',
                    'prompt_id': prompt_id
                })
            except Exception as e:
                print(f"❌ 生成失敗: {e}")
                results.append({
                    'scene': scene['id'],
                    'status': 'failed',
                    'error': str(e)
                })

        # 總結
        print(f"\n{'='*60}")
        print(f"📊 生成總結 - {character_name}")
        print(f"{'='*60}")
        success = sum(1 for r in results if r['status'] == 'success')
        failed = sum(1 for r in results if r['status'] == 'failed')
        print(f"✅ 成功: {success}")
        print(f"❌ 失敗: {failed}")
        print(f"{'='*60}\n")

    def generate_all(self, dry_run: bool = False):
        """生成所有角色的所有場景"""
        characters_dir = project_root() / "characters"
        config_files = list(characters_dir.glob("*.yaml"))

        print(f"\n📋 找到 {len(config_files)} 個角色配置")

        for config_file in config_files:
            character_name = config_file.stem
            self.generate_character(character_name, dry_run=dry_run)


def main():
    parser = argparse.ArgumentParser(
        description='批量生成角色視頻',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  %(prog)s --character miguel                    # 生成 Miguel 所有場景
  %(prog)s --character miguel --scene dancing    # 只生成 Miguel 跳舞場景
  %(prog)s --all                                 # 生成所有角色
  %(prog)s --all --dry-run                       # 預覽所有任務
        """
    )

    parser.add_argument(
        '--character', '-c',
        help='角色名稱 (例: miguel, alberto, luca)'
    )

    parser.add_argument(
        '--scene', '-s',
        help='場景 ID 過濾 (例: dancing, guitar)'
    )

    parser.add_argument(
        '--all', '-a',
        action='store_true',
        help='生成所有角色的所有場景'
    )

    parser.add_argument(
        '--dry-run', '-d',
        action='store_true',
        help='預覽模式，不實際執行生成'
    )

    parser.add_argument(
        '--url',
        default=default_comfyui_url(),
        help='ComfyUI 服務地址 (預設: $COMFYUI_URL)'
    )

    args = parser.parse_args()

    # 參數驗證
    if not args.all and not args.character:
        parser.print_help()
        print("\n❌ 錯誤: 請指定 --character 或 --all")
        sys.exit(1)

    # 建立生成器
    generator = BatchGenerator(comfyui_url=args.url)

    # 執行生成
    if args.all:
        generator.generate_all(dry_run=args.dry_run)
    else:
        generator.generate_character(
            character_name=args.character,
            scene_filter=args.scene,
            dry_run=args.dry_run
        )


if __name__ == '__main__':
    main()
