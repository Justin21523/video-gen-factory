#!/usr/bin/env python3
"""
自動產生所有角色的配置檔
Generate character configs for all characters in the dataset
"""

import os
import glob
import yaml
from pathlib import Path
from vgf_paths import project_root


# 角色資訊字典（基於 Pixar 電影角色）
CHARACTER_INFO = {
    'miguel': {
        'full_name': 'Miguel Rivera',
        'movie': 'Coco',
        'description': 'Miguel Rivera from Disney Pixar Coco movie, 12 year old Mexican boy character, distinctive appearance with brown skin tone, large expressive brown eyes, black messy hair, wearing iconic white long-sleeve shirt with black vest over it, bright red necktie, brown pants, holding traditional wooden guitar, Pixar 3D animation style, high detail character model, masterpiece quality',
        'lora': 'BEST_CHECKPOINTS_COLLECTION/BEST_miguel_lora_sdxl.safetensors',
    },
    'alberto': {
        'full_name': 'Alberto Scorfano',
        'movie': 'Luca',
        'description': 'Alberto Scorfano from Disney Pixar Luca movie, teenage Italian boy character approximately 14 years old, sea monster in human form, distinctive appearance with wild curly dark brown hair, bright green eyes with mischievous spark, tan bronze skin with sun-kissed tone, lean athletic build, wearing simple torn shorts, often shirtless showing casual beach style, confident cocky smile, Pixar 3D animation style, high detail character model, masterpiece quality',
        'lora': 'BEST_CHECKPOINTS_COLLECTION/BEST_alberto_lora_sdxl.safetensors',
    },
    'luca': {
        'full_name': 'Luca Paguro',
        'movie': 'Luca',
        'description': 'Luca Paguro from Disney Pixar Luca movie, young Italian boy character approximately 13 years old, sea monster in human form, distinctive appearance with dark brown hair, warm brown eyes, olive skin tone, slender build, wearing simple shorts and shirt, shy gentle expression, Pixar 3D animation style, high detail character model, masterpiece quality',
        'lora': 'BEST_CHECKPOINTS_COLLECTION/BEST_luca_lora_sdxl.safetensors',
    },
    'giulia': {
        'full_name': 'Giulia Marcovaldo',
        'movie': 'Luca',
        'description': 'Giulia Marcovaldo from Disney Pixar Luca movie, young Italian girl character approximately 13 years old, distinctive appearance with wild curly red orange hair, freckles across nose and cheeks, bright expressive eyes, confident energetic personality, wearing casual summer clothes, Pixar 3D animation style, high detail character model, masterpiece quality',
        'lora': 'BEST_CHECKPOINTS_COLLECTION/BEST_giulia_lora_sdxl.safetensors',
    },
    'ian_lightfoot': {
        'full_name': 'Ian Lightfoot',
        'movie': 'Onward',
        'description': 'Ian Lightfoot from Disney Pixar Onward movie, teenage elf character approximately 16 years old, blue skin tone, large pointed ears, dark blue hair, slender build, wearing purple polo shirt and jeans, shy anxious expression, glasses, Pixar 3D animation style, high detail character model, masterpiece quality',
        'lora': 'BEST_CHECKPOINTS_COLLECTION/BEST_ian_lightfoot_lora_sdxl.safetensors',
    },
    'barley_lightfoot': {
        'full_name': 'Barley Lightfoot',
        'movie': 'Onward',
        'description': 'Barley Lightfoot from Disney Pixar Onward movie, young adult elf character approximately 19 years old, blue skin tone, large pointed ears, long dark blue hair and beard, stocky muscular build, wearing band t-shirt and vest, confident enthusiastic expression, Pixar 3D animation style, high detail character model, masterpiece quality',
        'lora': 'BEST_CHECKPOINTS_COLLECTION/BEST_barley_lightfoot_lora_sdxl.safetensors',
    },
    'russell': {
        'full_name': 'Russell',
        'movie': 'Up',
        'description': 'Russell from Disney Pixar Up movie, young boy character approximately 8 years old, Asian American appearance, round face, black hair, wearing orange and yellow Wilderness Explorer uniform with badges, red neckerchief, khaki shorts, enthusiastic cheerful expression, Pixar 3D animation style, high detail character model, masterpiece quality',
        'lora': 'BEST_CHECKPOINTS_COLLECTION/BEST_russell_lora_sdxl.safetensors',
    },
    'elio': {
        'full_name': 'Elio',
        'movie': 'Elio',
        'description': 'Elio from Disney Pixar Elio movie, young boy character approximately 11 years old, distinctive appearance with dark curly hair, warm brown eyes, curious intelligent expression, wearing casual contemporary clothes, Pixar 3D animation style, high detail character model, masterpiece quality',
        'lora': 'BEST_CHECKPOINTS_COLLECTION/BEST_elio_lora_sdxl.safetensors',
    },
    # 以下角色為原創或其他來源
    'alberto_seamonster': {
        'full_name': 'Alberto (Sea Monster Form)',
        'movie': 'Luca',
        'description': 'Alberto Scorfano in sea monster form from Disney Pixar Luca movie, teenage sea monster character, distinctive appearance with teal blue-green scales, purple spots pattern, webbed hands and feet, fish-like tail, bright green eyes, confident expression, Pixar 3D animation style, high detail creature model, masterpiece quality',
        'lora': 'BEST_CHECKPOINTS_COLLECTION/BEST_alberto_seamonster_lora_sdxl.safetensors',
    },
    'luca_seamonster': {
        'full_name': 'Luca (Sea Monster Form)',
        'movie': 'Luca',
        'description': 'Luca Paguro in sea monster form from Disney Pixar Luca movie, young sea monster character, distinctive appearance with teal blue scales, darker blue patterns, webbed hands and feet, fish-like tail, warm brown eyes, gentle shy expression, Pixar 3D animation style, high detail creature model, masterpiece quality',
        'lora': 'BEST_CHECKPOINTS_COLLECTION/BEST_luca_seamonster_lora_sdxl.safetensors',
    },
    'bryce': {
        'full_name': 'Bryce',
        'movie': 'Original Character',
        'description': 'Bryce, young boy character, Pixar 3D animation style, high detail character model, masterpiece quality',
        'lora': 'BEST_CHECKPOINTS_COLLECTION/BEST_bryce_lora_sdxl.safetensors',
    },
    'caleb': {
        'full_name': 'Caleb',
        'movie': 'Original Character',
        'description': 'Caleb, young boy character, Pixar 3D animation style, high detail character model, masterpiece quality',
        'lora': 'BEST_CHECKPOINTS_COLLECTION/BEST_caleb_lora_sdxl.safetensors',
    },
    'orion': {
        'full_name': 'Orion',
        'movie': 'Original Character',
        'description': 'Orion, young boy character, Pixar 3D animation style, high detail character model, masterpiece quality',
        'lora': 'BEST_CHECKPOINTS_COLLECTION/BEST_orion_lora_sdxl.safetensors',
    },
    'tyler': {
        'full_name': 'Tyler',
        'movie': 'Original Character',
        'description': 'Tyler, young boy character, Pixar 3D animation style, high detail character model, masterpiece quality',
        'lora': 'BEST_CHECKPOINTS_COLLECTION/BEST_tyler_lora_sdxl.safetensors',
    },
}


