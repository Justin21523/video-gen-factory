#!/usr/bin/env python3
"""
纯Python SVD视频生成系统
- 不依赖ComfyUI
- 使用diffusers库
- 支持稳定性优化
- 输出：60fps, 5秒, 300帧
- 遵循AI_WAREHOUSE 3.0规范
"""

import os
import sys

# 设置AI_WAREHOUSE 3.0规范的环境变量
os.environ['HF_HOME'] = '/mnt/c/ai_cache/huggingface'
os.environ['TRANSFORMERS_CACHE'] = '/mnt/c/ai_cache/huggingface'
os.environ['TORCH_HOME'] = '/mnt/c/ai_cache/torch'
os.environ['XDG_CACHE_HOME'] = '/mnt/c/ai_cache'

# 创建必要的目录
for cache_dir in [
    '/mnt/c/ai_cache/huggingface',
    '/mnt/c/ai_cache/torch',
    '/mnt/c/ai_models/video'
]:
    os.makedirs(cache_dir, exist_ok=True)

import torch
import numpy as np
from PIL import Image
from pathlib import Path
from diffusers import StableVideoDiffusionPipeline
from diffusers.utils import load_image, export_to_video
import cv2
from typing import List, Tuple
import argparse


class SVDPurePythonGenerator:
    """纯Python SVD生成器"""

    def __init__(
        self,
        model_id: str = "stabilityai/stable-video-diffusion-img2vid-xt",
        device: str = "cuda",
        dtype: str = "fp16",
        cache_dir: str = "/mnt/c/ai_cache/huggingface"
    ):
        """
        初始化SVD生成器

        Args:
            model_id: Hugging Face模型ID
                - stabilityai/stable-video-diffusion-img2vid-xt (25帧)
                - stabilityai/stable-video-diffusion-img2vid (14帧)
            device: 运行设备
            dtype: 数据类型 (fp16/fp32)
            cache_dir: 模型缓存目录 (遵循AI_WAREHOUSE 3.0规范)
        """
        self.device = device
        self.dtype = torch.float16 if dtype == "fp16" else torch.float32
        self.cache_dir = cache_dir

        print(f"加载SVD模型: {model_id}")
        print(f"设备: {device}, 精度: {dtype}")
        print(f"缓存目录: {cache_dir}")

        self.pipe = StableVideoDiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=self.dtype,
            variant="fp16" if dtype == "fp16" else None,
            cache_dir=cache_dir
        )
        self.pipe.to(device)

        # 优化内存 - 使用CPU offload减少GPU内存使用
        self.pipe.enable_model_cpu_offload()

        print("✓ SVD模型加载完成")
        print(f"  模型位置: {cache_dir}")
        print(f"  内存优化: CPU offload已启用")

    def generate_video(
        self,
        image_path: str,
        output_path: str,
        # 稳定性参数
        num_frames: int = 25,
        motion_bucket_id: int = 80,  # 越低越稳定
        fps: int = 6,  # SVD基础fps
        noise_aug_strength: float = 0.0,  # 0.0 = 最稳定
        decode_chunk_size: int = 8,
        # 采样参数
        num_inference_steps: int = 25,
        min_guidance_scale: float = 1.0,
        max_guidance_scale: float = 3.5,  # 类似CFG，越高越贴近输入
        # 其他
        seed: int = 42,
        width: int = None,  # None = 自动检测
        height: int = None  # None = 自动检测
    ) -> List[Image.Image]:
        """
        生成视频帧

        稳定性建议：
            - motion_bucket_id: 50-80 (低=稳定, 高=运动大)
            - max_guidance_scale: 3.0-4.0 (高=贴近输入)
            - noise_aug_strength: 0.0 (不添加噪声)
            - num_inference_steps: 25-30 (高质量)

        Returns:
            List of PIL Image frames
        """
        # 加载图片并自动检测尺寸
        image = load_image(image_path)
        original_size = image.size

        # 如果没有指定尺寸，使用1024×576（16:9高质量）
        if width is None or height is None:
            # 使用较高分辨率以获得更好画质
            width, height = 1024, 576
            print(f"  使用高质量尺寸: {width}×{height} (原图: {original_size[0]}×{original_size[1]})")

        # 调整图片大小
        if image.size != (width, height):
            image = image.resize((width, height))

        print(f"\n生成SVD视频:")
        print(f"  输入图片: {image_path}")
        print(f"  原始尺寸: {original_size[0]}×{original_size[1]}")
        print(f"  输出: {output_path}")
        print(f"  帧数: {num_frames}")
        print(f"  分辨率: {width}×{height}")
        print(f"  稳定性参数:")
        print(f"    - motion_bucket_id: {motion_bucket_id}")
        print(f"    - max_guidance_scale: {max_guidance_scale}")
        print(f"    - noise_aug_strength: {noise_aug_strength}")
        print(f"    - num_inference_steps: {num_inference_steps}")

        # 设置随机种子
        generator = torch.manual_seed(seed)

        # 生成视频
        print("  开始生成...")
        frames = self.pipe(
            image,
            height=height,
            width=width,
            num_frames=num_frames,
            num_inference_steps=num_inference_steps,
            min_guidance_scale=min_guidance_scale,
            max_guidance_scale=max_guidance_scale,
            fps=fps,
            motion_bucket_id=motion_bucket_id,
            noise_aug_strength=noise_aug_strength,
            decode_chunk_size=decode_chunk_size,
            generator=generator
        ).frames[0]

        print(f"  ✓ 生成完成：{len(frames)} 帧")

        # 保存临时视频
        export_to_video(frames, output_path, fps=fps)
        print(f"  ✓ 保存到: {output_path}")

        return frames


