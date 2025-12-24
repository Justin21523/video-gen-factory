#!/usr/bin/env python3
"""SVD 批量視頻生成系統 - 為所有角色生成 420 個視頻"""

import os
import json
import random
import time
import requests
import shutil
from pathlib import Path
from typing import List, Dict, Any
from svd_workflow_generator import SVDWorkflowGenerator


class SVDBatchGenerator:
    """SVD 批量生成器"""

    def __init__(
        self,
        comfyui_url: str = "http://127.0.0.1:8188",
        data_dir: str = "/mnt/data/ai_data/synthetic_lora_data/generated_data",
        comfyui_input_dir: str = "/mnt/c/ai_tools/comfyui/input",
        output_dir: str = "/mnt/c/ai_tools/comfyui/output"
    ):
        self.comfyui_url = comfyui_url
        self.data_dir = data_dir
        self.comfyui_input_dir = comfyui_input_dir
        self.output_dir = output_dir
        self.generator = SVDWorkflowGenerator()

        # 14 個角色列表
        self.characters = [
            'miguel', 'alberto', 'luca', 'giulia',
            'ian_lightfoot', 'barley_lightfoot',
            'russell', 'elio',
            'miguel_child', 'alberto_human', 'luca_human',
            'giulia_summer', 'ian_confident', 'elio_space'
        ]

        # 圖片類別
        self.categories = ['action', 'expression', 'pose']

        # 每個類別選取的圖片數量
        self.images_per_category = 10

    def get_character_images(self, character: str) -> Dict[str, List[str]]:
        """
        獲取角色的隨機圖片

        返回: {
            'action': [圖片路徑列表],
            'expression': [圖片路徑列表],
            'pose': [圖片路徑列表]
        }
        """
        character_images = {}

        for category in self.categories:
            category_dir = os.path.join(self.data_dir, character, category, 'images')

            if not os.path.exists(category_dir):
                print(f"⚠️  目錄不存在: {category_dir}")
                character_images[category] = []
                continue

            # 獲取所有 PNG 圖片
            all_images = [
                os.path.join(category_dir, f)
                for f in os.listdir(category_dir)
                if f.endswith('.png')
            ]

            # 隨機選取指定數量的圖片
            if len(all_images) > self.images_per_category:
                selected = random.sample(all_images, self.images_per_category)
            else:
                selected = all_images

            character_images[category] = sorted(selected)

            print(f"  {category}: {len(all_images)} 張 → 選取 {len(selected)} 張")

        return character_images

    def copy_image_to_comfyui(self, image_path: str) -> str:
        """
        複製圖片到 ComfyUI input 目錄

        返回: ComfyUI 中的圖片檔名
        """
        image_name = os.path.basename(image_path)
        dest_path = os.path.join(self.comfyui_input_dir, image_name)

        # 如果檔案已存在且相同，跳過
        if os.path.exists(dest_path):
            if os.path.getsize(image_path) == os.path.getsize(dest_path):
                return image_name

        shutil.copy2(image_path, dest_path)
        return image_name

    def generate_video(
        self,
        character: str,
        category: str,
        image_path: str,
        index: int,
        motion_level: str = "medium",
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        為單張圖片生成視頻

        參數:
            character: 角色名稱
            category: 類別 (action/expression/pose)
            image_path: 圖片路徑
            index: 圖片索引
            motion_level: 運動級別 (small/medium/large)
            dry_run: 是否只是測試模式
        """
        # 運動級別映射
        motion_map = {
            'small': 80,      # 微小運動
            'medium': 127,    # 中等運動（默認）
            'large': 180      # 較大運動
        }
        motion_bucket_id = motion_map.get(motion_level, 127)

        # 為不同類別設置不同的運動級別
        if category == 'action':
            motion_bucket_id = 180  # 動作場景用較大運動
        elif category == 'expression':
            motion_bucket_id = 80   # 表情場景用微小運動
        else:  # pose
            motion_bucket_id = 127  # 姿勢場景用中等運動

        # 複製圖片到 ComfyUI
        image_name = self.copy_image_to_comfyui(image_path)

        # 生成輸出前綴
        output_prefix = f"{character}_{category}_{index:03d}"

        # 生成隨機種子
        seed = random.randint(0, 2**32 - 1)

        print(f"\n{'[DRY RUN] ' if dry_run else ''}生成視頻:")
        print(f"  角色: {character}")
        print(f"  類別: {category}")
        print(f"  圖片: {image_name}")
        print(f"  輸出: {output_prefix}")
        print(f"  運動級別: {motion_level} (bucket_id={motion_bucket_id})")
        print(f"  種子: {seed}")

        if dry_run:
            return {
                'character': character,
                'category': category,
                'image': image_name,
                'output_prefix': output_prefix,
                'motion_bucket_id': motion_bucket_id,
                'seed': seed
            }

        # 生成 workflow
        workflow = self.generator.generate_workflow(
            input_image=image_name,
            output_prefix=output_prefix,
            motion_bucket_id=motion_bucket_id,
            seed=seed,
            width=1024,
            height=576,
            video_frames=25,
            fps=16
        )

        # 提交到 ComfyUI
        payload = {
            "prompt": workflow,
            "client_id": f"svd_batch_{character}"
        }

        response = requests.post(f"{self.comfyui_url}/prompt", json=payload)

        if response.status_code == 200:
            result = response.json()
            if 'prompt_id' in result:
                print(f"✅ 提交成功！Prompt ID: {result['prompt_id']}")
                return {
                    'success': True,
                    'prompt_id': result['prompt_id'],
                    'character': character,
                    'category': category,
                    'output_prefix': output_prefix
                }
            else:
                print(f"❌ 提交失敗: {result}")
                return {'success': False, 'error': result}
        else:
            print(f"❌ HTTP 錯誤: {response.status_code}")
            return {'success': False, 'error': response.text}

    def wait_for_completion(self, timeout: int = 3600):
        """等待所有任務完成"""
        print("\n⏳ 等待生成完成...")
        start_time = time.time()
        last_status = None

        while True:
            try:
                response = requests.get(f"{self.comfyui_url}/queue")
                queue = response.json()

                running = queue.get('queue_running', [])
                pending = queue.get('queue_pending', [])

                status = f"{len(running)} 執行中, {len(pending)} 等待中"

                if status != last_status:
                    elapsed = int(time.time() - start_time)
                    print(f"[{elapsed}s] {status}")
                    last_status = status

                # 檢查是否完成
                if len(running) == 0 and len(pending) == 0:
                    elapsed = int(time.time() - start_time)
                    print(f"\n✅ 全部完成！總耗時: {elapsed}秒 ({elapsed//60}分{elapsed%60}秒)")
                    break

                # 超時檢查
                if time.time() - start_time > timeout:
                    print(f"\n⚠️  超時 ({timeout}秒)！還有任務未完成。")
                    break

                time.sleep(5)

            except KeyboardInterrupt:
                print("\n⏸️  監控已停止")
                break
            except Exception as e:
                print(f"⚠️  錯誤: {e}")
                time.sleep(5)

    def batch_generate_all(
        self,
        dry_run: bool = False,
        characters: List[str] = None,
        max_videos: int = None
    ):
        """
        批量生成所有視頻

        參數:
            dry_run: 是否只是測試模式（不實際提交）
            characters: 要處理的角色列表（None 表示全部）
            max_videos: 最大生成視頻數量（用於測試）
        """
        if characters is None:
            characters = self.characters

        total_videos = 0
        successful_videos = 0
        failed_videos = 0

        print("=" * 80)
        print("🎬 SVD 批量視頻生成系統")
        print("=" * 80)
        print(f"角色數量: {len(characters)}")
        print(f"每個角色預計: {self.images_per_category * len(self.categories)} 張圖片")
        print(f"預計總視頻數: {len(characters) * self.images_per_category * len(self.categories)}")
        print(f"模式: {'測試模式（不實際提交）' if dry_run else '正式生成'}")
        print("=" * 80)

        for char_idx, character in enumerate(characters, 1):
            print(f"\n{'='*80}")
            print(f"處理角色 [{char_idx}/{len(characters)}]: {character}")
            print(f"{'='*80}")

            # 獲取角色圖片
            character_images = self.get_character_images(character)

            # 處理每個類別
            for category in self.categories:
                images = character_images.get(category, [])

                if not images:
                    print(f"⚠️  {category}: 沒有圖片")
                    continue

                print(f"\n處理類別: {category} ({len(images)} 張圖片)")

                for img_idx, image_path in enumerate(images, 1):
                    # 檢查是否達到最大數量
                    if max_videos and total_videos >= max_videos:
                        print(f"\n⚠️  已達到最大視頻數量 ({max_videos})，停止生成")
                        return {
                            'total': total_videos,
                            'successful': successful_videos,
                            'failed': failed_videos
                        }

                    # 生成視頻
                    result = self.generate_video(
                        character=character,
                        category=category,
                        image_path=image_path,
                        index=img_idx,
                        dry_run=dry_run
                    )

                    total_videos += 1

                    if not dry_run:
                        if result.get('success'):
                            successful_videos += 1
                            # 每提交一個視頻後短暫等待，避免過載
                            time.sleep(2)
                        else:
                            failed_videos += 1

                    # 進度報告
                    print(f"  進度: {total_videos} / ~{len(characters) * 30}")

        print("\n" + "=" * 80)
        print("📊 批量生成完成統計")
        print("=" * 80)
        print(f"總視頻數: {total_videos}")
        if not dry_run:
            print(f"成功: {successful_videos}")
            print(f"失敗: {failed_videos}")
            print(f"成功率: {successful_videos/total_videos*100:.1f}%")
        print("=" * 80)

        return {
            'total': total_videos,
            'successful': successful_videos,
            'failed': failed_videos
        }


def main():
    """主程序"""
    import argparse

    parser = argparse.ArgumentParser(description='SVD 批量視頻生成')
    parser.add_argument('--dry-run', action='store_true', help='測試模式，不實際提交')
    parser.add_argument('--characters', nargs='+', help='指定要處理的角色')
    parser.add_argument('--max-videos', type=int, help='最大生成視頻數量（用於測試）')
    parser.add_argument('--wait', action='store_true', help='等待所有任務完成')

    args = parser.parse_args()

    # 創建生成器
    generator = SVDBatchGenerator()

    # 執行批量生成
    stats = generator.batch_generate_all(
        dry_run=args.dry_run,
        characters=args.characters,
        max_videos=args.max_videos
    )

    # 等待完成
    if args.wait and not args.dry_run:
        generator.wait_for_completion()


if __name__ == '__main__':
    main()
