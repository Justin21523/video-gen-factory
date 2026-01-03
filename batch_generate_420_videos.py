#!/usr/bin/env python3
"""
批量生成420个视频
- 14个角色
- 每个角色30张图片（10 expression, 10 action, 10 pose）
- 总共420个视频
- 每个5秒，60fps，1024×1024
"""

import os
import sys
import random
import time
from pathlib import Path
from typing import List, Dict
import subprocess
import json

from vgf_paths import project_root

# 设置AI_WAREHOUSE 3.0规范的环境变量
os.environ['HF_HOME'] = '/mnt/c/ai_cache/huggingface'
os.environ['TRANSFORMERS_CACHE'] = '/mnt/c/ai_cache/huggingface'
os.environ['TORCH_HOME'] = '/mnt/c/ai_cache/torch'
os.environ['XDG_CACHE_HOME'] = '/mnt/c/ai_cache'


class BatchVideoGenerator:
    """批量视频生成器"""

    def __init__(
        self,
        input_base_dir: str = "/mnt/data/ai_data/synthetic_lora_data/generated_data",
        output_base_dir: str = "/mnt/data/videos/svd_generated",
        images_per_category: int = 10,
        motion_bucket_id: int = 80,
        guidance_scale: float = 3.5,
        steps: int = 25,
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
        """获取角色指定类别的图片"""
        image_dir = os.path.join(
            self.input_base_dir,
            character,
            category,
            'images'
        )

        if not os.path.exists(image_dir):
            print(f"⚠️  目录不存在: {image_dir}")
            return []

        # 获取所有PNG图片
        all_images = [
            os.path.join(image_dir, f)
            for f in os.listdir(image_dir)
            if f.endswith('.png')
        ]

        # 随机选择指定数量
        if len(all_images) > self.images_per_category:
            selected = random.sample(all_images, self.images_per_category)
        else:
            selected = all_images

        return sorted(selected)

    def generate_single_video(
        self,
        input_image: str,
        output_path: str,
        character: str,
        category: str,
        index: int
    ) -> Dict:
        """生成单个视频"""

        # 构建命令
        cmd = [
            'python',
            str(project_root() / 'svd_pure_python.py'),
            '--input', input_image,
            '--output', output_path,
            '--motion', str(self.motion_bucket_id),
            '--guidance', str(self.guidance_scale),
            '--steps', str(self.steps)
        ]

        if not self.enable_upscale:
            cmd.append('--no-upscale')

        print(f"\n生成视频:")
        print(f"  角色: {character}")
        print(f"  类别: {category}")
        print(f"  索引: {index}")
        print(f"  输入: {os.path.basename(input_image)}")
        print(f"  输出: {output_path}")

        if self.dry_run:
            print("  [DRY RUN] 跳过实际生成")
            return {'success': True, 'dry_run': True}

        # 执行生成
        start_time = time.time()
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10分钟超时
            )

            elapsed = time.time() - start_time

            if result.returncode == 0:
                print(f"  ✅ 成功 (耗时: {elapsed:.1f}秒)")
                return {
                    'success': True,
                    'elapsed': elapsed,
                    'output': output_path
                }
            else:
                print(f"  ❌ 失败: {result.stderr[:200]}")
                return {
                    'success': False,
                    'error': result.stderr,
                    'elapsed': elapsed
                }

        except subprocess.TimeoutExpired:
            print(f"  ❌ 超时（>10分钟）")
            return {'success': False, 'error': 'timeout'}
        except Exception as e:
            print(f"  ❌ 错误: {e}")
            return {'success': False, 'error': str(e)}

    def batch_generate_all(self):
        """批量生成所有视频"""

        total_videos = 0
        successful_videos = 0
        failed_videos = 0
        total_time = 0

        print("=" * 80)
        print("🎬 批量生成420个视频")
        print("=" * 80)
        print(f"角色数量: {len(self.characters)}")
        print(f"每个角色: {self.images_per_category} × {len(self.categories)} = {self.images_per_category * len(self.categories)} 个视频")
        print(f"预计总数: {len(self.characters) * self.images_per_category * len(self.categories)} 个视频")
        print(f"输入目录: {self.input_base_dir}")
        print(f"输出目录: {self.output_base_dir}")
        print(f"模式: {'测试模式' if self.dry_run else '正式生成'}")
        print("=" * 80)

        start_time = time.time()

        for char_idx, character in enumerate(self.characters, 1):
            print(f"\n{'='*80}")
            print(f"处理角色 [{char_idx}/{len(self.characters)}]: {character}")
            print(f"{'='*80}")

            for category in self.categories:
                # 获取图片
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

                # 生成每张图片的视频
                for img_idx, image_path in enumerate(images, 1):
                    # 构建输出文件名
                    image_name = Path(image_path).stem
                    output_filename = f"{character}_{category}_{img_idx:02d}_{image_name}.mp4"
                    output_path = os.path.join(output_dir, output_filename)

                    # 如果文件已存在，跳过
                    if os.path.exists(output_path) and not self.dry_run:
                        print(f"  [{img_idx}/{len(images)}] 已存在，跳过: {output_filename}")
                        successful_videos += 1
                        total_videos += 1
                        continue

                    # 生成视频
                    result = self.generate_single_video(
                        input_image=image_path,
                        output_path=output_path,
                        character=character,
                        category=category,
                        index=img_idx
                    )

                    total_videos += 1

                    if result.get('success'):
                        successful_videos += 1
                        if 'elapsed' in result:
                            total_time += result['elapsed']
                    else:
                        failed_videos += 1

                    # 进度显示
                    progress = (successful_videos + failed_videos) / (len(self.characters) * self.images_per_category * len(self.categories)) * 100
                    avg_time = total_time / successful_videos if successful_videos > 0 else 0
                    remaining = (len(self.characters) * self.images_per_category * len(self.categories)) - (successful_videos + failed_videos)
                    eta_seconds = remaining * avg_time if avg_time > 0 else 0

                    print(f"  进度: {progress:.1f}% | 成功: {successful_videos} | 失败: {failed_videos} | 平均耗时: {avg_time:.1f}s | 预计剩余: {eta_seconds/60:.0f}分钟")

        # 统计总结
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

        print(f"\n统计已保存到: {stats_file}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='批量生成420个SVD视频')
    parser.add_argument('--dry-run', action='store_true', help='测试模式，不实际生成')
    parser.add_argument('--images-per-category', type=int, default=10, help='每个类别生成的图片数')
    parser.add_argument('--motion', type=int, default=80, help='运动强度 (50=稳定, 150=运动大)')
    parser.add_argument('--guidance', type=float, default=3.5, help='引导强度')
    parser.add_argument('--steps', type=int, default=25, help='采样步数')
    parser.add_argument('--no-upscale', action='store_true', help='跳过upscale')
    parser.add_argument('--output-dir', default='/mnt/data/videos/svd_generated', help='输出目录')

    args = parser.parse_args()

    generator = BatchVideoGenerator(
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
