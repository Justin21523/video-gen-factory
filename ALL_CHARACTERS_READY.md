# 🎬 批量視頻生成系統 - 角色總覽

## ✅ 系統狀態

- **總角色數**: 14 個
- **每個角色參考圖片**: 10 張（來自 action/expression/pose 類別）
- **每個角色場景數**: 4 個標準場景
- **總共可生成視頻數**: 56 個（14 角色 × 4 場景）

## 📋 角色清單

### Disney Pixar 官方角色（8 個）

1. **Miguel Rivera** (Coco)
   - LoRA: `BEST_miguel_lora_sdxl.safetensors`
   - 配置: `characters/miguel.yaml`
   - 參考圖: 10 張

2. **Alberto Scorfano** (Luca - 人類形態)
   - LoRA: `BEST_alberto_lora_sdxl.safetensors`
   - 配置: `characters/alberto.yaml`
   - 參考圖: 10 張

3. **Luca Paguro** (Luca - 人類形態)
   - LoRA: `BEST_luca_lora_sdxl.safetensors`
   - 配置: `characters/luca.yaml`
   - 參考圖: 10 張

4. **Giulia Marcovaldo** (Luca)
   - LoRA: `BEST_giulia_lora_sdxl.safetensors`
   - 配置: `characters/giulia.yaml`
   - 參考圖: 10 張

5. **Ian Lightfoot** (Onward - 精靈)
   - LoRA: `BEST_ian_lightfoot_lora_sdxl.safetensors`
   - 配置: `characters/ian_lightfoot.yaml`
   - 參考圖: 10 張

6. **Barley Lightfoot** (Onward - 精靈)
   - LoRA: `BEST_barley_lightfoot_lora_sdxl.safetensors`
   - 配置: `characters/barley_lightfoot.yaml`
   - 參考圖: 10 張

7. **Russell** (Up)
   - LoRA: `BEST_russell_lora_sdxl.safetensors`
   - 配置: `characters/russell.yaml`
   - 參考圖: 10 張

8. **Elio** (Elio - 即將上映)
   - LoRA: `BEST_elio_lora_sdxl.safetensors`
   - 配置: `characters/elio.yaml`
   - 參考圖: 10 張

### 海怪形態角色（2 個）

9. **Alberto (Sea Monster)** (Luca - 海怪形態)
   - LoRA: `BEST_alberto_seamonster_lora_sdxl.safetensors`
   - 配置: `characters/alberto_seamonster.yaml`
   - 參考圖: 10 張

10. **Luca (Sea Monster)** (Luca - 海怪形態)
    - LoRA: `BEST_luca_seamonster_lora_sdxl.safetensors`
    - 配置: `characters/luca_seamonster.yaml`
    - 參考圖: 10 張

### 原創/其他角色（4 個）

11. **Bryce**
    - LoRA: `BEST_bryce_lora_sdxl.safetensors`
    - 配置: `characters/bryce.yaml`
    - 參考圖: 10 張

12. **Caleb**
    - LoRA: `BEST_caleb_lora_sdxl.safetensors`
    - 配置: `characters/caleb.yaml`
    - 參考圖: 10 張

13. **Orion**
    - LoRA: `BEST_orion_lora_sdxl.safetensors`
    - 配置: `characters/orion.yaml`
    - 參考圖: 10 張

14. **Tyler**
    - LoRA: `BEST_tyler_lora_sdxl.safetensors`
    - 配置: `characters/tyler.yaml`
    - 參考圖: 10 張

## 🎭 標準場景（每個角色共通）

每個角色配置包含以下 4 個標準場景：

1. **happy_dancing** - 快樂跳舞
   - Seed: 123456
   - 重點: 充滿活力的動作，流暢運動

2. **walking_confident** - 自信走路
   - Seed: 234567
   - 重點: 自然步態，手臂自然擺動

3. **excited_jumping** - 興奮跳躍
   - Seed: 345678
   - 重點: 動態空中姿勢，最燦爛的笑容

4. **looking_around** - 好奇觀望
   - Seed: 456789
   - 重點: 溫和頭部動作，富有表情的臉龐

## 📊 生成設定（所有角色統一）

```yaml
model: kijai/CogVideoX-5b-1.5-I2V
steps: 25
cfg: 6.0
sampler: CogVideoXDDIM
scheduler: CogVideoX
width: 1360
height: 768
frame_rate: 16
```

## 🚀 快速生成指令

### 生成單個角色的所有場景

```bash
# Miguel 的所有場景（4 個視頻）
python batch_generate.py --character miguel

# Alberto 的所有場景
python batch_generate.py --character alberto

# Luca 的所有場景
python batch_generate.py --character luca
```

