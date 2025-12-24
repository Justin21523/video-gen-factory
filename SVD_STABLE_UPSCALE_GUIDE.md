# SVD 穩定生成 + 安全 Upscale 指南

## 🎯 解決的問題

✅ **問題1：4x Upscale 導致記憶體爆滿（OOM）**
- 解決方案：分階段 2x+2x upscale，避免一次性4x upscale

✅ **問題2：SVD 生成的角色容易錯亂、不一致**
- 解決方案：新增穩定性模式，優化 CFG、steps、motion_bucket_id 參數

✅ **問題3：需要同時實現 interpolation + upscale 提升畫質**
- 解決方案：支持幀插值（RIFE）+ 分階段放大（Real-ESRGAN）

---

## 🚀 快速開始

### 推薦配置（高質量 + 穩定 + 安全 4x 放大）

```bash
# 單個視頻測試
python svd_enhanced_batch.py \
  --quality high \
  --characters miguel \
  --max-videos 1 \
  --wait

# 批量生成（推薦）
python svd_enhanced_batch.py \
  --quality high \
  --wait
```

### 最高穩定性配置（角色高度一致）

```bash
python svd_enhanced_batch.py \
  --quality ultra_stable \
  --characters miguel \
  --max-videos 1 \
  --wait
```

---

## 📊 質量預設對比

| 預設 | 穩定性 | Interpolation | Upscale | 記憶體 | 速度 | 適用場景 |
|------|--------|---------------|---------|--------|------|----------|
| **draft** | 中等 | ❌ | ❌ | 低 | ⚡⚡⚡ | 快速預覽 |
| **medium** | 中等 | ✅ 2x | ❌ | 低 | ⚡⚡ | 中等質量（無放大） |
| **high** ⭐ | 高 | ✅ 2x | ✅ 2x+2x | 中 | ⚡ | **推薦：穩定+4x放大** |
| **ultra_stable** | 最高 | ✅ 2x | ✅ 2x+2x | 中 | ⚡ | 角色高度一致 |
| **creative** | 低 | ✅ 3x | ✅ 2x+2x | 中 | ⚡ | 動作場景（更多運動） |

### 詳細配置

#### 🟢 draft - 快速預覽
```
分辨率: 1024×576
幀數: 25
FPS: 16
插值: 無
放大: 無
穩定性: balanced
```

#### 🟡 medium - 中等質量
```
分辨率: 1024×576
幀數: 25 → 50（2x插值）
FPS: 30
插值: ✅ RIFE 2x
放大: 無
穩定性: balanced
```

#### ⭐ high - 高質量（推薦）
```
分辨率: 1024×576 → 4096×2304（4x）
幀數: 25 → 50（2x插值）
FPS: 30
插值: ✅ RIFE 2x
放大: ✅ 2x+2x 安全放大
穩定性: balanced
CFG: 3.5
Steps: 25
Motion: 80
```

#### 🔵 ultra_stable - 最高穩定性
```
分辨率: 1024×576 → 4096×2304（4x）
幀數: 25 → 50（2x插值）
FPS: 30
插值: ✅ RIFE 2x
放大: ✅ 2x+2x 安全放大
穩定性: high ⭐⭐⭐
CFG: 4.0（更貼近輸入圖片）
Steps: 30（更高質量）
Motion: 50（微小動作）
```

#### 🟣 creative - 創意模式
```
分辨率: 1024×576 → 4096×2304（4x）
幀數: 25 → 75（3x插值）
FPS: 48
插值: ✅ RIFE 3x
放大: ✅ 2x+2x 安全放大
穩定性: creative
CFG: 2.5（更多變化）
Steps: 20
Motion: 150（較大運動）
```

---

## 🔧 穩定性模式詳解

### stability_mode 參數

| 模式 | Motion Bucket | CFG | Steps | 效果 |
|------|---------------|-----|-------|------|
| **high** | 50 | 4.0 | 30 | 角色/場景幾乎不變，僅微小動作（呼吸、眨眼） |
| **balanced** | 80 | 3.5 | 25 | 適度運動，保持一致性（推薦） |
| **creative** | 150 | 2.5 | 20 | 較大運動和變化（適合動作場景） |

### 關鍵參數說明

1. **motion_bucket_id**（1-255）
   - 越低 = 越穩定，角色變化越小
   - `50` = 微小動作（高穩定性）
   - `80` = 適度動作（平衡）
   - `150` = 較大動作（創意）

2. **cfg**（1.0-6.0）
   - 越高 = 越貼近輸入圖片
   - `4.0` = 高度一致性
   - `3.5` = 平衡
   - `2.5` = 更多創意

3. **steps**（15-40）
   - 越高 = 質量越好，速度越慢
   - `30` = 高質量
   - `25` = 平衡
   - `20` = 快速

---

## 💾 記憶體管理

### Upscale 策略

| 策略 | 階段 | 記憶體需求 | 速度 | 說明 |
|------|------|-----------|------|------|
| **2x+2x** ⭐ | 2 | 中 | 中 | **推薦：安全避免 OOM** |
| **4x** | 1 | 高 | 快 | 需要大量 VRAM（可能 OOM） |
| **2x** | 1 | 低 | 快 | 僅 2x 放大 |

