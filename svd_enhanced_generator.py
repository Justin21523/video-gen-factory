#!/usr/bin/env python3
"""SVD 增強版 Workflow Generator - 包含 Interpolation 和 Upscaling"""

import json
import copy
from pathlib import Path
from typing import Dict, Any, Optional

from vgf_paths import workflow_path


class SVDEnhancedGenerator:
    """SVD 增強版 workflow 生成器（包含幀插值和放大）"""

    def __init__(self, template_path: str = None):
        """初始化並載入增強版模板"""
        if template_path is None:
            template_path = str(workflow_path("svd_enhanced_template.json"))

        with open(template_path, 'r', encoding='utf-8') as f:
            self.template = json.load(f)

        print(f"✓ 載入 SVD 增強版 workflow 模板: {len(self.template)} 個節點")

    def generate_workflow(
        self,
        input_image: str,
        output_prefix: str,
        # SVD 參數
        width: int = 1024,
        height: int = 576,
        video_frames: int = 25,
        motion_bucket_id: int = 80,  # 降低默認值以提高穩定性（原127）
        base_fps: int = 16,
        augmentation_level: float = 0.0,  # 保持0以避免噪聲
        seed: int = 123456,
        steps: int = 25,  # 提高默認步數以提升質量（原20）
        cfg: float = 3.5,  # 提高CFG以更貼近輸入圖片（原2.5）
        model_name: str = "svd_xt.safetensors",
        # 穩定性模式
        stability_mode: str = "balanced",  # "high", "balanced", "creative"
        # 幀插值參數
        enable_interpolation: bool = True,
        interpolation_multiplier: int = 2,
        rife_model: str = "rife47.pth",
        # 放大參數
        enable_upscale: bool = True,
        upscale_model: str = "RealESRGAN_x4plus_anime_6B.pth",
        upscale_strategy: str = "2x+2x",  # "2x+2x", "4x", "2x"
        # 輸出參數
        output_fps: int = 30,
        output_crf: int = 17
    ) -> Dict[str, Any]:
        """
        生成增強版 SVD workflow

        SVD 參數:
            input_image: 輸入圖片路徑（僅檔名）
            output_prefix: 輸出視頻前綴
            width: 視頻寬度
            height: 視頻高度
            video_frames: 視頻幀數（SVD-XT 建議 25 幀）
            motion_bucket_id: 運動幅度 (1-255)
            base_fps: SVD 基礎幀率
            seed: 隨機種子
            steps: 採樣步數
            cfg: CFG 強度
            model_name: SVD 模型名稱

        幀插值參數:
            enable_interpolation: 是否啟用幀插值
            interpolation_multiplier: 插值倍數 (2 = 幀數翻倍)
            rife_model: RIFE 模型名稱

        放大參數:
            enable_upscale: 是否啟用放大
            upscale_model: 放大模型名稱
              - RealESRGAN_x4plus_anime_6B.pth: 4x 動畫風格（推薦 Pixar）
              - RealESRGAN_x4plus.pth: 4x 通用
              - RealESRGAN_x2plus.pth: 2x 通用

        輸出參數:
            output_fps: 最終輸出幀率
            output_crf: 視頻質量 (17=高質量, 23=默認)

        穩定性模式:
            high: 最高穩定性 - 角色/場景幾乎不變，微小動作
                  (motion_bucket_id=50, cfg=4.0, steps=30)
            balanced: 平衡模式 - 適度運動，保持一致性（默認）
                     (motion_bucket_id=80, cfg=3.5, steps=25)
            creative: 創意模式 - 較大運動和變化，可能不太穩定
                     (motion_bucket_id=150, cfg=2.5, steps=20)
        """
        # 根據穩定性模式調整參數
        stability_presets = {
            "high": {
                "motion_bucket_id": 50,
                "cfg": 4.0,
                "steps": 30,
                "description": "最高穩定性 - 微小動作，角色/場景高度一致"
            },
            "balanced": {
                "motion_bucket_id": 80,
                "cfg": 3.5,
                "steps": 25,
                "description": "平衡模式 - 適度運動，保持一致性"
            },
            "creative": {
                "motion_bucket_id": 150,
                "cfg": 2.5,
                "steps": 20,
                "description": "創意模式 - 較大運動和變化"
            }
        }

        # 如果指定了穩定性模式，覆蓋默認參數
        if stability_mode in stability_presets:
            preset = stability_presets[stability_mode]
            # 只在用戶沒有明確指定時才使用預設值
            if motion_bucket_id == 80:  # 默認值
                motion_bucket_id = preset["motion_bucket_id"]
            if cfg == 3.5:  # 默認值
                cfg = preset["cfg"]
            if steps == 25:  # 默認值
                steps = preset["steps"]

            print(f"✓ 使用穩定性模式: {stability_mode} - {preset['description']}")
            print(f"  motion_bucket_id={motion_bucket_id}, cfg={cfg}, steps={steps}")

        workflow = copy.deepcopy(self.template)

        # 節點 1: ImageOnlyCheckpointLoader - 載入 SVD 模型
        workflow['1']['inputs']['ckpt_name'] = model_name

        # 節點 2: LoadImage - 載入輸入圖片
        image_name = Path(input_image).name
        workflow['2']['inputs']['image'] = image_name

        # 節點 3: SVD_img2vid_Conditioning - 圖片到視頻條件
        workflow['3']['inputs']['width'] = width
        workflow['3']['inputs']['height'] = height
        workflow['3']['inputs']['video_frames'] = video_frames
        workflow['3']['inputs']['motion_bucket_id'] = motion_bucket_id
        workflow['3']['inputs']['fps'] = base_fps
        workflow['3']['inputs']['augmentation_level'] = augmentation_level

        # 節點 4: KSampler - 採樣器
        workflow['4']['inputs']['seed'] = seed
        workflow['4']['inputs']['steps'] = steps
        workflow['4']['inputs']['cfg'] = cfg

        # 根據設置調整工作流
        last_image_node = "5"  # VAEDecode 輸出

        # 如果啟用幀插值
        if enable_interpolation:
            workflow['6']['inputs']['frames'] = [last_image_node, 0]
            workflow['6']['inputs']['multiplier'] = interpolation_multiplier
            workflow['6']['inputs']['ckpt_name'] = rife_model
            last_image_node = "6"
        else:
            # 移除 RIFE 節點
            if '6' in workflow:
                del workflow['6']

        # 如果啟用放大
        if enable_upscale:
            workflow['8']['inputs']['model_name'] = upscale_model
            workflow['7']['inputs']['image'] = [last_image_node, 0]
            last_image_node = "7"
        else:
            # 移除 upscale 節點
            if '7' in workflow:
                del workflow['7']
            if '8' in workflow:
                del workflow['8']

        # 節點 9: VHS_VideoCombine - 視頻輸出
        workflow['9']['inputs']['images'] = [last_image_node, 0]
        workflow['9']['inputs']['frame_rate'] = output_fps
        workflow['9']['inputs']['filename_prefix'] = output_prefix
        workflow['9']['inputs']['crf'] = output_crf

        return workflow

    def save_workflow(self, workflow: Dict[str, Any], output_path: str):
        """保存 workflow 到文件"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(workflow, f, indent=2, ensure_ascii=False)
        print(f"✓ 保存 workflow 到: {output_path}")


def main():
    """測試生成器"""
    generator = SVDEnhancedGenerator()

    print("\n" + "="*80)
    print("🎬 SVD 增強版 Workflow 生成器")
    print("="*80)

    # 測試 1: 完整增強版（插值 + 放大）
    print("\n1️⃣  測試完整增強版（interpolation + upscaling）")
    workflow_full = generator.generate_workflow(
        input_image="test.png",
        output_prefix="svd_full_enhanced",
        motion_bucket_id=127,
        enable_interpolation=True,
        interpolation_multiplier=2,
        enable_upscale=True,
        upscale_model="RealESRGAN_x4plus_anime_6B.pth",
        output_fps=30
    )
    generator.save_workflow(
        workflow_full,
        str(workflow_path("svd_full_enhanced.json"))
    )
    print(f"   節點數: {len(workflow_full)}")
    print(f"   流程: SVD → RIFE (2x) → Real-ESRGAN (4x) → 輸出")

    # 測試 2: 僅插值（不放大）
    print("\n2️⃣  測試僅幀插值（interpolation only）")
    workflow_interp = generator.generate_workflow(
        input_image="test.png",
        output_prefix="svd_interp_only",
        enable_interpolation=True,
        interpolation_multiplier=3,
        enable_upscale=False,
        output_fps=48
    )
    generator.save_workflow(
        workflow_interp,
        str(workflow_path("svd_interp_only.json"))
    )
    print(f"   節點數: {len(workflow_interp)}")
    print(f"   流程: SVD → RIFE (3x) → 輸出")

    # 測試 3: 僅放大（不插值）
    print("\n3️⃣  測試僅放大（upscaling only）")
    workflow_upscale = generator.generate_workflow(
        input_image="test.png",
        output_prefix="svd_upscale_only",
        enable_interpolation=False,
        enable_upscale=True,
        upscale_model="RealESRGAN_x2plus.pth",
        output_fps=16
    )
    generator.save_workflow(
        workflow_upscale,
        str(workflow_path("svd_upscale_only.json"))
    )
    print(f"   節點數: {len(workflow_upscale)}")
    print(f"   流程: SVD → Real-ESRGAN (2x) → 輸出")

    print("\n" + "="*80)
    print("📊 質量提升預估")
    print("="*80)
    print("完整增強版:")
    print("  輸入: 圖片")
    print("  SVD 生成: 1024×576, 25 幀, 16fps")
    print("  RIFE 插值: 1024×576, 50 幀, 30fps (流暢度 +100%)")
    print("  ESRGAN 放大: 4096×2304, 50 幀, 30fps (分辨率 +1600%)")
    print("  最終質量: ⭐⭐⭐⭐⭐")
    print("\n注意:")
    print("  - 完整流程需要更多 VRAM 和時間")
    print("  - 單個視頻處理時間: 2-5 分鐘（視 GPU 而定）")
    print("  - 420 個視頻預計: 14-35 小時")


if __name__ == '__main__':
    main()
