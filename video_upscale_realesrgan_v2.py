#!/usr/bin/env python3
"""
Real-ESRGAN視頻Upscale工具 v2
使用簡化的導入避免torchvision版本衝突
"""

import os
import sys
import cv2
import numpy as np
import torch
from pathlib import Path
import argparse


def upscale_video_realesrgan_v2(
    input_video: str,
    output_video: str,
    model_path: str = "/mnt/c/ai_models/upscale/RealESRGAN_x4plus_anime_6B.pth",
    scale: int = 4,
    tile: int = 512,
    tile_pad: int = 10,
    pre_pad: int = 0,
    half_precision: bool = True
):
    """
    使用Real-ESRGAN進行視頻upscale (簡化版)

    Args:
        input_video: 輸入視頻路徑
        output_video: 輸出視頻路徑
        model_path: Real-ESRGAN模型路徑
        scale: 放大倍數 (通常是4)
        tile: tile大小 (推薦512減少記憶體使用)
        tile_pad: tile padding
        pre_pad: pre padding
        half_precision: 使用fp16以節省記憶體
    """

    print(f"初始化Real-ESRGAN...")
    print(f"  模型: {os.path.basename(model_path)}")
    print(f"  縮放倍數: {scale}x")
    print(f"  Tile大小: {tile}")
    print(f"  精度: {'fp16' if half_precision else 'fp32'}")

    # 延遲導入避免版本衝突
    try:
        from realesrgan import RealESRGANer
        from basicsr.archs.rrdbnet_arch import RRDBNet
    except ImportError as e:
        print(f"❌ 導入錯誤: {e}")
        print("\n嘗試使用替代方法...")
        # 使用命令行工具作為後備
        return upscale_video_cli(input_video, output_video, model_path, scale)

    # 設置模型架構（anime版本 = 6 blocks）
    if "anime" in model_path.lower():
        num_block = 6
    else:
        num_block = 23

    try:
        model = RRDBNet(
            num_in_ch=3,
            num_out_ch=3,
            num_feat=64,
            num_block=num_block,
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
    except Exception as e:
        print(f"❌ 初始化錯誤: {e}")
        print("\n嘗試使用替代方法...")
        return upscale_video_cli(input_video, output_video, model_path, scale)

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
        cap.release()
        return

    # 處理每一幀
    processed_frames = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # 使用Real-ESRGAN upscale
            try:
                output, _ = upsampler.enhance(frame, outscale=scale)
            except Exception as e:
                print(f"⚠️  幀 {processed_frames} 處理失敗: {e}")
                # 使用簡單放大作為後備
                output = cv2.resize(frame, (output_width, output_height), interpolation=cv2.INTER_CUBIC)

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


def upscale_video_cli(input_video, output_video, model_path, scale):
    """
    使用命令行工具作為後備方案
    """
    print("使用Real-ESRGAN命令行工具...")

    # 創建臨時目錄
    import tempfile
    import subprocess

    temp_dir = tempfile.mkdtemp()
    frames_dir = os.path.join(temp_dir, "frames")
    upscaled_dir = os.path.join(temp_dir, "upscaled")
    os.makedirs(frames_dir, exist_ok=True)
    os.makedirs(upscaled_dir, exist_ok=True)

    try:
        # 1. 提取幀
        print("步驟1: 提取視頻幀...")
        cap = cv2.VideoCapture(input_video)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        frame_idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_path = os.path.join(frames_dir, f"frame_{frame_idx:06d}.png")
            cv2.imwrite(frame_path, frame)
            frame_idx += 1

            if frame_idx % 30 == 0:
                print(f"  提取: {frame_idx}/{frame_count}")

        cap.release()

        # 2. Upscale每一幀（使用Python API的逐幀處理）
        print("步驟2: Upscale幀...")

        from realesrgan import RealESRGANer
        from basicsr.archs.rrdbnet_arch import RRDBNet

        num_block = 6 if "anime" in model_path.lower() else 23
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=num_block, num_grow_ch=32, scale=4)

        upsampler = RealESRGANer(
            scale=scale,
            model_path=model_path,
            model=model,
            tile=512,
            tile_pad=10,
            pre_pad=0,
            half=True,
            device='cuda'
        )

        for i in range(frame_count):
            frame_path = os.path.join(frames_dir, f"frame_{i:06d}.png")
            if not os.path.exists(frame_path):
                continue

            img = cv2.imread(frame_path, cv2.IMREAD_UNCHANGED)
            output, _ = upsampler.enhance(img, outscale=scale)

            output_path = os.path.join(upscaled_dir, f"frame_{i:06d}.png")
            cv2.imwrite(output_path, output)

            if (i + 1) % 10 == 0:
                print(f"  Upscale: {i + 1}/{frame_count}")

        # 3. 合成視頻
        print("步驟3: 合成視頻...")
        first_frame = cv2.imread(os.path.join(upscaled_dir, "frame_000000.png"))
        height, width = first_frame.shape[:2]

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

        for i in range(frame_count):
            frame_path = os.path.join(upscaled_dir, f"frame_{i:06d}.png")
            if os.path.exists(frame_path):
                frame = cv2.imread(frame_path)
                out.write(frame)

        out.release()
        print(f"✓ 完成！輸出: {output_video}")

    finally:
        # 清理臨時文件
        import shutil
        shutil.rmtree(temp_dir)


def main():
    parser = argparse.ArgumentParser(description='Real-ESRGAN視頻Upscale工具 v2')
    parser.add_argument('--input', required=True, help='輸入視頻路徑')
    parser.add_argument('--output', required=True, help='輸出視頻路徑')
    parser.add_argument('--model-path', default='/mnt/c/ai_models/upscale/RealESRGAN_x4plus_anime_6B.pth',
                       help='模型路徑')
    parser.add_argument('--scale', type=int, default=4,
                       help='放大倍數 (默認4x)')
    parser.add_argument('--tile', type=int, default=512,
                       help='Tile大小 (推薦512減少記憶體)')
    parser.add_argument('--fp32', action='store_true',
                       help='使用fp32而非fp16')

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"❌ 錯誤: 輸入文件不存在: {args.input}")
        sys.exit(1)

    if not os.path.exists(args.model_path):
        print(f"❌ 錯誤: 模型文件不存在: {args.model_path}")
        sys.exit(1)

    # 創建輸出目錄
    os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)

    upscale_video_realesrgan_v2(
        input_video=args.input,
        output_video=args.output,
        model_path=args.model_path,
        scale=args.scale,
        tile=args.tile,
        half_precision=not args.fp32
    )


if __name__ == '__main__':
    main()