# 通用負向提示詞
BASE_NEGATIVE = "blurry, out of focus, distorted, warped, low quality, poor quality, bad quality, worst quality, jpeg artifacts, compression artifacts, bad anatomy, deformed body, deformed face, deformed hands, deformed fingers, extra limbs, missing limbs, bad proportions, inconsistent character appearance, character morphing, face morphing, flickering, temporal inconsistency, frame inconsistency, wrong facial features, different character, wrong clothing, clothing changes, color shifting, wrong face, ugly face, disgusting, poorly drawn, amateur, sketch, unfinished, watermark, signature, text, realistic photo, realistic style, live action, not animated, different art style, anime style, manga style, multiple people, crowd"


# 通用場景模板
GENERIC_SCENES = [
    {
        'id': 'happy_dancing',
        'prompt': 'dancing happily with joyful expression, energetic movement, smooth fluid motion, vibrant colors, detailed character animation, cinematic lighting, Pixar movie quality',
        'negative': 'static pose, stiff movement, sad expression',
        'seed': 123456
    },
    {
        'id': 'walking_confident',
        'prompt': 'walking confidently with natural gait, arms swinging naturally, cheerful expression, beautiful background, warm lighting, smooth animation',
        'negative': 'floating, sliding, unnatural movement, stiff body',
        'seed': 234567
    },
    {
        'id': 'excited_jumping',
        'prompt': 'jumping with excitement and joy, dynamic mid-air pose, biggest smile, energetic composition, vibrant atmosphere, Pixar quality',
        'negative': 'standing still, feet on ground, no motion, neutral face',
        'seed': 345678
    },
    {
        'id': 'looking_around',
        'prompt': 'looking around curiously with wonder in eyes, gentle head movement, expressive face, beautiful environment, cinematic composition',
        'negative': 'staring blankly, no movement, boring pose',
        'seed': 456789
    },
]


