#!/usr/bin/env python3
"""
独立视频Upscale工具
使用2x+2x策略提升画质后缩回原尺寸
"""

import os
import sys
import cv2
from PIL import Image
import numpy as np
from pathlib import Path
import argparse


def upscale_video_2x2x(
    input_video: str,
    output_video: str,
    method: str = "lanczos"
):
    """
    2x+2x upscale然后缩回原尺寸

    流程：
    1. 读取视频帧
    2. 每帧放大2x
    3. 再放大2x（总共4x）
    4. 缩回原尺寸
    5. 保存视频
    """

    print(f"开始处理视频: {input_video}")

    # 打开视频
    cap = cv2.VideoCapture(input_video)

    # 获取视频属性
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    orig_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    orig_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    print(f"原始规格:")
    print(f"  分辨率: {orig_width}×{orig_height}")
    print(f"  FPS: {fps}")
    print(f"  帧数: {frame_count}")

    print(f"\nUpscale策略: 2x+2x")
    print(f"  阶段1: {orig_width}×{orig_height} → {orig_width*2}×{orig_height*2}")
    print(f"  阶段2: {orig_width*2}×{orig_height*2} → {orig_width*4}×{orig_height*4}")
    print(f"  阶段3: {orig_width*4}×{orig_height*4} → {orig_width}×{orig_height} (缩回)")

    # 选择插值方法
    if method == "lanczos":
        resample = Image.LANCZOS
    elif method == "bicubic":
        resample = Image.BICUBIC
    else:
        resample = Image.LANCZOS

    # 创建视频写入器
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video, fourcc, fps, (orig_width, orig_height))

    # 处理每一帧
    processed_frames = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # OpenCV BGR → PIL RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_frame = Image.fromarray(frame_rgb)

        # 阶段1: 2x
        stage1 = pil_frame.resize(
            (orig_width * 2, orig_height * 2),
            resample
        )

        # 阶段2: 再2x
        stage2 = stage1.resize(
            (orig_width * 4, orig_height * 4),
            resample
        )

        # 阶段3: 缩回原尺寸
        final = stage2.resize(
            (orig_width, orig_height),
            resample
        )

        # PIL RGB → OpenCV BGR
        final_np = np.array(final)
        final_bgr = cv2.cvtColor(final_np, cv2.COLOR_RGB2BGR)

        # 写入帧
        out.write(final_bgr)

        processed_frames += 1

        if processed_frames % 30 == 0:
            progress = (processed_frames / frame_count) * 100
            print(f"  处理进度: {processed_frames}/{frame_count} ({progress:.1f}%)")

    # 释放资源
    cap.release()
    out.release()

    print(f"\n✅ Upscale完成！")
    print(f"输出: {output_video}")
    print(f"处理帧数: {processed_frames}")


def main():
    parser = argparse.ArgumentParser(description='独立视频Upscale工具 (2x+2x)')
    parser.add_argument('--input', required=True, help='输入视频路径')
    parser.add_argument('--output', required=True, help='输出视频路径')
    parser.add_argument('--method', default='lanczos',
                       choices=['lanczos', 'bicubic'],
                       help='缩放方法')

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"❌ 错误: 输入文件不存在: {args.input}")
        sys.exit(1)

    # 创建输出目录
    os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)

    upscale_video_2x2x(
        input_video=args.input,
        output_video=args.output,
        method=args.method
    )


if __name__ == '__main__':
    main()
