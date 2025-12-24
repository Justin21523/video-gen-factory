#!/usr/bin/env python3
"""
分段拼接脚本 - 用于长片段（>5秒）的无缝拼接

功能：
1. 将长视频分段生成后的片段进行overlap blending
2. 使用FFmpeg进行最终拼接
3. 支持帧级别的alpha混合过渡

适用场景：
- 超过120帧（5秒@24fps）的长片段
- VRAM不足以一次性生成完整序列
- 需要保持时序一致性的无缝拼接

作者：LLMProvider (AI Assistant)
日期：2025-12
"""

import os
import sys
import argparse
import subprocess
import logging
from pathlib import Path
from PIL import Image
import numpy as np
from typing import List, Tuple
from datetime import datetime

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =============================================================================
# 帧级别Overlap Blending
# =============================================================================

def load_frames_from_directory(frames_dir: Path, pattern: str = "frame_*.png") -> List[Path]:
    """加载目录中的所有帧图片

    Args:
        frames_dir: 帧图片目录
        pattern: 文件名模式

    Returns:
        排序后的帧路径列表
    """
    frames = sorted(frames_dir.glob(pattern))
    logger.info(f"从 {frames_dir} 加载了 {len(frames)} 帧")
    return frames

def blend_overlap_frames(
    segment1_frames: List[Path],
    segment2_frames: List[Path],
    overlap_count: int = 16,
    output_dir: Path = None,
    blend_mode: str = "linear"
) -> List[Path]:
    """混合两个片段的重叠区域

    Args:
        segment1_frames: 第一段的帧路径列表
        segment2_frames: 第二段的帧路径列表
        overlap_count: 重叠帧数
        output_dir: 混合后帧的输出目录
        blend_mode: 混合模式（linear/cosine/cubic）

    Returns:
        混合后的完整帧路径列表
    """
    if len(segment1_frames) < overlap_count:
        logger.error(f"第一段帧数 ({len(segment1_frames)}) 小于overlap数 ({overlap_count})")
        return []

    if len(segment2_frames) < overlap_count:
        logger.error(f"第二段帧数 ({len(segment2_frames)}) 小于overlap数 ({overlap_count})")
        return []

    # 创建输出目录
    if output_dir is None:
        output_dir = Path("./blended_frames")
    output_dir.mkdir(parents=True, exist_ok=True)

    # 提取重叠区域
    seg1_overlap_frames = segment1_frames[-overlap_count:]
    seg2_overlap_frames = segment2_frames[:overlap_count]

    logger.info(f"混合 {overlap_count} 帧的重叠区域...")
    logger.info(f"Segment1 overlap: frame {len(segment1_frames)-overlap_count} - {len(segment1_frames)-1}")
    logger.info(f"Segment2 overlap: frame 0 - {overlap_count-1}")

    # 混合权重计算
    def get_blend_weight(i: int, total: int, mode: str = "linear") -> float:
        """计算混合权重

        Args:
            i: 当前帧索引（0到total-1）
            total: 总帧数
            mode: linear（线性）/ cosine（余弦平滑）/ cubic（三次平滑）

        Returns:
            segment2的权重（0.0到1.0）
        """
        if mode == "linear":
            return i / (total - 1)
        elif mode == "cosine":
            # 使用cosine进行平滑过渡
            t = i / (total - 1)
            return (1 - np.cos(t * np.pi)) / 2
        elif mode == "cubic":
            # 使用cubic ease-in-out
            t = i / (total - 1)
            if t < 0.5:
                return 4 * t * t * t
            else:
                return 1 - pow(-2 * t + 2, 3) / 2
        else:
            return i / (total - 1)

    # 混合重叠帧
    blended_frames = []

    for i in range(overlap_count):
        # 加载两帧
        img1 = Image.open(seg1_overlap_frames[i]).convert("RGB")
        img2 = Image.open(seg2_overlap_frames[i]).convert("RGB")

        # 确保尺寸一致
        if img1.size != img2.size:
            logger.warning(f"帧 {i} 尺寸不一致: {img1.size} vs {img2.size}，调整为相同尺寸")
            img2 = img2.resize(img1.size, Image.LANCZOS)

        # 计算权重
        weight_seg2 = get_blend_weight(i, overlap_count, blend_mode)
        weight_seg1 = 1 - weight_seg2

        # Alpha混合
        arr1 = np.array(img1, dtype=np.float32)
        arr2 = np.array(img2, dtype=np.float32)
        blended_arr = (arr1 * weight_seg1 + arr2 * weight_seg2).astype(np.uint8)

        blended_img = Image.fromarray(blended_arr)

        # 保存混合帧
        output_frame_path = output_dir / f"blended_{i:04d}.png"
        blended_img.save(output_frame_path, compress_level=1)
        blended_frames.append(output_frame_path)

        if (i + 1) % 4 == 0 or i == overlap_count - 1:
            logger.info(f"  混合进度: {i+1}/{overlap_count} (权重: seg1={weight_seg1:.2f}, seg2={weight_seg2:.2f})")

    # 组合完整序列
    # Segment1的前面部分（不包括overlap）
    final_frames = segment1_frames[:-overlap_count]
    # 混合后的overlap部分
    final_frames.extend(blended_frames)
    # Segment2的后面部分（不包括overlap）
    final_frames.extend(segment2_frames[overlap_count:])

    logger.info(f"✓ 混合完成:")
    logger.info(f"  Segment1 前部: {len(segment1_frames) - overlap_count} 帧")
    logger.info(f"  混合区域: {len(blended_frames)} 帧")
    logger.info(f"  Segment2 后部: {len(segment2_frames) - overlap_count} 帧")
    logger.info(f"  总计: {len(final_frames)} 帧")

    return final_frames

