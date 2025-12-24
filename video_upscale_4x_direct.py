#!/usr/bin/env python3
"""
直接4x Upscale工具（不縮回原尺寸）
輸出分辨率：4096×2304 (從1024×576)
"""

import os
import sys
import cv2
from PIL import Image
import numpy as np
from pathlib import Path
import argparse


def upscale_video_4x_direct(
    input_video: str,
    output_video: str,
    method: str = "lanczos",
    strategy: str = "2x+2x"
):
    """
    直接4x upscale（不縮回原尺寸）

    Args:
        input_video: 輸入視頻路徑
        output_video: 輸出視頻路徑
        method: 縮放方法 (lanczos/bicubic)
        strategy: "2x+2x" (分兩階段) 或 "4x" (一次性)
    """

    print(f"開始處理視頻: {input_video}")

    # 打開視頻
    cap = cv2.VideoCapture(input_video)

    # 獲取視頻屬性
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    orig_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    orig_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # 計算4x後的尺寸
    final_width = orig_width * 4
    final_height = orig_height * 4

    print(f"\n原始規格:")
    print(f"  分辨率: {orig_width}×{orig_height}")
    print(f"  FPS: {fps}")
    print(f"  帧数: {frame_count}")

    print(f"\n4x Upscale策略: {strategy}")
    print(f"  最終輸出: {final_width}×{final_height}")

    # 選擇插值方法
    if method == "lanczos":
        resample = Image.LANCZOS
    elif method == "bicubic":
        resample = Image.BICUBIC
    else:
        resample = Image.LANCZOS

    # 創建視頻寫入器
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video, fourcc, fps, (final_width, final_height))

    # 處理每一幀
    processed_frames = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # OpenCV BGR → PIL RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_frame = Image.fromarray(frame_rgb)

        if strategy == "2x+2x":
            # 阶段1: 2x
            stage1 = pil_frame.resize(
                (orig_width * 2, orig_height * 2),
                resample
            )

            # 阶段2: 再2x (總共4x)
            final = stage1.resize(
                (final_width, final_height),
                resample
            )
        else:  # "4x" 一次性
            final = pil_frame.resize(
                (final_width, final_height),
                resample
            )

        # PIL RGB → OpenCV BGR
        final_np = np.array(final)
        final_bgr = cv2.cvtColor(final_np, cv2.COLOR_RGB2BGR)

        # 寫入帧
        out.write(final_bgr)

        processed_frames += 1

        if processed_frames % 30 == 0:
            progress = (processed_frames / frame_count) * 100
            print(f"  處理進度: {processed_frames}/{frame_count} ({progress:.1f}%)")

    # 釋放資源
    cap.release()
    out.release()

    print(f"\n✅ 4x Upscale完成！")
    print(f"輸出: {output_video}")
    print(f"最終分辨率: {final_width}×{final_height}")
    print(f"處理幀數: {processed_frames}")

    # 顯示文件大小
    if os.path.exists(output_video):
        file_size_mb = os.path.getsize(output_video) / (1024 * 1024)
        print(f"文件大小: {file_size_mb:.1f} MB")


def main():
    parser = argparse.ArgumentParser(description='直接4x Upscale工具（不縮回原尺寸）')
    parser.add_argument('--input', required=True, help='輸入視頻路徑')
    parser.add_argument('--output', required=True, help='輸出視頻路徑')
    parser.add_argument('--method', default='lanczos',
                       choices=['lanczos', 'bicubic'],
                       help='縮放方法')
    parser.add_argument('--strategy', default='2x+2x',
                       choices=['2x+2x', '4x'],
                       help='Upscale策略（2x+2x分階段 或 4x一次性）')

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"❌ 錯誤: 輸入文件不存在: {args.input}")
        sys.exit(1)

    # 創建輸出目錄
    os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)

    upscale_video_4x_direct(
        input_video=args.input,
        output_video=args.output,
        method=args.method,
        strategy=args.strategy
    )


if __name__ == '__main__':
    main()
