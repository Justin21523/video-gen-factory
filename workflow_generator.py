#!/usr/bin/env python3
"""
ComfyUI Workflow Generator (API Format)
自動產生 CogVideoX I2V workflow based on character config
"""

import json
import copy
from pathlib import Path
from typing import Dict, Any


class WorkflowGenerator:
    def __init__(self, template_path: str):
        """載入並轉換基礎 workflow 模板為 API 格式"""
        with open(template_path, 'r', encoding='utf-8') as f:
            ui_workflow = json.load(f)

        # 轉換為 API 格式
        self.template = self._convert_ui_to_api(ui_workflow)
        print(f"✓ 載入 workflow 模板: {len(self.template)} 個節點")

    def _convert_ui_to_api(self, ui_workflow: Dict[str, Any]) -> Dict[str, Any]:
        """將 UI workflow 格式轉換為 API 格式"""
        api_workflow = {}

        # 建立 link 索引
        links_by_id = {}
        for link in ui_workflow.get('links', []):
            link_id = link[0]
            links_by_id[link_id] = {
                'source_node': link[1],
                'source_slot': link[2],
            }

        # 轉換每個節點
        for node in ui_workflow.get('nodes', []):
            node_id = str(node['id'])
            class_type = node['type']
            widgets = node.get('widgets_values', [])

            api_node = {
                'class_type': class_type,
                'inputs': {}
            }

            # 處理輸入連結
            if 'inputs' in node:
                for inp in node['inputs']:
                    inp_name = inp['name']
                    link_id = inp.get('link')

                    if link_id is not None and link_id in links_by_id:
                        link_info = links_by_id[link_id]
                        api_node['inputs'][inp_name] = [
                            str(link_info['source_node']),
                            link_info['source_slot']
                        ]

            # 處理 widgets_values（根據節點類型映射）
            if class_type == 'LoadImage' and len(widgets) >= 1:
                api_node['inputs']['image'] = widgets[0]

            elif class_type == 'CLIPLoader' and len(widgets) >= 2:
                api_node['inputs']['clip_name'] = widgets[0]
                api_node['inputs']['type'] = widgets[1]

            elif class_type == 'CogVideoTextEncode' and len(widgets) >= 1:
                api_node['inputs']['prompt'] = widgets[0]
                if len(widgets) >= 2:
                    api_node['inputs']['guidance'] = widgets[1]
                if len(widgets) >= 3:
                    api_node['inputs']['force_offload'] = widgets[2]

            elif class_type == 'ImageResizeKJ' and len(widgets) >= 8:
                api_node['inputs']['width'] = widgets[0]
                api_node['inputs']['height'] = widgets[1]
                api_node['inputs']['interpolation'] = widgets[2]
                api_node['inputs']['keep_proportion'] = widgets[3]
                api_node['inputs']['divisible_by'] = widgets[4]
                api_node['inputs']['width_input'] = widgets[5]
                api_node['inputs']['height_input'] = widgets[6]
                upscale_method = widgets[7] if widgets[7] != 'disabled' else 'lanczos'
                api_node['inputs']['upscale_method'] = upscale_method

            elif class_type == 'CogVideoSampler' and len(widgets) >= 7:
                api_node['inputs']['seed'] = widgets[0]
                api_node['inputs']['steps'] = widgets[1]
                api_node['inputs']['cfg'] = widgets[2]
                api_node['inputs']['denoise_strength'] = widgets[3]
                api_node['inputs']['seed_mode'] = widgets[4]
                api_node['inputs']['scheduler'] = widgets[5]
                api_node['inputs']['num_frames'] = widgets[6]

            elif class_type == 'CogVideoImageEncode' and len(widgets) >= 2:
                api_node['inputs']['enable_vae_encode'] = widgets[0]
                api_node['inputs']['latent_samples'] = widgets[1]

            elif class_type == 'CogVideoDecode' and len(widgets) >= 6:
                api_node['inputs']['enable_vae_tiling'] = widgets[0]
                api_node['inputs']['tile_sample_min_height'] = widgets[1]
                api_node['inputs']['tile_sample_min_width'] = widgets[2]
                api_node['inputs']['tile_overlap_factor_height'] = widgets[3]
                api_node['inputs']['tile_overlap_factor_width'] = widgets[4]
                api_node['inputs']['auto_tile_size'] = widgets[5]

            elif class_type == 'DownloadAndLoadCogVideoModel' and len(widgets) >= 6:
                api_node['inputs']['model'] = widgets[0]
                api_node['inputs']['precision'] = widgets[1]
                api_node['inputs']['compile'] = widgets[2]
                api_node['inputs']['enable_sequential_cpu_offload'] = widgets[3]
                api_node['inputs']['attention_mode'] = widgets[4]
                api_node['inputs']['device'] = widgets[5]

            elif class_type == 'VHS_VideoCombine' and isinstance(widgets, dict):
                for key, value in widgets.items():
                    if key != 'videopreview':
                        api_node['inputs'][key] = value

            api_workflow[node_id] = api_node

        return api_workflow

    def generate_workflow(
        self,
        character_name: str,
        prompt: str,
        negative_prompt: str,
        reference_image: str,
        output_prefix: str,
        seed: int = 123456,
        steps: int = 25,
        cfg: float = 6.0,
        width: int = 1360,
        height: int = 768,
        num_frames: int = 49,
        lora_path: str = None,
        lora_strength: float = 0.8
    ) -> Dict[str, Any]:
        """
        產生自訂的 API 格式 workflow

        Args:
            character_name: 角色名稱
            prompt: 正向提示詞
            negative_prompt: 負向提示詞
            reference_image: 參考圖片路徑
            output_prefix: 輸出檔名前綴
            seed: 隨機種子
            steps: 採樣步數
            cfg: CFG scale
            width: 輸出寬度
            height: 輸出高度
            num_frames: 生成幀數（重要！）
            lora_path: LoRA 路徑（暫不支援）
            lora_strength: LoRA 強度

        Returns:
            修改後的 API 格式 workflow dict
        """
        workflow = copy.deepcopy(self.template)

        # 只使用檔名，不包含完整路徑
        image_name = Path(reference_image).name

        # 修改各個節點的參數
        for node_id, node in workflow.items():
            class_type = node['class_type']

            # 1. 修改正向 prompt (CogVideoTextEncode - node 30)
            if class_type == 'CogVideoTextEncode' and node_id == '30':
                node['inputs']['prompt'] = prompt
                print(f"✓ 設定正向 prompt: {prompt[:50]}...")

            # 2. 修改負向 prompt (CogVideoTextEncode - node 31)
            elif class_type == 'CogVideoTextEncode' and node_id == '31':
                node['inputs']['prompt'] = negative_prompt
                print(f"✓ 設定負向 prompt: {negative_prompt[:50]}...")

            # 3. 修改參考圖片 (LoadImage - node 36)
            elif class_type == 'LoadImage' and node_id == '36':
                node['inputs']['image'] = image_name
                print(f"✓ 設定參考圖片: {image_name}")

            # 4. 修改解析度 (ImageResizeKJ - node 37)
            elif class_type == 'ImageResizeKJ' and node_id == '37':
                node['inputs']['width'] = width
                node['inputs']['height'] = height
                print(f"✓ 設定解析度: {width}x{height}")

            # 5. 修改採樣器參數 (CogVideoSampler - node 63)
            elif class_type == 'CogVideoSampler' and node_id == '63':
                node['inputs']['seed'] = seed
                node['inputs']['steps'] = steps
                node['inputs']['cfg'] = cfg
                node['inputs']['num_frames'] = num_frames  # 重要！設定幀數
                print(f"✓ 設定採樣參數: seed={seed}, steps={steps}, cfg={cfg}, num_frames={num_frames}")

            # 6. 修改輸出檔名 (VHS_VideoCombine - node 44)
            elif class_type == 'VHS_VideoCombine' and node_id == '44':
                node['inputs']['filename_prefix'] = output_prefix
                print(f"✓ 設定輸出前綴: {output_prefix}")

        if lora_path:
            print(f"⚠ LoRA 支援待實現: {lora_path}")

        return workflow

    def save_workflow(self, workflow: Dict[str, Any], output_path: str):
        """儲存 API 格式 workflow 到檔案"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(workflow, f, indent=2)
        print(f"✓ Workflow 已儲存: {output_path}")


if __name__ == '__main__':
    # 測試範例
    generator = WorkflowGenerator(
        template_path='/mnt/c/ai_projects/video-gen-factory/workflows/miguel_cogvideox_base.json'
    )

    workflow = generator.generate_workflow(
        character_name="Miguel Rivera",
        prompt="Miguel Rivera from Disney Pixar Coco movie, dancing happily with guitar, Pixar style",
        negative_prompt="blurry, distorted, low quality, bad anatomy",
        reference_image="prompt_0000_img_00.png",
        output_prefix="miguel_dancing_test",
        seed=123456,
        steps=25,
        cfg=6.0,
        num_frames=49  # 生成 49 幀 ~3 秒 @ 16fps
    )

    generator.save_workflow(
        workflow,
        '/mnt/c/ai_projects/video-gen-factory/workflows/generated_test_api.json'
    )
    print("\n✓ 測試完成！")
