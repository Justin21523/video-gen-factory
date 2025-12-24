#!/usr/bin/env python3
"""
批次处理脚本 - 自动化处理多段3D动画序列
针对 ComfyUI + AnimateDiff 工作流

功能：
1. 扫描input_sequences目录下的所有场景文件夹
2. 读取style_presets.yaml配置
3. 通过ComfyUI API批量提交任务
4. 生成符合命名规范的输出视频
5. 记录处理日志和VRAM统计

作者：LLMProvider (AI Assistant)
日期：2025-12
"""

import os
import sys
import json
import yaml
import requests
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import argparse

# =============================================================================
# 配置部分
# =============================================================================

# ComfyUI API地址
COMFYUI_API_URL = "http://127.0.0.1:8188"

# 项目路径
PROJECT_ROOT = Path(__file__).parent.parent
INPUT_DIR = PROJECT_ROOT / "input_sequences"
OUTPUT_DIR = PROJECT_ROOT / "output_videos"
CONFIG_DIR = PROJECT_ROOT / "config"
WORKFLOW_DIR = PROJECT_ROOT / "workflows"
LOG_DIR = PROJECT_ROOT / "logs"

# 配置文件路径
STYLE_PRESETS_PATH = CONFIG_DIR / "style_presets.yaml"

# Workflow模板文件
WORKFLOW_TEMPLATES = {
    "stable": WORKFLOW_DIR / "workflow_A_stable.json",
    "cinematic": WORKFLOW_DIR / "workflow_B_cinematic.json"
}

# =============================================================================
# 日志配置
# =============================================================================

def setup_logger(log_file: Optional[str] = None) -> logging.Logger:
    """配置日志记录器"""
    LOG_DIR.mkdir(exist_ok=True)

    if log_file is None:
        log_file = LOG_DIR / f"batch_process_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    logger = logging.getLogger("BatchProcessor")
    logger.setLevel(logging.INFO)

    # 控制台handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_format)

    # 文件handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_format)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

logger = setup_logger()

# =============================================================================
# ComfyUI API接口
# =============================================================================

class ComfyUIClient:
    """ComfyUI API客户端"""

    def __init__(self, api_url: str = COMFYUI_API_URL):
        self.api_url = api_url
        self.session = requests.Session()

    def check_connection(self) -> bool:
        """检查ComfyUI是否在线"""
        try:
            response = self.session.get(f"{self.api_url}/system_stats")
            return response.status_code == 200
        except requests.exceptions.ConnectionError:
            return False

    def submit_prompt(self, workflow: Dict) -> Optional[str]:
        """提交workflow到队列

        Args:
            workflow: ComfyUI workflow JSON

        Returns:
            prompt_id: 任务ID，失败返回None
        """
        try:
            payload = {"prompt": workflow}
            response = self.session.post(
                f"{self.api_url}/prompt",
                json=payload,
                timeout=10
            )
            response.raise_for_status()

            result = response.json()
            prompt_id = result.get("prompt_id")

            if prompt_id:
                logger.info(f"任务提交成功，Prompt ID: {prompt_id}")
            else:
                logger.error(f"任务提交失败：{result}")

            return prompt_id

        except Exception as e:
            logger.error(f"提交任务时出错: {e}")
            return None

    def get_queue_info(self) -> Dict:
        """获取队列信息"""
        try:
            response = self.session.get(f"{self.api_url}/queue")
            return response.json()
        except Exception as e:
            logger.error(f"获取队列信息失败: {e}")
            return {}

    def get_history(self, prompt_id: str) -> Dict:
        """获取任务历史记录"""
        try:
            response = self.session.get(f"{self.api_url}/history/{prompt_id}")
            return response.json()
        except Exception as e:
            logger.error(f"获取任务历史失败: {e}")
            return {}

    def wait_for_completion(self, prompt_id: str, timeout: int = 3600) -> bool:
        """等待任务完成

        Args:
            prompt_id: 任务ID
            timeout: 超时时间（秒）

        Returns:
            bool: 成功完成返回True，失败或超时返回False
        """
        start_time = time.time()

        while True:
            if time.time() - start_time > timeout:
                logger.error(f"任务 {prompt_id} 超时（{timeout}秒）")
                return False

            history = self.get_history(prompt_id)

            if prompt_id in history:
                status = history[prompt_id].get("status", {})

                if status.get("completed", False):
                    logger.info(f"任务 {prompt_id} 完成")
                    return True

                if "error" in status:
                    logger.error(f"任务 {prompt_id} 失败: {status['error']}")
                    return False

            # 检查队列状态
            queue_info = self.get_queue_info()
            queue_running = queue_info.get("queue_running", [])
            queue_pending = queue_info.get("queue_pending", [])

            # 如果任务既不在运行也不在等待，可能已完成或失败
            running_ids = [item[1] for item in queue_running]
            pending_ids = [item[1] for item in queue_pending]

            if prompt_id not in running_ids and prompt_id not in pending_ids:
                # 再次检查历史确认
                time.sleep(2)
                history = self.get_history(prompt_id)
                if prompt_id in history:
                    logger.info(f"任务 {prompt_id} 已完成")
                    return True

            time.sleep(5)  # 每5秒检查一次

