#!/usr/bin/env python3
"""
批量生成420个视频 - 两步流程
步骤1: SVD生成 (576×320, 快速)
步骤2: 独立Upscale (2x+2x画质提升)
"""

import os
import sys
import random
import time
import subprocess
import json
from pathlib import Path
from typing import List, Dict

from vgf_paths import project_root

# 设置AI_WAREHOUSE 3.0规范的环境变量
os.environ['HF_HOME'] = '/mnt/c/ai_cache/huggingface'
os.environ['TRANSFORMERS_CACHE'] = '/mnt/c/ai_cache/huggingface'
os.environ['TORCH_HOME'] = '/mnt/c/ai_cache/torch'
os.environ['XDG_CACHE_HOME'] = '/mnt/c/ai_cache'


class BatchVideoGenerator420:
    """420个视频批量生成器"""

    def __init__(
        self,
        input_base_dir: str = "/mnt/data/ai_data/synthetic_lora_data/generated_data",
        output_base_dir: str = "/mnt/data/videos/svd_420_batch",
        images_per_category: int = 10,
        motion_bucket_id: int = 80,
        guidance_scale: float = 3.5,
        steps: int = 20,
        enable_upscale: bool = True,
        dry_run: bool = False
    ):
        self.input_base_dir = input_base_dir
        self.output_base_dir = output_base_dir
        self.images_per_category = images_per_category
        self.motion_bucket_id = motion_bucket_id
        self.guidance_scale = guidance_scale
        self.steps = steps
        self.enable_upscale = enable_upscale
        self.dry_run = dry_run

        # 14个角色
        self.characters = [
            'miguel', 'alberto', 'luca', 'giulia',
            'ian_lightfoot', 'barley_lightfoot', 'russell', 'elio',
            'alberto_seamonster', 'luca_seamonster',
            'bryce', 'caleb', 'orion', 'tyler'
        ]

        # 3个类别
        self.categories = ['action', 'expression', 'pose']

        # 创建输出目录
        os.makedirs(output_base_dir, exist_ok=True)

    def get_character_images(self, character: str, category: str) -> List[str]:
        """获取角色指定类别的图片（随机选择10张）"""
        image_dir = os.path.join(
            self.input_base_dir,
            character,
            category,
            'images'
        )

        if not os.path.exists(image_dir):
            return []

        all_images = [
            os.path.join(image_dir, f)
            for f in os.listdir(image_dir)
            if f.endswith('.png')
        ]

        if len(all_images) > self.images_per_category:
            selected = random.sample(all_images, self.images_per_category)
        else:
            selected = all_images

        return sorted(selected)

    def generate_svd_video(
        self,
        input_image: str,
        output_path: str
    ) -> Dict:
        """步骤1: SVD生成基础视频"""

        cmd = [
            'python',
            str(project_root() / 'svd_pure_python.py'),
            '--input', input_image,
            '--output', output_path,
            '--motion', str(self.motion_bucket_id),
            '--guidance', str(self.guidance_scale),
            '--steps', str(self.steps),
            '--no-upscale'  # 不在生成时upscale
        ]

        if self.dry_run:
            return {'success': True, 'dry_run': True}

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            return {
                'success': result.returncode == 0,
                'output': output_path if result.returncode == 0 else None
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def upscale_video(
        self,
        input_video: str,
        output_video: str
    ) -> Dict:
        """步骤2: 独立Upscale (Real-ESRGAN 4x)"""

        cmd = [
            'python',
            str(project_root() / 'video_upscale_realesrgan_simple.py'),
            '--input', input_video,
            '--output', output_video,
            '--model-type', 'anime',
            '--tile', '512'
        ]

        if self.dry_run:
            return {'success': True, 'dry_run': True}

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=1800  # 30分钟timeout，因为AI upscale更慢
            )

            return {
                'success': result.returncode == 0,
                'output': output_video if result.returncode == 0 else None
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def process_single_image(
        self,
        image_path: str,
        character: str,
        category: str,
        index: int,
        output_dir: str
    ) -> Dict:
        """处理单张图片：SVD生成 + Upscale"""

        image_name = Path(image_path).stem
        base_filename = f"{character}_{category}_{index:02d}_{image_name}"

        # 输出路径
        base_video = os.path.join(output_dir, f"{base_filename}_base.mp4")
        final_video = os.path.join(output_dir, f"{base_filename}.mp4")

        print(f"\n处理图片:")
        print(f"  角色: {character}")
        print(f"  类别: {category}")
        print(f"  索引: {index}")
        print(f"  输入: {os.path.basename(image_path)}")

        start_time = time.time()

        # 步骤1: SVD生成
        print(f"  [1/2] SVD生成...")
        svd_result = self.generate_svd_video(image_path, base_video)

        if not svd_result.get('success'):
            print(f"  ❌ SVD生成失败")
            return {'success': False, 'step': 'svd'}

        # 步骤2: Upscale (如果启用)
        if self.enable_upscale:
            print(f"  [2/2] Upscale提升画质...")
            upscale_result = self.upscale_video(base_video, final_video)

            if not upscale_result.get('success'):
                print(f"  ❌ Upscale失败")
                return {'success': False, 'step': 'upscale'}

            # 删除base video节省空间
            if os.path.exists(base_video):
                os.remove(base_video)
        else:
            # 不upscale，直接重命名
            os.rename(base_video, final_video)

        elapsed = time.time() - start_time

        print(f"  ✅ 完成 (耗时: {elapsed:.1f}秒)")
        print(f"  输出: {final_video}")

        return {
            'success': True,
            'output': final_video,
            'elapsed': elapsed
        }

    def batch_generate_all(self):
        """批量生成所有420个视频"""

        total_videos = 0
        successful_videos = 0
        failed_videos = 0
        total_time = 0

        expected_total = len(self.characters) * self.images_per_category * len(self.categories)

        print("=" * 80)
        print("🎬 批量生成420个视频 - Real-ESRGAN AI Upscale")
        print("=" * 80)
        print(f"角色数量: {len(self.characters)}")
        print(f"每个角色: {self.images_per_category} × {len(self.categories)} = {self.images_per_category * len(self.categories)} 个视频")
        print(f"预计总数: {expected_total} 个视频")
        print(f"流程: SVD生成(1024×576) → 插值(300帧,60fps) → Real-ESRGAN 4x(4096×2304)")
        print(f"输出目录: {self.output_base_dir}")
        print(f"模式: {'测试模式' if self.dry_run else '正式生成'}")
        print("=" * 80)

        start_time = time.time()

        for char_idx, character in enumerate(self.characters, 1):
            print(f"\n{'='*80}")
            print(f"角色 [{char_idx}/{len(self.characters)}]: {character}")
            print(f"{'='*80}")

            for category in self.categories:
                images = self.get_character_images(character, category)

                if not images:
                    print(f"⚠️  {category}: 没有图片，跳过")
                    continue

                print(f"\n类别: {category} ({len(images)} 张图片)")

                # 创建输出目录
                output_dir = os.path.join(
                    self.output_base_dir,
                    character,
                    category
                )
                os.makedirs(output_dir, exist_ok=True)

                for img_idx, image_path in enumerate(images, 1):
                    result = self.process_single_image(
                        image_path=image_path,
                        character=character,
                        category=category,
                        index=img_idx,
                        output_dir=output_dir
                    )

                    total_videos += 1

                    if result.get('success'):
                        successful_videos += 1
                        if 'elapsed' in result:
                            total_time += result['elapsed']
                    else:
                        failed_videos += 1

                    # 进度统计
                    progress = (successful_videos + failed_videos) / expected_total * 100
                    avg_time = total_time / successful_videos if successful_videos > 0 else 0
                    remaining = expected_total - (successful_videos + failed_videos)
                    eta_minutes = (remaining * avg_time) / 60 if avg_time > 0 else 0

                    print(f"  总进度: {progress:.1f}% | 成功: {successful_videos}/{expected_total} | 失败: {failed_videos} | 平均: {avg_time:.1f}s/个 | 预计剩余: {eta_minutes:.0f}分钟")

        # 总结统计
        elapsed_total = time.time() - start_time

        print("\n" + "=" * 80)
        print("📊 批量生成完成统计")
        print("=" * 80)
        print(f"总视频数: {total_videos}")
        print(f"成功: {successful_videos}")
        print(f"失败: {failed_videos}")
        print(f"成功率: {successful_videos/total_videos*100:.1f}%" if total_videos > 0 else "N/A")
        print(f"总耗时: {elapsed_total/60:.1f} 分钟 ({elapsed_total/3600:.1f} 小时)")
        print(f"平均每个视频: {total_time/successful_videos:.1f} 秒" if successful_videos > 0 else "N/A")
        print(f"输出目录: {self.output_base_dir}")
        print("=" * 80)

        # 保存统计
        stats_file = os.path.join(self.output_base_dir, 'generation_stats.json')
        with open(stats_file, 'w') as f:
            json.dump({
                'total': total_videos,
                'successful': successful_videos,
                'failed': failed_videos,
                'total_time_seconds': elapsed_total,
                'avg_time_per_video': total_time/successful_videos if successful_videos > 0 else 0,
                'characters': len(self.characters),
                'images_per_category': self.images_per_category,
                'categories': len(self.categories)
            }, f, indent=2)

        print(f"\n统计已保存: {stats_file}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='批量生成420个SVD视频 (两步流程)')
    parser.add_argument('--dry-run', action='store_true', help='测试模式')
    parser.add_argument('--images-per-category', type=int, default=10, help='每类别图片数 (默认10)')
    parser.add_argument('--motion', type=int, default=80, help='运动强度 (默认80)')
    parser.add_argument('--guidance', type=float, default=3.5, help='引导强度 (默认3.5)')
    parser.add_argument('--steps', type=int, default=20, help='采样步数 (默认20)')
    parser.add_argument('--no-upscale', action='store_true', help='跳过upscale')
    parser.add_argument('--output-dir', default='/mnt/data/videos/svd_420_batch', help='输出目录')

    args = parser.parse_args()

    generator = BatchVideoGenerator420(
        images_per_category=args.images_per_category,
        motion_bucket_id=args.motion,
        guidance_scale=args.guidance,
        steps=args.steps,
        enable_upscale=not args.no_upscale,
        output_base_dir=args.output_dir,
        dry_run=args.dry_run
    )

    generator.batch_generate_all()


if __name__ == '__main__':
    main()
