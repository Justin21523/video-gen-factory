# 🎬 Miguel 視頻生成完整指南

## 兩種方法對比

| 特性 | B1: SVD (img2vid) | B2: AnimateDiff (txt2vid) |
|------|-------------------|---------------------------|
| **輸入** | 1 張圖片 | 文字描述 |
| **輸出長度** | 2-4 秒 (25 幀) | 1.6 秒 (48 幀) |
| **輸出幀率** | 6fps → 30fps (插值) | 直接 30fps |
| **角色一致性** | ⭐⭐⭐⭐⭐ (完美) | ⭐⭐⭐⭐ (需要 LoRA) |
| **動作控制** | ⭐⭐ (隨機運動) | ⭐⭐⭐ (文字控制) |
| **相機運動** | ✅ 可控制 | ❌ 無 |
| **處理時間** | 3-5 分鐘 | 8-12 分鐘 |
| **難度** | 簡單 | 中等 |
| **推薦用途** | **快速原型，相機運動** | **特定動作，多樣性** |

---

## 方法 B1: SVD (Stable Video Diffusion)

### 📖 原理

從**單張圖片**生成 2-4 秒的視頻，自動添加運動和相機移動。

### ✅ 優點

- **極高的角色一致性** - 保持輸入圖片的所有細節
- **相機運動控制** - 可以設置縮放、平移等
- **快速生成** - 3-5 分鐘
- **簡單** - 只需一張好圖片

### ❌ 限制

- 動作**隨機** - 無法精確控制 Miguel 做什麼
- 較短 - 通常 2-4 秒
- 需要**高質量輸入圖片**

### 🎯 使用步驟

#### 1. 在 UI 中操作（推薦）

1. 打開：http://localhost:8188
2. Load → `miguel_img2vid_svd.json`
3. **選擇輸入圖片**：
   - 點擊 Node 1 (LoadImage)
   - 上傳一張 Miguel 圖片（推薦 miguel_ref_face.png）
4. **調整參數**（可選）：
   - Node 4 `motion_bucket_id`:
     - 低 (50-100) = 小動作
     - 中 (127) = 中等運動 ✅ 推薦
     - 高 (200-255) = 大動作
   - Node 4 `video_frames`: 25 (約 4 秒 @ 6fps)
5. Queue Prompt

#### 2. 參數說明

**Node 4: SVD_img2vid_Conditioning**
```
video_frames: 25         # 生成 25 幀
motion_bucket_id: 127    # 運動強度 (0-255)
fps: 6                   # 原始 fps
augmentation_level: 0.0  # 增強級別 (保持 0)
```

**Node 8: VHS_RIFE (幀插值)**
```
multiplier: 5            # 6fps × 5 = 30fps
interpolation: lanczos   # 插值方法
```

#### 3. 輸出文件

```
/mnt/c/ai_tools/comfyui/output/miguel_svd_00001.mp4        (原始 6fps)
/mnt/c/ai_tools/comfyui/output/miguel_svd_30fps_00001.mp4  (插值 30fps) ✅
```

---

## 方法 B2: AnimateDiff txt2vid

### 📖 原理

從**文字描述**生成動畫，使用 Miguel LoRA 確保角色一致性。

### ✅ 優點

- **動作可控** - 通過文字描述控制
- **多樣性高** - 可以生成各種場景
- **無需輸入圖** - 完全從零生成
- **使用 Miguel LoRA** - 角色特徵穩定

### ❌ 限制

- 較慢 - 8-12 分鐘
- 角色一致性**略低於 SVD**
- 需要**好的 prompt**
- 無相機運動

### 🎯 使用步驟

#### 1. 在 UI 中操作（推薦）

1. 打開：http://localhost:8188
2. Load → `miguel_txt2vid_animatediff.json`
3. **修改 Prompt**：
   - Node 3 (Positive Prompt)
   - 修改動作描述，例如：
     ```
     miguel rivera, young boy, dancing happily,
     spinning around, smiling, detailed face,
     smooth motion, vibrant colors, masterpiece
     ```
4. **調整幀數**（可選）：
   - Node 5 `batch_size`:
     - 48 = 1.6 秒 @ 30fps
     - 60 = 2.0 秒
     - 90 = 3.0 秒
5. Queue Prompt

#### 2. Prompt 範例

**走路**：
```
miguel rivera, young boy, walking forward,
confident stride, smiling, detailed face,
smooth motion, cinematic, masterpiece
```

**跳舞**：
```
miguel rivera, young boy, dancing happily,
moving to music, joyful expression,
smooth animation, vibrant colors, masterpiece
```