# =============================================================================
# 配置加载
# =============================================================================

def load_style_presets() -> Dict:
    """加载风格配置文件"""
    try:
        with open(STYLE_PRESETS_PATH, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"加载风格配置文件失败: {e}")
        sys.exit(1)

def load_workflow_template(template_type: str = "stable") -> Dict:
    """加载workflow模板"""
    template_path = WORKFLOW_TEMPLATES.get(template_type)

    if not template_path or not template_path.exists():
        logger.error(f"Workflow模板不存在: {template_path}")
        logger.warning("请先在ComfyUI中手动构建workflow并导出JSON到workflows目录")
        sys.exit(1)

    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"加载workflow模板失败: {e}")
        sys.exit(1)

# =============================================================================
# Workflow定制化
# =============================================================================

def customize_workflow(
    workflow: Dict,
    scene_path: Path,
    style_config: Dict,
    output_path: Path,
    resolution: str = "768x432"
) -> Dict:
    """定制化workflow参数

    Args:
        workflow: 原始workflow模板
        scene_path: 输入图片序列路径
        style_config: 风格配置
        output_path: 输出视频路径
        resolution: 目标分辨率

    Returns:
        定制化后的workflow

    注意: 此函数需要根据实际的workflow结构调整节点ID和参数路径
    """
    # 警告：以下节点ID需要根据实际workflow调整
    logger.warning("注意：此函数中的节点ID是示例，需要根据实际workflow.json调整！")

    # 这里是示例逻辑，实际需要根据workflow_A_stable.json的结构修改
    # 通常需要修改的节点：
    # - LoadImageSequence: 输入路径
    # - KSampler: denoise, cfg, steps, seed
    # - AnimateDiff: context_length
    # - ControlNet: 权重
    # - SaveVideo: 输出路径

    params = style_config.get("parameters", {})

    # 示例：修改参数（需要根据实际workflow结构调整）
    # workflow["nodes"]["KSampler"]["inputs"]["denoise"] = params.get("denoise", 0.5)
    # workflow["nodes"]["KSampler"]["inputs"]["cfg"] = params.get("cfg_scale", 7.0)
    # workflow["nodes"]["KSampler"]["inputs"]["steps"] = params.get("steps", 20)
    # ...

    logger.info(f"已定制workflow：场景={scene_path.name}, 风格={style_config.get('description')}")

    return workflow

# =============================================================================
# 场景扫描
# =============================================================================