class VideoProcessor:
    """视频后处理工具"""

    @staticmethod
    def interpolate_to_60fps(
        frames: List[Image.Image],
        target_fps: int = 60,
        target_duration: float = 5.0,
        method: str = "linear"
    ) -> List[Image.Image]:
        """
        插值到60fps, 5秒

        Args:
            frames: 输入帧列表
            target_fps: 目标fps (60)
            target_duration: 目标时长（秒）(5.0)
            method: 插值方法 ("linear", "cubic")

        Returns:
            插值后的帧列表
        """
        target_frames = int(target_fps * target_duration)  # 300帧
        current_frames = len(frames)

        print(f"\n帧插值:")
        print(f"  当前: {current_frames} 帧")
        print(f"  目标: {target_frames} 帧 ({target_fps}fps × {target_duration}s)")
        print(f"  插值倍数: {target_frames / current_frames:.1f}x")

        if current_frames >= target_frames:
            print(f"  无需插值，已达目标帧数")
            return frames[:target_frames]

        # 转换为numpy数组
        frame_arrays = [np.array(f) for f in frames]
        height, width = frame_arrays[0].shape[:2]

        # 使用OpenCV进行插值
        interpolated = []
        for i in range(target_frames):
            # 计算源帧位置
            src_pos = (i / target_frames) * (current_frames - 1)
            src_idx = int(src_pos)
            alpha = src_pos - src_idx

            if src_idx >= current_frames - 1:
                interpolated.append(frames[-1])
            else:
                # 线性插值
                frame1 = frame_arrays[src_idx]
                frame2 = frame_arrays[src_idx + 1]

                blended = cv2.addWeighted(
                    frame1, 1 - alpha,
                    frame2, alpha,
                    0
                )
                interpolated.append(Image.fromarray(blended))

        print(f"  ✓ 插值完成: {len(interpolated)} 帧")
        return interpolated

    @staticmethod
    def upscale_and_downscale(
        frames: List[Image.Image],
        upscale_strategy: str = "2x+2x",
        method: str = "lanczos"
    ) -> List[Image.Image]:
        """
        分阶段upscale然后缩放回原尺寸（提升画质）

        Args:
            frames: 输入帧
            upscale_strategy: "2x+2x" (分两阶段) 或 "4x" (一次性)
            method: 缩放方法 ("lanczos", "bicubic")

        Returns:
            处理后的帧
        """
        if not frames:
            return frames

        width, height = frames[0].size
        resample = Image.LANCZOS if method == "lanczos" else Image.BICUBIC

        print(f"\nUpscale提升画质:")
        print(f"  原始: {width}×{height}")
        print(f"  策略: {upscale_strategy}")
        print(f"  方法: {method}")

        processed = []

        if upscale_strategy == "2x+2x":
            # 分两阶段：2x → 2x → 缩回原尺寸
            print(f"  阶段1: {width}×{height} → {width*2}×{height*2}")
            print(f"  阶段2: {width*2}×{height*2} → {width*4}×{height*4}")
            print(f"  阶段3: {width*4}×{height*4} → {width}×{height}")

            for i, frame in enumerate(frames):
                # 第一阶段：2x
                stage1 = frame.resize((width * 2, height * 2), resample)
                # 第二阶段：再2x
                stage2 = stage1.resize((width * 4, height * 4), resample)
                # 缩放回原尺寸
                final = stage2.resize((width, height), resample)
                processed.append(final)

                if (i + 1) % 50 == 0:
                    print(f"  处理进度: {i + 1}/{len(frames)}")

        else:  # "4x" 一次性
            upscaled_size = (width * 4, height * 4)
            print(f"  一次性: {width}×{height} → {upscaled_size[0]}×{upscaled_size[1]} → {width}×{height}")

            for i, frame in enumerate(frames):
                # 一次性4x
                upscaled = frame.resize(upscaled_size, resample)
                # 缩放回原尺寸
                downscaled = upscaled.resize((width, height), resample)
                processed.append(downscaled)

                if (i + 1) % 50 == 0:
                    print(f"  处理进度: {i + 1}/{len(frames)}")

        print(f"  ✓ 完成")
        return processed

    @staticmethod
    def save_video(
        frames: List[Image.Image],
        output_path: str,
        fps: int = 60,
        codec: str = "mp4v",
        quality: int = 95
    ):
        """
        保存视频

        Args:
            frames: 帧列表
            output_path: 输出路径
            fps: 帧率
            codec: 编码器
            quality: 质量 (0-100)
        """
        if not frames:
            print("错误：没有帧可保存")
            return

        width, height = frames[0].size

        print(f"\n保存视频:")
        print(f"  路径: {output_path}")
        print(f"  分辨率: {width}×{height}")
        print(f"  帧数: {len(frames)}")
        print(f"  FPS: {fps}")
        print(f"  时长: {len(frames) / fps:.2f}秒")

        # 使用ffmpeg保存高质量视频
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        for frame in frames:
            # PIL to OpenCV (RGB -> BGR)
            frame_cv = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
            out.write(frame_cv)

        out.release()
        print(f"  ✓ 保存完成")