# =============================================================================
# FFmpeg视频拼接
# =============================================================================

def frames_to_video(
    frame_paths: List[Path],
    output_video: Path,
    fps: int = 24,
    codec: str = "libx264",
    quality: str = "high",
    bitrate: str = "8M"
) -> bool:
    """使用FFmpeg将帧序列转换为视频

    Args:
        frame_paths: 帧路径列表
        output_video: 输出视频路径
        fps: 帧率
        codec: 视频编码器
        quality: 质量预设（high/medium/low）
        bitrate: 目标比特率

    Returns:
        bool: 成功返回True
    """
    if not frame_paths:
        logger.error("帧列表为空")
        return False

    # 创建临时文件列表（FFmpeg concat）
    temp_dir = Path("/tmp/ffmpeg_concat")
    temp_dir.mkdir(parents=True, exist_ok=True)

    list_file = temp_dir / f"frames_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    # 写入帧列表
    with open(list_file, 'w') as f:
        for frame_path in frame_paths:
            f.write(f"file '{frame_path.absolute()}'\n")
            f.write(f"duration {1/fps}\n")
        # 最后一帧需要特殊处理
        f.write(f"file '{frame_paths[-1].absolute()}'\n")

    logger.info(f"创建FFmpeg输入列表: {list_file}")
    logger.info(f"总帧数: {len(frame_paths)}, FPS: {fps}, 时长: {len(frame_paths)/fps:.2f}秒")

    # CRF质量映射
    crf_map = {
        "high": 18,
        "medium": 23,
        "low": 28
    }
    crf = crf_map.get(quality, 18)

    # FFmpeg命令
    cmd = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", str(list_file),
        "-c:v", codec,
        "-crf", str(crf),
        "-b:v", bitrate,
        "-r", str(fps),
        "-pix_fmt", "yuv420p",
        "-y",  # 覆盖输出文件
        str(output_video)
    ]

    logger.info(f"执行FFmpeg命令:")
    logger.info(f"  {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )

        logger.info("✓ 视频生成成功")
        logger.info(f"  输出: {output_video}")

        # 获取文件大小
        size_mb = output_video.stat().st_size / (1024 * 1024)
        logger.info(f"  文件大小: {size_mb:.2f} MB")

        # 清理临时文件
        list_file.unlink()

        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg执行失败:")
        logger.error(f"  返回码: {e.returncode}")
        logger.error(f"  STDOUT: {e.stdout}")
        logger.error(f"  STDERR: {e.stderr}")
        return False

# =============================================================================
# 多段拼接工作流
# =============================================================================

def blend_multiple_segments(
    segment_dirs: List[Path],
    output_video: Path,
    overlap_count: int = 16,
    fps: int = 24,
    blend_mode: str = "cosine",
    keep_blended_frames: bool = False
) -> bool:
    """拼接多个视频片段

    Args:
        segment_dirs: 片段目录列表（每个目录包含frame_*.png）
        output_video: 输出视频路径
        overlap_count: 重叠帧数
        fps: 输出帧率
        blend_mode: 混合模式
        keep_blended_frames: 是否保留混合后的帧

    Returns:
        bool: 成功返回True
    """
    if len(segment_dirs) < 2:
        logger.error("至少需要2个片段才能拼接")
        return False

    logger.info(f"\n{'='*80}")
    logger.info(f"开始拼接 {len(segment_dirs)} 个片段")
    logger.info(f"Overlap: {overlap_count} 帧, 混合模式: {blend_mode}")
    logger.info(f"{'='*80}\n")

    # 加载所有片段的帧
    all_segment_frames = []
    for i, seg_dir in enumerate(segment_dirs, 1):
        frames = load_frames_from_directory(seg_dir)
        if not frames:
            logger.error(f"片段 {i} ({seg_dir}) 没有找到帧")
            return False
        all_segment_frames.append(frames)
        logger.info(f"Segment {i}: {len(frames)} 帧")

    # 逐对混合
    current_frames = all_segment_frames[0]

    for i in range(1, len(all_segment_frames)):
        logger.info(f"\n混合 Segment {i} 和 Segment {i+1}...")

        blended_frames = blend_overlap_frames(
            current_frames,
            all_segment_frames[i],
            overlap_count=overlap_count,
            output_dir=Path(f"./blended_{i-1}_{i}"),
            blend_mode=blend_mode
        )

        if not blended_frames:
            logger.error("混合失败")
            return False

        current_frames = blended_frames

    logger.info(f"\n最终序列: {len(current_frames)} 帧")

    # 生成视频
    success = frames_to_video(
        current_frames,
        output_video,
        fps=fps
    )

    # 清理临时文件
    if not keep_blended_frames:
        logger.info("清理临时混合帧...")
        for i in range(len(all_segment_frames) - 1):
            temp_dir = Path(f"./blended_{i}_{i+1}")
            if temp_dir.exists():
                import shutil
                shutil.rmtree(temp_dir)

    return success

# =============================================================================
# 命令行接口
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="分段拼接脚本 - 无缝混合长视频片段",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:

  # 拼接两个片段目录
  python overlap_blend.py \
    --segments ./segment_01 ./segment_02 \
    --output ./output/final_video.mp4 \
    --overlap 16 \
    --fps 24

  # 拼接三个片段，使用余弦混合
  python overlap_blend.py \
    --segments ./seg1 ./seg2 ./seg3 \
    --output ./final.mp4 \
    --overlap 20 \
    --blend-mode cosine \
    --keep-frames

混合模式说明:
  - linear: 线性插值（最快，适合相似帧）
  - cosine: 余弦平滑过渡（推荐，平滑自然）
  - cubic: 三次ease-in-out（最平滑，适合差异较大的帧）
        """
    )

    parser.add_argument(
        "--segments",
        nargs="+",
        type=Path,
        required=True,
        help="片段目录列表（包含frame_*.png）"
    )

    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="输出视频路径"
    )

    parser.add_argument(
        "--overlap",
        type=int,
        default=16,
        help="重叠帧数（默认16）"
    )

    parser.add_argument(
        "--fps",
        type=int,
        default=24,
        help="输出帧率（默认24）"
    )

    parser.add_argument(
        "--blend-mode",
        choices=["linear", "cosine", "cubic"],
        default="cosine",
        help="混合模式（默认cosine）"
    )

    parser.add_argument(
        "--keep-frames",
        action="store_true",
        help="保留混合后的帧（用于调试）"
    )

    args = parser.parse_args()

    # 验证片段目录
    for seg_dir in args.segments:
        if not seg_dir.exists():
            logger.error(f"片段目录不存在: {seg_dir}")
            sys.exit(1)

    # 执行拼接
    success = blend_multiple_segments(
        segment_dirs=args.segments,
        output_video=args.output,
        overlap_count=args.overlap,
        fps=args.fps,
        blend_mode=args.blend_mode,
        keep_blended_frames=args.keep_frames
    )

    if success:
        logger.info("\n" + "="*80)
        logger.info("✓ 拼接完成！")
        logger.info("="*80)
        sys.exit(0)
    else:
        logger.error("\n" + "="*80)
        logger.error("✗ 拼接失败")
        logger.error("="*80)
        sys.exit(1)

if __name__ == "__main__":
    main()