**揮手**：
```
miguel rivera, young boy, waving hand,
greeting gesture, friendly smile,
detailed face, smooth motion, masterpiece
```

**彈吉他**（Coco 主題）：
```
miguel rivera, young boy, playing guitar,
passionate expression, musical performance,
detailed face, smooth motion, cinematic lighting
```

#### 3. 參數說明

**Node 5: EmptyLatentImage**
```
width: 512
height: 512
batch_size: 48           # 幀數 (48 = 1.6s @ 30fps)
```

**Node 10: KSampler**
```
steps: 30                # 品質步數
cfg: 8.0                 # 提示詞引導強度
denoise: 1.0             # txt2vid 必須是 1.0
```

#### 4. 輸出文件

```
/mnt/c/ai_tools/comfyui/output/miguel_txt2vid_00001.mp4
```

---

## ⚙️ 進階調優

### SVD 參數調優

| 問題 | 解決方案 |
|------|----------|
| 動作太小 | 增加 motion_bucket_id 到 180-200 |
| 動作太大/不穩 | 降低 motion_bucket_id 到 80-100 |
| 角色變形 | 使用更高質量的輸入圖片 |
| 視頻太短 | 增加 video_frames 到 30-35 |

### AnimateDiff txt2vid 調優

| 問題 | 解決方案 |
|------|----------|
| 動作不明顯 | 在 prompt 中加強動作描述詞 |
| 角色特徵不穩 | 檢查 LoRA strength = 1.0 |
| 質量不佳 | 增加 steps 到 35-40 |
| 太短 | 增加 batch_size 到 60-90 |

---

## 🎬 推薦工作流程

### 快速測試（5 分鐘）

1. **使用 SVD**
2. 選擇最好的 Miguel 參考圖
3. motion_bucket_id = 127
4. 生成並查看效果

### 製作特定動作（15 分鐘）

1. **使用 txt2vid**
2. 撰寫詳細 prompt
3. batch_size = 48 先測試
4. 滿意後增加到 90 幀

### 最佳實踐

1. **先用 SVD 測試** - 快速看效果
2. **再用 txt2vid 製作** - 精確控制動作
3. **結合使用** - SVD 用於靜態場景，txt2vid 用於動作場景

---

## 📊 預期處理時間

### RTX 5080 16GB

| 方法 | 配置 | 預計時間 |
|------|------|----------|
| **SVD** | 25 幀, 1024x576, 20 steps | 3-5 分鐘 |
| **SVD + RIFE插值** | 上述 + 插值到 30fps | 4-6 分鐘 |
| **txt2vid** | 48 幀, 512x512, 30 steps | 8-12 分鐘 |
| **txt2vid** | 90 幀, 512x512, 30 steps | 15-20 分鐘 |

---

## 📁 文件位置

```
工作流程：
├── miguel_img2vid_svd.json          ← B1: SVD img2vid
└── miguel_txt2vid_animatediff.json  ← B2: txt2vid

模型：
├── /mnt/c/ai_models/video/stable-video-diffusion/svd_xt.safetensors
└── /mnt/c/ai_models/video/animatediff-sdxl-beta/diffusion_pytorch_model.safetensors

輸出：
└── /mnt/c/ai_tools/comfyui/output/
    ├── miguel_svd_*.mp4
    ├── miguel_svd_30fps_*.mp4
    └── miguel_txt2vid_*.mp4
```

---

## 🚀 立即開始

### 方法 B1 (SVD) - 推薦先試

1. 確認 SVD 模型已下載（檢查終端輸出）
2. 打開 http://localhost:8188
3. Load → `miguel_img2vid_svd.json`
4. 上傳 Miguel 圖片
5. Queue Prompt
6. 等待 3-5 分鐘

### 方法 B2 (txt2vid) - 可立即使用

1. 打開 http://localhost:8188
2. Load → `miguel_txt2vid_animatediff.json`
3. 修改 Prompt（描述想要的動作）
4. Queue Prompt
5. 等待 8-12 分鐘

---

## 💡 Pro Tips

1. **SVD 輸入圖片很重要**：
   - 使用清晰、高分辨率的圖片
   - Miguel 居中，表情自然
   - 背景簡潔

2. **txt2vid Prompt 技巧**：
   - 動詞要具體："walking", "dancing", "waving"
   - 包含情緒："happy", "excited", "calm"
   - 添加細節："smooth motion", "detailed face"

3. **組合使用**：
   - SVD 生成角色參考
   - txt2vid 生成動作序列
   - 後期編輯組合

祝您創作順利！🎉
