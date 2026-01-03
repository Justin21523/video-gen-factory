#!/usr/bin/env python3
"""SVD Workflow Generator - 為 Stable Video Diffusion 生成 ComfyUI workflows"""

import json
import copy
from pathlib import Path
from typing import Dict, Any, Optional

from vgf_paths import workflow_path


class SVDWorkflowGenerator:
    """SVD workflow 生成器"""

    def __init__(self, template_path: str = None):
        """初始化並載入 SVD 模板"""
        if template_path is None:
            template_path = str(workflow_path("svd_template.json"))

        with open(template_path, 'r', encoding='utf-8') as f:
            self.template = json.load(f)

        print(f"✓ 載入 SVD workflow 模板: {len(self.template)} 個節點")

    def generate_workflow(
        self,
        input_image: str,
        output_prefix: str,
        width: int = 1024,
        height: int = 576,
        video_frames: int = 25,
        motion_bucket_id: int = 127,
        fps: int = 16,
        augmentation_level: float = 0.0,
        seed: int = 123456,
        steps: int = 20,
        cfg: float = 2.5,
        model_name: str = "svd_xt_1_1.safetensors"
    ) -> Dict[str, Any]:
        """
        生成 SVD workflow

        參數:
            input_image: 輸入圖片路徑（僅檔名）
            output_prefix: 輸出視頻前綴
            width: 視頻寬度
            height: 視頻高度
            video_frames: 視頻幀數（SVD-XT 建議 25 幀）
            motion_bucket_id: 運動幅度 (1-255, 127 為中等運動)
            fps: 幀率
            augmentation_level: 增強級別 (0.0-1.0)
            seed: 隨機種子
            steps: 採樣步數
            cfg: CFG 強度
            model_name: SVD 模型名稱
        """
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
        workflow['3']['inputs']['fps'] = fps
        workflow['3']['inputs']['augmentation_level'] = augmentation_level

        # 節點 4: KSampler - 採樣器
        workflow['4']['inputs']['seed'] = seed
        workflow['4']['inputs']['steps'] = steps
        workflow['4']['inputs']['cfg'] = cfg

        # 節點 6: VHS_VideoCombine - 視頻輸出
        workflow['6']['inputs']['frame_rate'] = fps
        workflow['6']['inputs']['filename_prefix'] = output_prefix

        return workflow

    def save_workflow(self, workflow: Dict[str, Any], output_path: str):
        """保存 workflow 到文件"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(workflow, f, indent=2, ensure_ascii=False)
        print(f"✓ 保存 workflow 到: {output_path}")


def main():
    """測試生成器"""
    generator = SVDWorkflowGenerator()

    # 生成測試 workflow
    workflow = generator.generate_workflow(
        input_image="test_image.png",
        output_prefix="svd_test",
        motion_bucket_id=127,
        seed=42
    )

    # 保存
    output_path = str(workflow_path("svd_test_workflow.json"))
    generator.save_workflow(workflow, output_path)

    print("\n📊 SVD Workflow 參數說明:")
    print("  motion_bucket_id: 控制運動幅度")
    print("    - 1-50: 微小運動（適合靜態場景）")
    print("    - 51-127: 中等運動（推薦，默認值）")
    print("    - 128-200: 較大運動（適合動作場景）")
    print("    - 201-255: 極大運動（可能不穩定）")
    print("  video_frames: SVD-XT 支援最多 25 幀")
    print("  augmentation_level: 增加多樣性，但可能降低質量")


if __name__ == '__main__':
    main()