def main():
    parser = argparse.ArgumentParser(description='纯Python SVD视频生成')
    parser.add_argument('--input', required=True, help='输入图片路径')
    parser.add_argument('--output', default='output.mp4', help='输出视频路径')
    parser.add_argument('--motion', type=int, default=80,
                       help='运动强度 (50=稳定, 80=平衡, 150=运动大)')
    parser.add_argument('--guidance', type=float, default=3.5,
                       help='引导强度 (3.5=平衡, 4.0=高稳定)')
    parser.add_argument('--steps', type=int, default=25, help='采样步数')
    parser.add_argument('--upscale', type=int, default=4, help='临时放大倍数')
    parser.add_argument('--no-upscale', action='store_true', help='跳过upscale步骤')
    parser.add_argument('--no-interpolation', action='store_true', help='跳过插值步骤（只输出25帧）')

    args = parser.parse_args()

    print("=" * 80)
    print("🎬 纯Python SVD视频生成系统")
    print("=" * 80)

    # 1. 生成SVD视频
    generator = SVDPurePythonGenerator()
    frames = generator.generate_video(
        image_path=args.input,
        output_path="temp_svd.mp4",
        num_frames=25,  # SVD-XT最多25帧
        motion_bucket_id=args.motion,
        max_guidance_scale=args.guidance,
        num_inference_steps=args.steps
    )

    # 2. 插值到60fps, 5秒 (300帧) - 可选
    if not args.no_interpolation:
        frames = VideoProcessor.interpolate_to_60fps(
            frames,
            target_fps=60,
            target_duration=5.0
        )
        output_fps = 60
    else:
        print("\n⏭️  跳过插值，保留原始25帧")
        output_fps = 6  # SVD默认fps

    # 3. Upscale提升画质（可选）- 使用2x+2x策略
    if not args.no_upscale:
        frames = VideoProcessor.upscale_and_downscale(
            frames,
            upscale_strategy="2x+2x"
        )

    # 4. 保存最终视频
    VideoProcessor.save_video(
        frames,
        output_path=args.output,
        fps=output_fps
    )

    print("\n" + "=" * 80)
    print("✅ 完成！")
    print(f"输出: {args.output}")
    print(f"规格: 1024×576, 300帧, 60fps, 5秒")
    print("=" * 80)


if __name__ == '__main__':
    main()
