#!/usr/bin/env python3
"""
將 ComfyUI UI workflow 格式轉換為 API 格式
UI 格式: {nodes: [...], links: [...]}
API 格式: {"node_id": {class_type: "...", inputs: {...}}}
"""

import json
import sys

def convert_ui_to_api(ui_workflow):
    """轉換 UI workflow 到 API 格式"""
    api_workflow = {}

    # 建立 link 索引以快速查找
    links_by_id = {}
    for link in ui_workflow.get('links', []):
        # link 格式: [link_id, source_node_id, source_slot, target_node_id, target_slot, type]
        link_id = link[0]
        links_by_id[link_id] = {
            'source_node': link[1],
            'source_slot': link[2],
            'target_node': link[3],
            'target_slot': link[4],
            'type': link[5]
        }

    # 建立節點索引
    nodes_by_id = {node['id']: node for node in ui_workflow.get('nodes', [])}

    # 轉換每個節點
    for node in ui_workflow.get('nodes', []):
        node_id = str(node['id'])
        class_type = node['type']

        api_node = {
            'class_type': class_type,
            'inputs': {}
        }

        # 處理輸入
        if 'inputs' in node:
            for inp in node['inputs']:
                inp_name = inp['name']
                link_id = inp.get('link')

                if link_id is not None and link_id in links_by_id:
                    link_info = links_by_id[link_id]
                    # API 格式: [source_node_id, source_output_slot]
                    api_node['inputs'][inp_name] = [str(link_info['source_node']), link_info['source_slot']]

        # 處理 widgets_values - 這些是節點的直接參數
        if 'widgets_values' in node:
            widgets = node['widgets_values']

            # widgets_values 的處理取決於節點類型
            # 對於大多數節點，我們需要知道參數名稱
            # 這裡使用一個通用方法：從節點定義中獲取參數名
            #
            # 但為了簡化，我們可以使用一些常見節點的已知映射

            if class_type == 'LoadImage':
                if len(widgets) >= 1:
                    api_node['inputs']['image'] = widgets[0]

            elif class_type == 'CLIPLoader':
                if len(widgets) >= 2:
                    api_node['inputs']['clip_name'] = widgets[0]
                    api_node['inputs']['type'] = widgets[1]

            elif class_type == 'CogVideoTextEncode':
                if len(widgets) >= 1:
                    api_node['inputs']['prompt'] = widgets[0]  # 修正：text -> prompt
                if len(widgets) >= 2:
                    api_node['inputs']['guidance'] = widgets[1]
                if len(widgets) >= 3:
                    api_node['inputs']['force_offload'] = widgets[2]  # 修正：use_compile -> force_offload

            elif class_type == 'ImageResizeKJ':
                if len(widgets) >= 8:
                    api_node['inputs']['width'] = widgets[0]
                    api_node['inputs']['height'] = widgets[1]
                    api_node['inputs']['interpolation'] = widgets[2]
                    api_node['inputs']['keep_proportion'] = widgets[3]
                    api_node['inputs']['divisible_by'] = widgets[4]
                    api_node['inputs']['width_input'] = widgets[5]
                    api_node['inputs']['height_input'] = widgets[6]
                    # upscale_method 的 'disabled' 不是有效值，改用 'lanczos'
                    upscale_method = widgets[7]
                    if upscale_method == 'disabled':
                        upscale_method = 'lanczos'
                    api_node['inputs']['upscale_method'] = upscale_method

            elif class_type == 'CogVideoSampler':
                # widgets: [seed, steps, cfg, denoise_strength, seed_mode, sampler_name, num_frames]
                if len(widgets) >= 7:
                    api_node['inputs']['seed'] = widgets[0]
                    api_node['inputs']['steps'] = widgets[1]
                    api_node['inputs']['cfg'] = widgets[2]
                    api_node['inputs']['denoise_strength'] = widgets[3]
                    api_node['inputs']['seed_mode'] = widgets[4]
                    api_node['inputs']['scheduler'] = widgets[5]  # 這是 scheduler 而不是 sampler_name
                    api_node['inputs']['num_frames'] = widgets[6]  # 修正：添加 num_frames

            elif class_type == 'CogVideoImageEncode':
                if len(widgets) >= 2:
                    api_node['inputs']['enable_vae_encode'] = widgets[0]
                    api_node['inputs']['latent_samples'] = widgets[1]

            elif class_type == 'CogVideoDecode':
                # widgets: [enable_vae_tiling, tile_sample_min_height, tile_sample_min_width,
                #           tile_overlap_factor_height, tile_overlap_factor_width, auto_tile_size]
                if len(widgets) >= 6:
                    api_node['inputs']['enable_vae_tiling'] = widgets[0]  # 修正：enable_vae_decode -> enable_vae_tiling
                    api_node['inputs']['tile_sample_min_height'] = widgets[1]
                    api_node['inputs']['tile_sample_min_width'] = widgets[2]
                    api_node['inputs']['tile_overlap_factor_height'] = widgets[3]
                    api_node['inputs']['tile_overlap_factor_width'] = widgets[4]
                    api_node['inputs']['auto_tile_size'] = widgets[5]

            elif class_type == 'DownloadAndLoadCogVideoModel':
                if len(widgets) >= 6:
                    api_node['inputs']['model'] = widgets[0]
                    api_node['inputs']['precision'] = widgets[1]
                    api_node['inputs']['compile'] = widgets[2]
                    api_node['inputs']['enable_sequential_cpu_offload'] = widgets[3]
                    api_node['inputs']['attention_mode'] = widgets[4]
                    api_node['inputs']['device'] = widgets[5]

            elif class_type == 'VHS_VideoCombine':
                # VHS_VideoCombine 使用字典格式的 widgets_values
                if isinstance(widgets, dict):
                    for key, value in widgets.items():
                        if key != 'videopreview':  # 跳過 videopreview
                            api_node['inputs'][key] = value

            else:
                # 對於未知節點，保留 widgets_values 用於調試
                api_node['_debug_widgets'] = widgets

        api_workflow[node_id] = api_node

    return api_workflow


def main():
    if len(sys.argv) < 2:
        print("Usage: python convert_workflow_to_api.py <ui_workflow.json> [output.json]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.json', '_api.json')

    with open(input_file, 'r') as f:
        ui_workflow = json.load(f)

    api_workflow = convert_ui_to_api(ui_workflow)

    with open(output_file, 'w') as f:
        json.dump(api_workflow, f, indent=2)

    print(f"✅ 轉換完成:")
    print(f"   輸入: {input_file}")
    print(f"   輸出: {output_file}")
    print(f"   節點數: {len(api_workflow)}")


if __name__ == '__main__':
    main()