### 分階段 Upscale 流程（2x+2x）

```
1024×576 (原始SVD輸出)
    ↓
[階段1] 2x upscale → 2048×1152
    ↓
等待完成...
    ↓
[階段2] 2x upscale → 4096×2304 (最終輸出)
```

**優勢：**
- ✅ 避免一次性 4x 導致的 VRAM 爆滿
- ✅ 適合 16GB VRAM
- ✅ 更穩定，成功率更高

---

## 📝 使用範例

### 範例 1：測試單個角色（高質量模式）

```bash
python svd_enhanced_batch.py \
  --quality high \
  --characters miguel \
  --max-videos 1 \
  --wait
```

**輸出：**
```
質量: high
角色: miguel
分辨率: 1024×576 → 4096×2304（2x+2x）
幀數: 25 → 50（RIFE 2x插值）
FPS: 30
穩定性: balanced
```

### 範例 2：最高穩定性測試

```bash
python svd_enhanced_batch.py \
  --quality ultra_stable \
  --characters miguel alberto \
  --max-videos 2 \
  --wait
```

**效果：**
- 角色高度一致（CFG=4.0）
- 微小動作（motion_bucket_id=50）
- 最高採樣質量（steps=30）

### 範例 3：批量生成所有角色（測試模式）

```bash
# 先測試不實際提交
python svd_enhanced_batch.py \
  --quality high \
  --dry-run

# 確認無誤後正式生成
python svd_enhanced_batch.py \
  --quality high \
  --wait
```

### 範例 4：創意模式（動作場景）

```bash
python svd_enhanced_batch.py \
  --quality creative \
  --characters miguel \
  --max-videos 1 \
  --wait
```

**特點：**
- 較大運動變化（motion_bucket_id=150）
- 3x 幀插值（25 → 75幀）
- 48fps 輸出

---

## 🎬 完整工作流程

```
輸入圖片 (PNG)
    ↓
[SVD] 圖片轉視頻
  - 1024×576
  - 25 幀
  - 穩定性優化（CFG, Motion, Steps）
    ↓
[RIFE] 幀插值（可選）
  - 2x: 25→50 幀
  - 3x: 25→75 幀
    ↓
[Real-ESRGAN] 分階段放大（可選）
  - 階段1: 1024×576 → 2048×1152 (2x)
  - 階段2: 2048×1152 → 4096×2304 (2x)
    ↓
[輸出] MP4 視頻
  - 30fps (high/ultra_stable)
  - 48fps (creative)
  - CRF 15-17 (高質量)
```

---

## 🐛 故障排除

### 問題：仍然出現 OOM（記憶體不足）

**解決方案：**
1. 使用更低的質量預設：
   ```bash
   python svd_enhanced_batch.py --quality medium
   ```

2. 關閉 upscale：
   - 編輯 `svd_enhanced_batch.py`
   - 在對應預設中設置 `'enable_upscale': False`

3. 減少幀數：
   - 設置 `'video_frames': 14`（默認 25）

### 問題：角色仍然不夠穩定

**解決方案：**
1. 使用 `ultra_stable` 模式
2. 手動降低 `motion_bucket_id`：
   - 編輯 `svd_enhanced_generator.py`
   - 在 `high` 穩定性模式中設置 `"motion_bucket_id": 30`

3. 提高 CFG：
   - 設置 `cfg: 4.5` 或 `5.0`

### 問題：視頻太慢/太快

**調整 FPS：**
```python
# 在質量預設中修改
'output_fps': 24  # 改為你想要的 fps
```

---

## 📈 效能預估（16GB VRAM）

| 配置 | 單個視頻時間 | 420個視頻總時間 |
|------|-------------|----------------|
| draft | ~30秒 | ~3.5小時 |
| medium | ~1分鐘 | ~7小時 |
| high (2x+2x) | ~2-3分鐘 | ~14-21小時 |
| ultra_stable | ~3-4分鐘 | ~21-28小時 |

**建議：**
- 先用 `--max-videos 1` 測試
- 確認配置無誤後再批量生成
- 使用 `--wait` 自動等待完成

---

## ✨ 總結

### 推薦配置

**一般用途（推薦）：**
```bash
python svd_enhanced_batch.py --quality high --wait
```
- ✅ 穩定性好
- ✅ 4x 安全放大
- ✅ 2x 幀插值
- ✅ 記憶體安全

**角色一致性最高：**
```bash
python svd_enhanced_batch.py --quality ultra_stable --wait
```
- ✅ 最高穩定性（CFG=4.0, Motion=50）
- ✅ 角色幾乎不變
- ✅ 適合需要角色一致性的場景

**動作場景：**
```bash
python svd_enhanced_batch.py --quality creative --wait
```
- ✅ 更大運動變化
- ✅ 3x 幀插值（更流暢）
- ✅ 48fps 輸出

---

## 🔗 相關文件

- `svd_enhanced_batch.py` - 批量生成主程式
- `svd_enhanced_generator.py` - Workflow 生成器（含穩定性模式）
- `video_upscaler.py` - 視頻放大工具（含分階段 upscale）

---

**享受穩定、高質量的 SVD 視頻生成！** 🎉
