# 🎬 Miguel 終極視頻生成工作流程

## 方案 C：專業級混合工作流程

結合 **Wan 2.2 + CogVideoX + RIFE + Real-ESRGAN** 達到極致品質

---

## 📋 系統配置

- **GPU**: RTX 5080 16GB VRAM
- **ComfyUI**: v0.5.1
- **Miguel LoRA**: `BEST_miguel_lora_sdxl.safetensors`

---

## 🔧 已安裝組件

### 核心模型
- ✅ Wan 2.2 I2V 14B GGUF Q5_K_M (10.8 GB) - 下載中
- ✅ T5 XXL FP8 編碼器 - 下載中
- ✅ Real-ESRGAN x4 Anime 6B
- ✅ RIFE v4.7

### ComfyUI 插件
- ✅ ComfyUI-GGUF (Wan 2.2 支援)
- ✅ ComfyUI-CogVideoXWrapper
- ✅ ComfyUI-AnimateDiff-Evolved
- ✅ ComfyUI_IPAdapter_plus
- ✅ ComfyUI-VideoHelperSuite
- ✅ ComfyUI-Frame-Interpolation

---

## 🎯 完整工作流程

### 階段 1：Wan 2.2 基礎生成（角色一致性核心）

**目標**: 生成保持 Miguel 特徵的基礎動畫

#### 輸入準備
1. **參考圖片**: Miguel 的單張清晰圖片
   - 位置: `/mnt/c/ai_tools/comfyui/input/miguel_ref.png`
   - 建議: 正面、全身或半身、表情自然

2. **LoRA 權重**: 0.7-0.9
   - 路徑: `/mnt/c/ai_models/lora/BEST_miguel_lora_sdxl.safetensors`

#### Wan 2.2 參數設置

```yaml
模型: wan2.2_i2v_low_noise_14B_Q5_K_M.gguf
模型路徑: /mnt/c/ai_models/video/wan_gguf/

生成設定:
  - Resolution: 512x512 或 640x480 (VRAM 優化)
  - Duration: 5-10 秒
  - Seed: 固定值（可重複生成）
  - Prompt Extend: True
  - Watermark: False

Prompt 範例:
  Positive: "Miguel Rivera from Coco, dancing happily with guitar,
             Pixar animation style, smooth motion, vibrant colors,
             detailed character, high quality"

  Negative: "blurry, distorted, low quality, bad anatomy,
             inconsistent character, flickering"

VRAM 優化:
  - 使用 GGUF Q5_K_M 量化版本
  - 啟用 CPU offload
  - 分塊處理（如果需要）
```

#### 預期輸出
- **格式**: MP4 或幀序列
- **質量**: 中等解析度，角色特徵保持一致
- **時長**: 5-10 秒，低幀率（~6-8fps）

---

### 階段 2：CogVideoX 運動優化（可選）

**目標**: 提升運動流暢度和細節

#### 選項 A: Vid2Vid 增強
```yaml
模型: CogVideoX-5B (自動下載)
輸入: Wan 2.2 生成的視頻

參數:
  - Denoise Strength: 0.3-0.5 (保持原始內容)
  - Steps: 20-25
  - CFG Scale: 7.0
  - Prompt: 與階段 1 相同或略微調整
```

#### 選項 B: Video-As-Prompt (VAP)
```yaml
用途: 使用參考視頻的運動模式
輸入:
  - Source Image: Miguel 參考圖
  - Reference Video: 期望的運動參考

效果: 將參考視頻的動作應用到 Miguel 上
```

**注意**: 此階段為可選，如果階段 1 效果已滿意可跳過

---

### 階段 3：RIFE 超級插值

**目標**: 6fps → 60fps 絲滑流暢

#### Workflow 節點
```json
{
  "node_type": "RIFE VFI",
  "parameters": {
    "ckpt_name": "rife47.pth",
    "multiplier": 10,
    "fast_mode": false,
    "ensemble": true,
    "scale_factor": 1.0
  }
}
```

