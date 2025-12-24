#!/usr/bin/env python3
"""
Real-ESRGAN視頻Upscale工具
使用AI模型進行4x超解析度
"""

import os
import sys
import cv2
from PIL import Image
import numpy as np
from pathlib import Path
import argparse
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer
import torch


def upscale_video_realesrgan(
    input_video: str,
    output_video: str,
    model_path: str = "/mnt/c/ai_models/upscale/RealESRGAN_x4plus_anime_6B.pth",
    model_type: str = "anime",
    scale: int = 4,
    tile: int = 0,  # 0 = auto, 建議512 for 16GB GPU
    tile_pad: int = 10,
    pre_pad: int = 0,
    half_precision: bool = True
):
    """
    使用Real-ESRGAN進行視頻upscale

    Args:
        input_video: 輸入視頻路徑
        output_video: 輸出視頻路徑
        model_path: Real-ESRGAN模型路徑
        model_type: 模型類型 ("anime" or "general")
        scale: 放大倍數 (通常是4)
        tile: tile大小 (0=auto, 推薦512減少記憶體使用)
        tile_pad: tile padding
        pre_pad: pre padding
        half_precision: 使用fp16以節省記憶體
    """

    print(f"初始化Real-ESRGAN...")
    print(f"  模型: {os.path.basename(model_path)}")
    print(f"  類型: {model_type}")
    print(f"  縮放倍數: {scale}x")
    print(f"  精度: {'fp16' if half_precision else 'fp32'}")

    # 設置模型架構
    if model_type == "anime":
        # RealESRGAN_x4plus_anime_6B
        model = RRDBNet(
            num_in_ch=3,
            num_out_ch=3,
            num_feat=64,
            num_block=6,  # anime版本使用6個block
            num_grow_ch=32,
            scale=4
        )
    else:
        # RealESRGAN_x4plus (general)
        model = RRDBNet(
            num_in_ch=3,
            num_out_ch=3,
            num_feat=64,
            num_block=23,  # general版本使用23個block
            num_grow_ch=32,
            scale=4
        )

    # 初始化upsampler
    upsampler = RealESRGANer(
        scale=scale,
        model_path=model_path,
        model=model,
        tile=tile,
        tile_pad=tile_pad,
        pre_pad=pre_pad,
        half=half_precision,
        device='cuda' if torch.cuda.is_available() else 'cpu'
    )

    print(f"✓ Real-ESRGAN初始化完成")
    print(f"\n開始處理視頻: {input_video}")

    # 打開視頻
    cap = cv2.VideoCapture(input_video)

    # 獲取視頻屬性
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    orig_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    orig_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # 計算輸出尺寸
    output_width = orig_width * scale
    output_height = orig_height * scale

    print(f"\n原始規格:")
    print(f"  分辨率: {orig_width}×{orig_height}")
    print(f"  FPS: {fps}")
    print(f"  帧数: {frame_count}")
    print(f"\n輸出規格:")
    print(f"  分辨率: {output_width}×{output_height}")
    print(f"  FPS: {fps}")

    # 創建視頻寫入器
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video, fourcc, fps, (output_width, output_height))

    if not out.isOpened():
        print(f"❌ 錯誤：無法創建輸出視頻文件")
        return

    # 處理每一幀
    processed_frames = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # 使用Real-ESRGAN upscale
            output, _ = upsampler.enhance(frame, outscale=scale)

            # 寫入幀
            out.write(output)

            processed_frames += 1

            if processed_frames % 10 == 0:
                progress = (processed_frames / frame_count) * 100
                print(f"  處理進度: {processed_frames}/{frame_count} ({progress:.1f}%)")

    except Exception as e:
        print(f"❌ 處理錯誤: {e}")
        raise

    finally:
        # 釋放資源
        cap.release()
        out.release()

    print(f"\n✅ Real-ESRGAN Upscale完成！")
    print(f"輸出: {output_video}")
    print(f"最終分辨率: {output_width}×{output_height}")
    print(f"處理幀數: {processed_frames}")

    # 顯示文件大小
    if os.path.exists(output_video):
        file_size_mb = os.path.getsize(output_video) / (1024 * 1024)
        print(f"文件大小: {file_size_mb:.1f} MB")


def main():
    parser = argparse.ArgumentParser(description='Real-ESRGAN視頻Upscale工具')
    parser.add_argument('--input', required=True, help='輸入視頻路徑')
    parser.add_argument('--output', required=True, help='輸出視頻路徑')
    parser.add_argument('--model-type', default='anime',
                       choices=['anime', 'general'],
                       help='模型類型 (anime或general)')
    parser.add_argument('--model-path', default='/mnt/c/ai_models/upscale/RealESRGAN_x4plus_anime_6B.pth',
                       help='模型路徑')
    parser.add_argument('--scale', type=int, default=4,
                       help='放大倍數 (默認4x)')
    parser.add_argument('--tile', type=int, default=0,
                       help='Tile大小 (0=auto, 推薦512減少記憶體)')
    parser.add_argument('--fp32', action='store_true',
                       help='使用fp32而非fp16 (更高精度但需要更多記憶體)')

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"❌ 錯誤: 輸入文件不存在: {args.input}")
        sys.exit(1)

    if not os.path.exists(args.model_path):
        print(f"❌ 錯誤: 模型文件不存在: {args.model_path}")
        print(f"請確保模型已下載到: {args.model_path}")
        sys.exit(1)

    # 創建輸出目錄
    os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)

    upscale_video_realesrgan(
        input_video=args.input,
        output_video=args.output,
        model_path=args.model_path,
        model_type=args.model_type,
        scale=args.scale,
        tile=args.tile,
        half_precision=not args.fp32
    )


if __name__ == '__main__':
    main()