def scan_input_sequences() -> List[Path]:
    """扫描输入目录，返回所有场景文件夹"""
    if not INPUT_DIR.exists():
        logger.error(f"输入目录不存在: {INPUT_DIR}")
        return []

    scenes = [d for d in INPUT_DIR.iterdir() if d.is_dir()]

    logger.info(f"找到 {len(scenes)} 个场景文件夹")
    for scene in scenes:
        frame_count = len(list(scene.glob("*.png"))) + len(list(scene.glob("*.jpg")))
        logger.info(f"  - {scene.name}: {frame_count} 帧")

    return scenes

def validate_scene_frames(scene_path: Path) -> bool:
    """验证场景帧序列完整性"""
    frames = sorted(scene_path.glob("frame_*.png")) + sorted(scene_path.glob("frame_*.jpg"))

    if len(frames) == 0:
        logger.warning(f"场景 {scene_path.name} 没有找到帧图片")
        return False

    # 检查命名规范（frame_0001.png格式）
    expected_pattern = r"frame_\d{4}\.(png|jpg)"
    import re

    for frame in frames[:5]:  # 检查前5帧
        if not re.match(expected_pattern, frame.name):
            logger.warning(f"场景 {scene_path.name} 的帧命名不符合规范: {frame.name}")
            logger.warning("建议格式：frame_0001.png, frame_0002.png, ...")
            return False

    logger.info(f"场景 {scene_path.name} 验证通过：{len(frames)} 帧")
    return True

# =============================================================================
# 输出命名
# =============================================================================