def get_character_images(character_name: str, data_dir: str) -> list:
    """獲取角色的所有參考圖片"""
    char_dir = os.path.join(data_dir, character_name)
    if not os.path.exists(char_dir):
        return []

    images = []
    for category in ['action', 'expression', 'pose']:
        pattern = os.path.join(char_dir, category, 'images', '*.png')
        images.extend(glob.glob(pattern))

    return sorted(images)[:10]  # 最多取 10 張作為參考


def generate_character_config(character_name: str, data_dir: str) -> dict:
    """產生單個角色的配置"""
    info = CHARACTER_INFO.get(character_name, {
        'full_name': character_name.replace('_', ' ').title(),
        'movie': 'Unknown',
        'description': f'{character_name.replace("_", " ").title()}, Pixar 3D animation style, high detail character model, masterpiece quality',
        'lora': f'BEST_CHECKPOINTS_COLLECTION/BEST_{character_name}_lora_sdxl.safetensors',
    })

    ref_images = get_character_images(character_name, data_dir)

    config = {
        'character': {
            'name': info['full_name'],
            'lora_path': info['lora'],
            'lora_strength': 0.8,
            'reference_images': ref_images if ref_images else [
                str(project_root() / "reference_images" / f"{character_name}_ref.png")
            ],
            'base_description': info['description'],
            'base_negative': BASE_NEGATIVE,
            'scenes': GENERIC_SCENES,
        },
        'generation_settings': {
            'model': 'kijai/CogVideoX-5b-1.5-I2V',
            'steps': 25,
            'cfg': 6.0,
            'sampler': 'CogVideoXDDIM',
            'scheduler': 'CogVideoX',
            'width': 1360,
            'height': 768,
            'frame_rate': 16,
            'output_prefix': character_name,
        }
    }

    return config


def main():
    data_dir = '/mnt/data/ai_data/synthetic_lora_data/generated_data'
    output_dir = str(project_root() / "characters")

    # 確保輸出目錄存在
    os.makedirs(output_dir, exist_ok=True)

    # 獲取所有角色目錄
    character_dirs = [d for d in os.listdir(data_dir)
                      if os.path.isdir(os.path.join(data_dir, d))]

    print(f"找到 {len(character_dirs)} 個角色")

    for character_name in sorted(character_dirs):
        print(f"\n處理角色: {character_name}")

        # 產生配置
        config = generate_character_config(character_name, data_dir)

        # 儲存配置
        output_path = os.path.join(output_dir, f'{character_name}.yaml')
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, sort_keys=False, default_flow_style=False)

        # 顯示統計
        ref_count = len(config['character']['reference_images'])
        scene_count = len(config['character']['scenes'])
        print(f"  ✓ 儲存到: {output_path}")
        print(f"  ✓ 參考圖片: {ref_count} 張")
        print(f"  ✓ 場景數量: {scene_count} 個")

    print(f"\n{'='*60}")
    print(f"✅ 完成！共產生 {len(character_dirs)} 個角色配置檔")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
