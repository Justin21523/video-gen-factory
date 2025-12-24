#!/usr/bin/env python3
"""
Real-ESRGAN視頻Upscale工具 - 簡化版
繞過basicsr的導入問題，直接使用模型推理
"""

import os
import sys
import cv2
import numpy as np
import torch
from pathlib import Path
import argparse
import tempfile
import shutil


def load_realesrgan_model(model_path, num_block=6, device='cuda'):
    """
    直接加載Real-ESRGAN模型，避免basicsr導入問題
    """
    # 手動構建RRDBNet結構
    import torch.nn as nn

    class ResidualDenseBlock(nn.Module):
        def __init__(self, num_feat=64, num_grow_ch=32):
            super(ResidualDenseBlock, self).__init__()
            self.conv1 = nn.Conv2d(num_feat, num_grow_ch, 3, 1, 1)
            self.conv2 = nn.Conv2d(num_feat + num_grow_ch, num_grow_ch, 3, 1, 1)
            self.conv3 = nn.Conv2d(num_feat + 2 * num_grow_ch, num_grow_ch, 3, 1, 1)
            self.conv4 = nn.Conv2d(num_feat + 3 * num_grow_ch, num_grow_ch, 3, 1, 1)
            self.conv5 = nn.Conv2d(num_feat + 4 * num_grow_ch, num_feat, 3, 1, 1)
            self.lrelu = nn.LeakyReLU(negative_slope=0.2, inplace=True)

        def forward(self, x):
            x1 = self.lrelu(self.conv1(x))
            x2 = self.lrelu(self.conv2(torch.cat((x, x1), 1)))
            x3 = self.lrelu(self.conv3(torch.cat((x, x1, x2), 1)))
            x4 = self.lrelu(self.conv4(torch.cat((x, x1, x2, x3), 1)))
            x5 = self.conv5(torch.cat((x, x1, x2, x3, x4), 1))
            return x5 * 0.2 + x

    class RRDB(nn.Module):
        def __init__(self, num_feat, num_grow_ch=32):
            super(RRDB, self).__init__()
            self.rdb1 = ResidualDenseBlock(num_feat, num_grow_ch)
            self.rdb2 = ResidualDenseBlock(num_feat, num_grow_ch)
            self.rdb3 = ResidualDenseBlock(num_feat, num_grow_ch)

        def forward(self, x):
            out = self.rdb1(x)
            out = self.rdb2(out)
            out = self.rdb3(out)
            return out * 0.2 + x

    class RRDBNet(nn.Module):
        def __init__(self, num_in_ch=3, num_out_ch=3, scale=4, num_feat=64, num_block=23, num_grow_ch=32):
            super(RRDBNet, self).__init__()
            self.scale = scale
            self.conv_first = nn.Conv2d(num_in_ch, num_feat, 3, 1, 1)
            self.body = nn.Sequential(*[RRDB(num_feat, num_grow_ch) for _ in range(num_block)])
            self.conv_body = nn.Conv2d(num_feat, num_feat, 3, 1, 1)
            # upsample
            self.conv_up1 = nn.Conv2d(num_feat, num_feat, 3, 1, 1)
            self.conv_up2 = nn.Conv2d(num_feat, num_feat, 3, 1, 1)
            self.conv_hr = nn.Conv2d(num_feat, num_feat, 3, 1, 1)
            self.conv_last = nn.Conv2d(num_feat, num_out_ch, 3, 1, 1)
            self.lrelu = nn.LeakyReLU(negative_slope=0.2, inplace=True)

        def forward(self, x):
            feat = self.conv_first(x)
            body_feat = self.conv_body(self.body(feat))
            feat = feat + body_feat
            feat = self.lrelu(self.conv_up1(torch.nn.functional.interpolate(feat, scale_factor=2, mode='nearest')))
            feat = self.lrelu(self.conv_up2(torch.nn.functional.interpolate(feat, scale_factor=2, mode='nearest')))
            out = self.conv_last(self.lrelu(self.conv_hr(feat)))
            return out

    # 創建模型
    model = RRDBNet(num_in_ch=3, num_out_ch=3, scale=4, num_feat=64, num_block=num_block, num_grow_ch=32)

    # 加載權重
    print(f"加載模型權重: {model_path}")
    loadnet = torch.load(model_path, map_location=torch.device('cpu'), weights_only=False)
    if 'params_ema' in loadnet:
        keyname = 'params_ema'
    elif 'params' in loadnet:
        keyname = 'params'
    else:
        keyname = 'model'

    model.load_state_dict(loadnet[keyname] if keyname in loadnet else loadnet, strict=True)
    model.eval()
    model = model.to(device)

    return model