def generate_output_filename(scene_name: str, style: str, resolution: str) -> str:
    """生成输出文件名

    格式: {scene_name}_{style}_{resolution}_{timestamp}.mp4
    例如: scene_01_kitchen_S2_1280x720_20250120_143052.mp4
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{scene_name}_{style}_{resolution}_{timestamp}.mp4"

# =============================================================================
# 批次处理主逻辑
# =============================================================================

def process_single_scene(
    client: ComfyUIClient,
    scene_path: Path,
    style: str,
    resolution: str,
    workflow_type: str = "stable",
    dry_run: bool = False
) -> bool:
    """处理单个场景

    Args:
        client: ComfyUI客户端
        scene_path: 场景路径
        style: 风格名称（S1_conservative/S2_balanced/S3_aggressive）
        resolution: 分辨率（512x288/768x432/1024x576/1280x720）
        workflow_type: workflow类型（stable/cinematic）
        dry_run: 仅模拟不实际提交

    Returns:
        bool: 成功返回True
    """
    logger.info(f"\n{'='*80}")
    logger.info(f"开始处理场景: {scene_path.name}")
    logger.info(f"  风格: {style}")
    logger.info(f"  分辨率: {resolution}")
    logger.info(f"  Workflow: {workflow_type}")
    logger.info(f"{'='*80}\n")

    # 验证场景
    if not validate_scene_frames(scene_path):
        return False

    # 加载配置
    presets = load_style_presets()
    style_config = presets.get(style)

    if not style_config:
        logger.error(f"风格配置不存在: {style}")
        return False

    # 加载workflow模板
    workflow = load_workflow_template(workflow_type)

    # 生成输出文件名
    OUTPUT_DIR.mkdir(exist_ok=True)
    output_filename = generate_output_filename(scene_path.name, style, resolution)
    output_path = OUTPUT_DIR / output_filename

    # 定制化workflow
    workflow = customize_workflow(
        workflow,
        scene_path,
        style_config,
        output_path,
        resolution
    )

    if dry_run:
        logger.info("[DRY RUN] 跳过实际提交")
        logger.info(f"输出文件: {output_path}")
        return True

    # 提交任务
    prompt_id = client.submit_prompt(workflow)

    if not prompt_id:
        logger.error("任务提交失败")
        return False

    # 等待完成
    logger.info("等待任务完成...")
    success = client.wait_for_completion(prompt_id, timeout=3600)

    if success:
        logger.info(f"✓ 场景 {scene_path.name} 处理成功")
        logger.info(f"  输出: {output_path}")
    else:
        logger.error(f"✗ 场景 {scene_path.name} 处理失败")

    return success

def batch_process(
    styles: List[str],
    resolutions: List[str],
    workflow_type: str = "stable",
    dry_run: bool = False,
    sequential: bool = True
):
    """批次处理所有场景

    Args:
        styles: 风格列表（例如 ["S1_conservative", "S2_balanced"]）
        resolutions: 分辨率列表（例如 ["768x432", "1024x576"]）
        workflow_type: workflow类型
        dry_run: 仅模拟
        sequential: 顺序处理（True）或并行提交（False，不推荐16GB VRAM）
    """
    logger.info("\n" + "="*80)
    logger.info("批次处理开始")
    logger.info("="*80 + "\n")

    # 检查ComfyUI连接
    client = ComfyUIClient()

    if not client.check_connection():
        logger.error("无法连接到ComfyUI，请确保ComfyUI正在运行（http://127.0.0.1:8188）")
        sys.exit(1)

    logger.info("✓ ComfyUI连接成功")

    # 扫描场景
    scenes = scan_input_sequences()

    if not scenes:
        logger.warning("没有找到需要处理的场景")
        return

    # 生成任务列表
    tasks = []
    for scene in scenes:
        for style in styles:
            for resolution in resolutions:
                tasks.append({
                    "scene": scene,
                    "style": style,
                    "resolution": resolution
                })

    logger.info(f"\n总共 {len(tasks)} 个任务:")
    for i, task in enumerate(tasks, 1):
        logger.info(f"  {i}. {task['scene'].name} - {task['style']} - {task['resolution']}")

    # 执行任务
    success_count = 0
    fail_count = 0

    start_time = time.time()

    for i, task in enumerate(tasks, 1):
        logger.info(f"\n进度: {i}/{len(tasks)}")

        success = process_single_scene(
            client,
            task["scene"],
            task["style"],
            task["resolution"],
            workflow_type,
            dry_run
        )

        if success:
            success_count += 1
        else:
            fail_count += 1

        # 清理VRAM（如果支持）
        time.sleep(2)

    elapsed_time = time.time() - start_time

    # 最终报告
    logger.info("\n" + "="*80)
    logger.info("批次处理完成")
    logger.info("="*80)
    logger.info(f"总任务数: {len(tasks)}")
    logger.info(f"成功: {success_count}")
    logger.info(f"失败: {fail_count}")
    logger.info(f"耗时: {elapsed_time/60:.1f} 分钟")
    logger.info("="*80 + "\n")

# =============================================================================
# 命令行接口
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="ComfyUI + AnimateDiff 批次处理脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:

  # 处理所有场景，使用S2风格，768x432分辨率
  python batch_processor.py --style S2_balanced --resolution 768x432

  # 处理所有场景，使用S1和S2风格，多个分辨率
  python batch_processor.py --style S1_conservative S2_balanced --resolution 512x288 768x432

  # 仅模拟运行，不实际提交
  python batch_processor.py --style S2_balanced --resolution 768x432 --dry-run

  # 使用电影风格workflow
  python batch_processor.py --style S3_aggressive --resolution 768x432 --workflow cinematic
        """
    )

    parser.add_argument(
        "--style",
        nargs="+",
        choices=["S1_conservative", "S2_balanced", "S3_aggressive"],
        default=["S2_balanced"],
        help="风格列表（可多选）"
    )

    parser.add_argument(
        "--resolution",
        nargs="+",
        choices=["512x288", "768x432", "1024x576", "1280x720"],
        default=["768x432"],
        help="分辨率列表（可多选）"
    )

    parser.add_argument(
        "--workflow",
        choices=["stable", "cinematic"],
        default="stable",
        help="Workflow类型"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅模拟运行，不实际提交任务"
    )

    args = parser.parse_args()

    # 运行批次处理
    batch_process(
        styles=args.style,
        resolutions=args.resolution,
        workflow_type=args.workflow,
        dry_run=args.dry_run
    )

if __name__ == "__main__":
    main()