### 生成所有角色的特定場景

```bash
# 所有角色的跳舞場景（14 個視頻）
python batch_generate.py --all --scene happy_dancing

# 所有角色的跳躍場景（14 個視頻）
python batch_generate.py --all --scene excited_jumping
```

### 生成所有角色的所有場景

```bash
# 預覽模式（不實際生成）
python batch_generate.py --all --dry-run

# 實際生成（14 角色 × 4 場景 = 56 個視頻）
python batch_generate.py --all
```

## ⏱️ 預估生成時間（RTX 5080 16GB）

單個視頻（1360x768, 25 steps）：約 5-8 分鐘

- **單個角色 4 場景**: 約 20-30 分鐘
- **全部 56 個視頻**: 約 5-7 小時

### 加速建議

如果需要快速測試，可修改配置：

```yaml
steps: 15           # 降低至 15 步（原 25）
width: 1024         # 降低解析度（原 1360）
height: 576         # （原 768）
```

預估時間可減少至：
- 單個視頻: 約 3-5 分鐘
- 全部 56 個: 約 3-4 小時

## 📁 參考圖片來源

所有角色的參考圖片來自：

```
/mnt/data/ai_data/synthetic_lora_data/generated_data/{character}/
├── action/images/      # 動作類圖片
├── expression/images/  # 表情類圖片
└── pose/images/        # 姿勢類圖片
```

每個角色取前 10 張圖片作為參考（按檔名排序）。

## 🎨 Prompt 結構

### 完整 Prompt 組成

```
[base_description] + [scene.prompt]
```

範例（Miguel 跳舞場景）：
```
Miguel Rivera from Disney Pixar Coco movie, 12 year old Mexican boy character,
distinctive appearance with brown skin tone, large expressive brown eyes,
black messy hair, wearing iconic white long-sleeve shirt with black vest over it,
bright red necktie, brown pants, holding traditional wooden guitar,
Pixar 3D animation style, high detail character model, masterpiece quality,
dancing happily with joyful expression, energetic movement, smooth fluid motion,
vibrant colors, detailed character animation, cinematic lighting,
Pixar movie quality
```

### 完整 Negative Prompt 組成

```
[base_negative] + [scene.negative]
```

範例：
```
blurry, out of focus, distorted, warped, low quality, poor quality,
bad quality, worst quality, jpeg artifacts, compression artifacts,
bad anatomy, deformed body, deformed face, deformed hands, deformed fingers,
extra limbs, missing limbs, bad proportions, inconsistent character appearance,
character morphing, face morphing, flickering, temporal inconsistency,
frame inconsistency, wrong facial features, different character,
wrong clothing, clothing changes, color shifting, wrong face,
ugly face, disgusting, poorly drawn, amateur, sketch, unfinished,
watermark, signature, text, realistic photo, realistic style,
live action, not animated, different art style, anime style,
manga style, multiple people, crowd, static pose, stiff movement,
sad expression
```

## 🔧 自訂場景

如果想為特定角色添加專屬場景，編輯對應的 YAML 檔：

```yaml
scenes:
  # ... 現有場景 ...

  - id: "custom_scene_name"
    prompt: "詳細的場景描述"
    negative: "要避免的元素"
    seed: 999999
```

然後執行：

```bash
python batch_generate.py --character 角色名 --scene custom_scene_name
```

## 📈 下一步

1. **測試單個角色**: 先用 `--dry-run` 預覽
2. **小規模測試**: 生成 1-2 個角色驗證品質
3. **調整參數**: 根據結果調整 steps/cfg/resolution
4. **批量生成**: 確認無誤後執行全部生成

## 🆘 疑難排解

### 如果遇到 "參考圖片未找到" 錯誤

ComfyUI 需要圖片在其 input 目錄中。有兩個選項：

**選項 A: 建立符號連結**
```bash
ln -sf /mnt/data/ai_data/synthetic_lora_data/generated_data \
       /mnt/c/ai_tools/comfyui/input/characters
```

**選項 B: 複製圖片**
```bash
cp -r /mnt/data/ai_data/synthetic_lora_data/generated_data/* \
      /mnt/c/ai_tools/comfyui/input/
```

### 如果生成失敗

1. 檢查 ComfyUI 是否運行：`curl http://127.0.0.1:8188`
2. 查看 ComfyUI 日誌尋找錯誤訊息
3. 嘗試降低解析度或步數
4. 確認 LoRA 檔案存在於 `/mnt/c/ai_models/lora_sdxl/`

---

**系統已就緒！** 可開始批量生成 🎬
