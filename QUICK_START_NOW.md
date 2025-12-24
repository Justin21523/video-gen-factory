# 🎬 立即開始：Wan 2.2 + Miguel LoRA（最簡單方式）

## ✅ 步驟 1：載入內建模板

1. **打開 ComfyUI**: http://localhost:8188
2. **刷新頁面**（F5）確保最新狀態
3. **點擊左上角菜單**：Workflow → Browse Templates
4. **選擇類別**：Video
5. **找到並載入**：尋找包含 "Wan" 的模板
   - 可能叫 "Wan2.2 14B I2V" 或類似名稱

**如果沒有看到 Wan 模板**：
→ 使用下面的**手動方案**

---

## 🔧 步驟 2：手動創建 Workflow（替代方案）

如果內建模板沒有 Wan 2.2，我們改用 **AnimateDiff + IP-Adapter**（您已有的插件）：

### 基礎節點配置：

1. **載入模型**（右鍵 → Add Node）：
   ```
   - CheckpointLoaderSimple
     → 選擇：sd_xl_base_1.0.safetensors
   ```

2. **添加 Miguel LoRA**：
   ```
   - LoraLoader
     → lora_name: BEST_CHECKPOINTS_COLLECTION/BEST_miguel_lora_sdxl.safetensors
     → strength_model: 0.8
     → strength_clip: 1.0
   ```

3. **添加 IP-Adapter**（保持角色一致性）：
   ```
   - IPAdapterModelLoader
     → model_name: ip-adapter-plus_sdxl_vit-h.safetensors

   - IPAdapter Apply
     → weight: 0.8
     → image: [載入 Miguel 參考圖]
   ```

4. **AnimateDiff 運動模組**：
   ```
   - ADE_AnimateDiffLoaderGen1
     → model_name: mm_sd_v15_v2.ckpt

   - ADE_AnimateDiffSampler
     → context_length: 16
     → context_overlap: 4
   ```

5. **提示詞節點**：
   ```
   - CLIPTextEncode (Positive):
     "Miguel Rivera from Coco, dancing with guitar,
      Pixar style, smooth motion, high quality"

   - CLIPTextEncode (Negative):
     "blurry, distorted, inconsistent, flickering"
   ```

6. **採樣設置**：
   ```
   - KSampler:
     → steps: 20
     → cfg: 7.0
     → sampler_name: euler
     → scheduler: normal
     → denoise: 0.75
   ```

7. **輸出**：
   ```
   - VHS_VideoCombine:
     → frame_rate: 8
     → format: video/h264-mp4
     → filename_prefix: miguel_test
   ```

---

## 📊 參數建議（小測試）

```yaml
解析度: 512x512
幀數: 16 frames (2秒 @ 8fps)
Steps: 20
CFG: 7.0
Denoise: 0.75
LoRA 權重: 0.8
IP-Adapter 權重: 0.8
Seed: 123456 (固定)
```

---

## ⚡ 超簡單方案：先測試靜態圖

如果視頻生成太複雜，先測試**靜態 Miguel 圖片生成**：

### 最簡 Workflow：
```
[CheckpointLoader (SDXL)]
         ↓
[LoraLoader (Miguel)]
         ↓
[CLIPTextEncode (Prompt)]
         ↓
[KSampler]
         ↓
[VAEDecode]
         ↓
[SaveImage]
```

**Prompt 範例**：
```
Miguel Rivera from Coco, 12 year old boy,
brown skin, white shirt, black vest, red tie,
holding guitar, happy expression,
Pixar animation style, high quality
```

**測試目標**：
- ✅ 確認 Miguel LoRA 正常工作
- ✅ 確認角色特徵正確
- ✅ 然後再加入視頻生成

---

## 🆘 如果還是遇到問題

### 問題：找不到 UnetLoaderGGUF 節點

**解決**：
1. 在 ComfyUI 中點擊右側 **Manager** 按鈕
2. 選擇 **"Install Custom Nodes"**
3. 搜尋 **"ComfyUI-GGUF"** by city96
4. 點擊 **Install**
5. 重啟 ComfyUI

### 問題：GGUF 節點還是不出現

**替代方案**：
- **不使用 GGUF 格式**
- 改用標準的 SDXL + AnimateDiff workflow
- Miguel LoRA + IP-Adapter 一樣能達到角色一致性

---

## 📝 我現在能幫您什麼？

請告訴我：

**選項 A**：我想用 AnimateDiff + IP-Adapter（不用 Wan 2.2）
→ 我會給您完整的 JSON workflow

**選項 B**：我想先測試靜態圖片生成
→ 我會給您最簡單的靜態圖 workflow

**選項 C**：我想繼續嘗試 Wan 2.2 GGUF
→ 我們一起在 Manager 中安裝並測試

**選項 D**：我在 ComfyUI UI 中看到了 XXX 節點
→ 告訴我您看到什麼，我幫您配置

---

**當前狀態**：
- ✅ ComfyUI 運行中
- ✅ 所有模型已下載
- ✅ Miguel LoRA 已就緒
- ⏳ 等待您選擇執行方式

**下一步由您決定！** 🎬