#### 輸出
- **幀率**: 60fps
- **品質**: 平滑過渡，無明顯抖動

---

### 階段 4：Real-ESRGAN AI 放大

**目標**: 低解析度 → 1920x1080 Full HD

#### Workflow 節點
```json
{
  "upscale_model": "RealESRGAN_x4plus_anime_6B.pth",
  "process": [
    "1. AI Upscale 4x",
    "2. Resize to 1920x1080 (Lanczos)",
    "3. Save as H.264 MP4 (CRF 15)"
  ]
}
```

---

## 📊 參數優化表

### Wan 2.2 解析度 vs VRAM 需求

| Resolution | VRAM (Q5_K_M) | 適用場景 |
|-----------|---------------|---------|
| 480x480   | ~8-9 GB       | 最安全，測試用 |
| 512x512   | ~10-11 GB     | 推薦平衡點 ✅ |
| 640x480   | ~12-13 GB     | 較高質量 |
| 768x512   | ~14-15 GB     | 接近極限 ⚠️ |

### Miguel LoRA 權重建議

| 權重 | 效果 | 使用場景 |
|------|------|---------|
| 0.6-0.7 | 較自由，允許更多變化 | 需要動作幅度大 |
| 0.7-0.8 | 平衡 ✅ | **推薦** |
| 0.8-0.9 | 強制保持特徵 | 特寫鏡頭 |
| 0.9-1.0 | 極度嚴格 | 可能過度約束 |

---

## 🚀 快速啟動步驟

### 1. 檢查模型下載完成
```bash
ls -lh /mnt/c/ai_models/video/wan_gguf/wan2.2_i2v_low_noise_14B_Q5_K_M.gguf
ls -lh /mnt/c/ai_models/clip/t5xxl_fp8_e4m3fn.safetensors
```

### 2. 重啟 ComfyUI 載入新插件
```bash
# ComfyUI 會自動載入新模型
```

### 3. 載入工作流程
- 瀏覽器: http://localhost:8188
- Load: `workflows/miguel_wan22_ultimate.json`
- 調整參數
- Queue Prompt

### 4. 預計處理時間
- **Wan 2.2 生成**: 10-20 分鐘 (5-10秒視頻)
- **RIFE 插值**: 5-10 分鐘
- **ESRGAN 放大**: 10-20 分鐘
- **總計**: 約 30-50 分鐘（取決於視頻長度）

---

## 💡 進階技巧

### 1. 批次處理多個場景
使用 `scripts/batch_processor.py` 處理多個 Miguel 動畫場景

### 2. 角色一致性微調
如果某些角度 Miguel 特徵不明顯：
- 提高 LoRA 權重到 0.85-0.9
- 在 prompt 中加入更詳細的特徵描述
- 使用 IP-Adapter 作為額外約束

### 3. 運動控制
如果需要精確控制運動：
- 使用 ControlNet (Pose/Depth)
- 準備運動參考序列
- AnimateDiff + ControlNet 組合

---

## 🔍 故障排除

### VRAM 不足 (OOM)
```
解決方案:
1. 降低解析度: 512x512 → 480x480
2. 減少視頻時長: 10秒 → 5秒
3. 使用更低量化: Q5_K_M → Q4_K_M
4. 啟用 CPU offload
```

### 角色不一致
```
解決方案:
1. 提高 LoRA 權重
2. 降低 Denoise strength (Wan 2.2)
3. 使用更清晰的參考圖
4. 添加 IP-Adapter 節點
```

### 運動不流暢
```
解決方案:
1. 增加 RIFE multiplier
2. 啟用 RIFE ensemble mode
3. 檢查輸入視頻幀率
4. 使用 CogVideoX VAP 優化
```

---

## 📞 下一步

模型下載完成後：
1. 測試基礎 Wan 2.2 生成
2. 評估是否需要 CogVideoX 優化
3. 套用完整的後處理流程
4. 根據結果調整參數

---

**創建時間**: 2025-12-21
**ComfyUI 版本**: v0.5.1
**Wan 版本**: 2.2 I2V GGUF Q5_K_M