@torch.no_grad()
def upscale_frame(model, img, tile_size=512, device='cuda'):
    """
    使用tile策略upscale單幀
    """
    img = img.astype(np.float32) / 255.0
    img = torch.from_numpy(np.transpose(img, (2, 0, 1))).float()
    img = img.unsqueeze(0).to(device)

    # 簡單推理（不使用tile）
    if tile_size == 0:
        output = model(img)
    else:
        # 使用tile處理大圖
        b, c, h, w = img.size()
        output = torch.zeros((b, c, h * 4, w * 4), dtype=img.dtype, device=device)

        tiles_x = (w + tile_size - 1) // tile_size
        tiles_y = (h + tile_size - 1) // tile_size

        for i in range(tiles_y):
            for j in range(tiles_x):
                # 提取tile
                top = i * tile_size
                left = j * tile_size
                bottom = min((i + 1) * tile_size, h)
                right = min((j + 1) * tile_size, w)

                tile = img[:, :, top:bottom, left:right]

                # upscale tile
                tile_output = model(tile)

                # 放回輸出
                output[:, :, top*4:bottom*4, left*4:right*4] = tile_output

    output = output.squeeze(0).cpu().numpy()
    output = np.transpose(output, (1, 2, 0))
    output = np.clip(output * 255.0, 0, 255).astype(np.uint8)

    return output


def upscale_video_realesrgan_simple(
    input_video: str,
    output_video: str,
    model_path: str,
    num_block: int = 6,
    tile_size: int = 512,
    device: str = 'cuda'
):
    """
    簡化的Real-ESRGAN視頻upscale
    """
    print("="*80)
    print("Real-ESRGAN視頻Upscale - 簡化版")
    print("="*80)

    # 1. 加載模型
    print("\n步驟1: 加載Real-ESRGAN模型")
    print(f"  模型路徑: {model_path}")
    print(f"  Block數量: {num_block} ({'anime' if num_block == 6 else 'general'})")
    print(f"  Tile大小: {tile_size if tile_size > 0 else '無 (完整處理)'}")
    print(f"  設備: {device}")

    model = load_realesrgan_model(model_path, num_block=num_block, device=device)
    print("✓ 模型加載完成")

    # 2. 打開視頻
    print(f"\n步驟2: 讀取輸入視頻")
    print(f"  路徑: {input_video}")

    cap = cv2.VideoCapture(input_video)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    orig_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    orig_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    print(f"  分辨率: {orig_width}×{orig_height}")
    print(f"  FPS: {fps}")
    print(f"  總幀數: {frame_count}")

    # 3. 創建輸出視頻
    output_width = orig_width * 4
    output_height = orig_height * 4

    print(f"\n步驟3: 創建輸出視頻")
    print(f"  路徑: {output_video}")
    print(f"  分辨率: {output_width}×{output_height}")

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video, fourcc, fps, (output_width, output_height))

    if not out.isOpened():
        print("❌ 無法創建輸出視頻")
        cap.release()
        return

    # 4. 處理每一幀
    print(f"\n步驟4: 處理視頻幀 (4x upscale)")
    processed_frames = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Upscale
            upscaled_frame = upscale_frame(model, frame, tile_size=tile_size, device=device)

            # 寫入
            out.write(upscaled_frame)

            processed_frames += 1

            if processed_frames % 10 == 0:
                progress = (processed_frames / frame_count) * 100
                print(f"  進度: {processed_frames}/{frame_count} ({progress:.1f}%)")

    except Exception as e:
        print(f"❌ 處理錯誤: {e}")
        import traceback
        traceback.print_exc()

    finally:
        cap.release()
        out.release()

    # 5. 完成
    print(f"\n{'='*80}")
    print("✅ Upscale完成！")
    print(f"{'='*80}")
    print(f"輸出: {output_video}")
    print(f"分辨率: {output_width}×{output_height}")
    print(f"處理幀數: {processed_frames}/{frame_count}")

    if os.path.exists(output_video):
        file_size_mb = os.path.getsize(output_video) / (1024 * 1024)
        print(f"文件大小: {file_size_mb:.1f} MB")


def main():
    parser = argparse.ArgumentParser(description='Real-ESRGAN視頻Upscale - 簡化版')
    parser.add_argument('--input', required=True, help='輸入視頻路徑')
    parser.add_argument('--output', required=True, help='輸出視頻路徑')
    parser.add_argument('--model-path', default='/mnt/c/ai_models/upscale/RealESRGAN_x4plus_anime_6B.pth',
                       help='模型路徑')
    parser.add_argument('--model-type', default='anime', choices=['anime', 'general'],
                       help='模型類型 (anime=6 blocks, general=23 blocks)')
    parser.add_argument('--tile', type=int, default=512,
                       help='Tile大小 (0=不使用tile)')
    parser.add_argument('--device', default='cuda', help='設備 (cuda/cpu)')

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"❌ 輸入文件不存在: {args.input}")
        sys.exit(1)

    if not os.path.exists(args.model_path):
        print(f"❌ 模型文件不存在: {args.model_path}")
        sys.exit(1)

    # 創建輸出目錄
    os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)

    # 設置block數量
    num_block = 6 if args.model_type == 'anime' else 23

    upscale_video_realesrgan_simple(
        input_video=args.input,
        output_video=args.output,
        model_path=args.model_path,
        num_block=num_block,
        tile_size=args.tile,
        device=args.device
    )


if __name__ == '__main__':
    main()
