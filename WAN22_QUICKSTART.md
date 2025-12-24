# 🚀 Wan 2.2 + Miguel LoRA 快速開始指南

## 方式 A：使用我創建的 Workflow（簡化版）

### 步驟 1：準備 Miguel 參考圖
```bash
# 將您的 Miguel 參考圖複製到 ComfyUI input 目錄
cp /path/to/your/miguel_image.png /mnt/c/ai_tools/comfyui/input/miguel_ref.png
```

### 步驟 2：載入 Workflow
1. 打開瀏覽器：http://localhost:8188
2. 拖放檔案：`workflows/miguel_wan22_test.json` 到 ComfyUI 畫布

### 步驟 3：檢查設定
- **LoRA 權重**: 0.8（可調整 0.6-0.9）
- **解析度**: 512x512
- **Seed**: 123456（固定可重複）
- **Steps**: 20
- **CFG**: 7.0

### 步驟 4：點擊 "Queue Prompt" 開始生成

---

## 方式 B：使用 ComfyUI 官方 Template（推薦）

### 步驟 1：載入官方 Wan 2.2 Template

1. 打開 ComfyUI：http://localhost:8188
2. 點擊菜單：**Workflow → Browse Templates**
3. 選擇分類：**Video**
4. 找到並載入：**"Wan2.2 14B I2V"**

### 步驟 2：添加 Miguel LoRA 節點

#### 2.1 添加 LoRA Loader
1. 右鍵點擊畫布 → Add Node
2. 搜尋：**"LoRA Loader"**
3. 添加到畫布

#### 2.2 連接節點
```
原本：[Unet Loader] → [KSampler]
修改後：[Unet Loader] → [LoRA Loader] → [KSampler]
              ↓
         [CLIP Loader] → [LoRA Loader]
```

#### 2.3 配置 LoRA
- **lora_name**: `BEST_CHECKPOINTS_COLLECTION/BEST_miguel_lora_sdxl.safetensors`
- **strength_model**: 0.8
- **strength_clip**: 1.0

### 步驟 3：修改 Prompt

**Positive Prompt（正向提示詞）**:
```
Miguel Rivera from Coco, 12 year old Mexican boy, brown skin,
wearing white shirt, black vest, red tie, dancing happily with guitar,
Pixar animation style, smooth motion, vibrant colors,
detailed character, high quality, cinematic lighting
```

**Negative Prompt（負向提示詞）**:
```
blurry, distorted, low quality, bad anatomy, inconsistent character,
flickering, wrong face, different character, ugly, deformed,
multiple people, crowd
```

### 步驟 4：設定參數（小測試）

#### 基礎設定
- **Resolution**: 512x512（VRAM 安全）
- **Duration**: 5 秒
- **Frame Rate**: 8 fps
- **Seed**: 固定值（如 123456）

#### 進階設定
- **Steps**: 20-25
- **CFG Scale**: 6.5-7.5
- **Sampler**: euler 或 euler_a
- **Scheduler**: normal

### 步驟 5：執行測試
1. 確認所有節點連接正確
2. 點擊 **"Queue Prompt"**
3. 觀察 VRAM 使用情況
4. 等待生成完成（約 10-15 分鐘）

---

## ⚙️ 參數調整建議

### 如果 VRAM 不足
```yaml
Resolution: 512x512 → 448x448
Duration: 5秒 → 3秒
或使用更低量化：Q5_K_M → Q4_K_M
```

### 如果 Miguel 特徵不明顯
```yaml
LoRA 權重: 0.8 → 0.85 或 0.9
Prompt 中加入更詳細的 Miguel 特徵描述
考慮添加 IP-Adapter 節點
```

### 如果運動不自然
```yaml
CFG Scale: 7.0 → 6.0 (降低)
Steps: 20 → 25 (增加)
嘗試不同的 Sampler
```

---

## 📊 預期結果

### 成功指標
- ✅ Miguel 的臉部特徵清晰可辨
- ✅ 服裝顏色正確（白襯衫、黑背心、紅領帶）
- ✅ 動作流暢，無嚴重抖動
- ✅ Pixar 風格明顯
- ✅ VRAM 使用在 14-15GB 以內

### 如果出現問題

#### 問題 1：角色不像 Miguel
**解決**：
- 提高 LoRA 權重到 0.9
- 使用更清晰的參考圖
- 在 Prompt 中加入 "Miguel Rivera from Coco movie"

#### 問題 2：VRAM 溢出 (OOM)
**解決**：
- 降低解析度：512 → 448 → 384
- 減少視頻長度：5秒 → 3秒
- 關閉其他程序釋放 VRAM

#### 問題 3：生成速度太慢
**解決**：
- 降低 Steps：25 → 20
- 使用 Q4_K_M 量化版本
- 這是正常的，Wan 2.2 14B 就是比較慢

#### 問題 4：視頻閃爍或不穩定
**解決**：
- 使用 Low Noise 版本（您已下載）
- 降低 CFG Scale：7.0 → 6.0
- 增加 Steps
- 固定 Seed 確保可重複性

---

## 🎯 測試檢查清單

完成首次測試後，檢查：

- [ ] Miguel 的臉部特徵是否保持一致？
- [ ] 服裝細節是否正確？
- [ ] 動作是否流暢？
- [ ] VRAM 峰值是多少？（記錄下來）
- [ ] 生成時間是多久？（記錄下來）
- [ ] 是否需要調整參數？

---

## 📁 輸出位置

生成的視頻會保存在：
```
/mnt/c/ai_tools/comfyui/output/miguel_wan22_test_XXXXX.mp4
```

---

## 🔄 下一步

測試成功後，您可以：

1. **提升解析度**：512 → 640 → 768
2. **延長時長**：5秒 → 10秒
3. **套用後處理**：RIFE 插值 + ESRGAN 放大
4. **嘗試不同動作**：修改 Prompt
5. **批次生成**：多個場景

---

**準備好了嗎？開始您的第一個 Miguel 視頻測試吧！** 🎬

