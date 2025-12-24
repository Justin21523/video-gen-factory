# 🎬 SVD 增強版批量生成系統

**完整的高質量視頻生成流程**，包含 Frame Interpolation（幀插值）和 Video Upscaling（放大）

## 系統概述

生成 **420 個高質量 Pixar 角色視頻**，包含完整的後處理流程：

```
輸入圖片
    ↓
[SVD] 生成基礎視頻 (1024×576, 25幀, 16fps)
    ↓
[RIFE] 幀插值 (25幀 → 50幀, 16fps → 30fps)
    ↓
[Real-ESRGAN] 視頻放大 (1024×576 → 1920×1080 或 4K)
    ↓
最終輸出：高清流暢視頻
```

## 質量預設

系統提供 4 種質量預設，可根據需求和硬體選擇：

### 1. Draft（草稿模式）⚡ 最快
- **輸出**: 1024×576, 25幀, 16fps
- **處理**: 僅 SVD 生成
- **單視頻時間**: ~30秒
- **420 視頻總時間**: ~3.5小時
- **VRAM 需求**: 10-12GB
- **適用**: 快速預覽、測試

### 2. Medium（中等質量）⭐ 推薦日常
- **輸出**: 1024×576, 50幀, 30fps
- **處理**: SVD + RIFE 幀插值
- **單視頻時間**: ~1分鐘
- **420 視頻總時間**: ~7小時
- **VRAM 需求**: 12-14GB
- **適用**: 平衡質量和速度

### 3. High（高質量）⭐⭐ 推薦高質量
- **輸出**: 2048×1152, 50幀, 30fps
- **處理**: SVD + RIFE + Real-ESRGAN 2x
- **單視頻時間**: ~2分鐘
- **420 視頻總時間**: ~14小時
- **VRAM 需求**: 14-16GB
- **適用**: 高質量發布

### 4. Ultra（極致質量）⭐⭐⭐ 最高品質
- **輸出**: 4096×2304, 50幀, 30fps
- **處理**: SVD + RIFE + Real-ESRGAN 4x
- **單視頻時間**: ~3-5分鐘
- **420 視頻總時間**: ~21-35小時
- **VRAM 需求**: 16-24GB
- **適用**: 專業品質、最終成品

## 前置需求

### 1. PyTorch 環境（用戶指定版本）

```bash
pip install torch==2.7.1 torchvision==0.22.1 torchaudio==2.7.1 --index-url https://download.pytorch.org/whl/cu128
```

### 2. ComfyUI 插件安裝

#### a. Frame Interpolation (RIFE)

```bash
cd /mnt/c/ai_tools/comfyui/custom_nodes
git clone https://github.com/Fannovel16/ComfyUI-Frame-Interpolation
cd ComfyUI-Frame-Interpolation
pip install -r requirements.txt
```

下載 RIFE 模型：

```bash
cd /mnt/c/ai_tools/comfyui/custom_nodes/ComfyUI-Frame-Interpolation/ckpts
wget https://github.com/hzwer/Practical-RIFE/releases/download/v4.7/rife47.pth
```

#### b. Video Helper Suite（視頻處理）

```bash
cd /mnt/c/ai_tools/comfyui/custom_nodes
git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite
cd ComfyUI-VideoHelperSuite
pip install -r requirements.txt
```

#### c. Real-ESRGAN（視頻放大）

```bash
# 通常包含在 ComfyUI 核心中，如果沒有：
pip install realesrgan
```

下載 Real-ESRGAN 模型：

```bash
cd /mnt/c/ai_tools/comfyui/models/upscale_models

# 4x 動畫風格（推薦 Pixar）
wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-animevideov3.pth -O RealESRGAN_x4plus_anime_6B.pth

# 2x 通用
wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.1/RealESRGAN_x2plus.pth

# 4x 通用
wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth
```

### 3. SVD 模型

```bash
cd /mnt/c/ai_tools/comfyui/models/checkpoints
huggingface-cli download stabilityai/stable-video-diffusion-img2vid-xt-1-1 \
  svd_xt_1_1.safetensors --local-dir .
```

## 快速開始

### 1. 測試單個視頻（各質量級別）

```bash
cd /mnt/c/ai_projects/video-gen-factory

# Draft 模式（最快）
python svd_enhanced_batch.py --quality draft --characters miguel --max-videos 1 --wait

# Medium 模式（推薦測試）
python svd_enhanced_batch.py --quality medium --characters miguel --max-videos 1 --wait

# High 模式（高質量）
python svd_enhanced_batch.py --quality high --characters miguel --max-videos 1 --wait

# Ultra 模式（需要強大GPU）
python svd_enhanced_batch.py --quality ultra --characters miguel --max-videos 1 --wait
```

### 2. 批量生成單個角色

```bash
# Miguel 的所有 30 個視頻（High 質量）
python svd_enhanced_batch.py --quality high --characters miguel --wait
```

### 3. 批量生成所有 420 個視頻

```bash
# 分批生成（推薦）
for char in miguel alberto luca giulia ian_lightfoot barley_lightfoot russell elio; do
    python svd_enhanced_batch.py --quality high --characters $char --wait
done

# 或一次全部（後台運行）
nohup python svd_enhanced_batch.py --quality high --wait > svd_enhanced.log 2>&1 &
```

## 輸出文件命名

```
{角色}_{類別}_{索引}_{質量}.mp4

範例:
miguel_action_001_high.mp4
miguel_action_002_high.mp4
miguel_expression_001_high.mp4
alberto_action_001_ultra.mp4
```

## 自定義配置

### 修改質量預設

編輯 `svd_enhanced_batch.py` 中的 `quality_presets`：

```python
'custom': {
    'enable_interpolation': True,
    'interpolation_multiplier': 3,      # 3x 幀插值（75幀）
    'enable_upscale': True,
    'upscale_model': 'RealESRGAN_x4plus_anime_6B.pth',
    'steps': 30,
    'output_fps': 45,                   # 45fps 輸出
    'output_crf': 15,                   # 更高質量
    'description': '自定義質量'
}
```

### 僅幀插值（不放大）

```bash
# 修改質量預設或創建新的
python svd_enhanced_batch.py --quality medium --characters miguel --max-videos 1
```

Medium 預設已經是僅幀插值。

### 僅放大（不幀插值）

創建自定義預設：

```python
'upscale_only': {
    'enable_interpolation': False,
    'enable_upscale': True,
    'upscale_model': 'RealESRGAN_x2plus.pth',
    'steps': 20,
    'output_fps': 16,
    'output_crf': 17,
    'description': '僅放大，無幀插值'
}
```

## 性能優化

### VRAM 不足

1. **使用較低質量預設**
   ```bash
   python svd_enhanced_batch.py --quality draft  # 最低 VRAM
   ```

2. **使用 2x 放大代替 4x**
   ```python
   upscale_model='RealESRGAN_x2plus.pth'  # 需要更少 VRAM
   ```

3. **降低 SVD 基礎分辨率**
   ```python
   # 在 svd_enhanced_generator.py 中修改默認值
   width=768,
   height=432
   ```

### 加速生成

1. **使用 Draft 模式進行預覽**
2. **減少採樣步數**（質量略降）
   ```python
   steps=15  # 從 20 降到 15
   ```
3. **分批處理，避免長時間佔用**

## 質量對比

| 參數 | Draft | Medium | High | Ultra |
|------|-------|--------|------|-------|
| 分辨率 | 1024×576 | 1024×576 | 2048×1152 | 4096×2304 |
| 幀數 | 25 | 50 | 50 | 50 |
| 幀率 | 16fps | 30fps | 30fps | 30fps |
| 幀插值 | ❌ | ✅ 2x | ✅ 2x | ✅ 2x |
| 放大 | ❌ | ❌ | ✅ 2x | ✅ 4x |
| 流暢度 | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 清晰度 | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 時間/視頻 | 30秒 | 1分鐘 | 2分鐘 | 3-5分鐘 |
| 420視頻總時 | 3.5小時 | 7小時 | 14小時 | 21-35小時 |

## 進階用法

### 測試不同參數組合

```bash
# 測試 workflow 生成
python svd_enhanced_generator.py
```

這會生成 3 個測試 workflow：
1. `svd_full_enhanced.json` - 完整增強（插值 + 放大）
2. `svd_interp_only.json` - 僅幀插值
3. `svd_upscale_only.json` - 僅放大

### 監控生成進度

```bash
# 實時查看隊列
watch -n 5 'curl -s http://127.0.0.1:8188/queue | jq'

# 統計已生成視頻
watch -n 30 'ls /mnt/c/ai_tools/comfyui/output/*_high.mp4 | wc -l'

# 按角色和質量統計
for char in miguel alberto luca; do
    for quality in draft medium high ultra; do
        count=$(ls /mnt/c/ai_tools/comfyui/output/${char}_*_${quality}.mp4 2>/dev/null | wc -l)
        echo "$char ($quality): $count"
    done
done
```

## 故障排除

### 問題 1: RIFE 節點找不到

```bash
# 確認插件已安裝
ls /mnt/c/ai_tools/comfyui/custom_nodes/ComfyUI-Frame-Interpolation

# 重啟 ComfyUI
```

### 問題 2: Real-ESRGAN 模型找不到

```bash
# 確認模型在正確位置
ls /mnt/c/ai_tools/comfyui/models/upscale_models/RealESRGAN_*.pth

# 模型名稱要精確匹配 workflow 中的設定
```

### 問題 3: 視頻處理太慢

- 使用較低質量預設
- 降低幀插值倍數
- 使用 2x 放大代替 4x

### 問題 4: VRAM OOM

1. 降低質量預設到 Draft 或 Medium
2. 降低 SVD 基礎分辨率
3. 關閉放大功能，僅使用幀插值

## 技術細節

### 幀插值 (RIFE)

- **RIFE** (Real-Time Intermediate Flow Estimation)
- 通過光流估計生成中間幀
- `multiplier=2`: 幀數翻倍（25 → 50）
- `multiplier=3`: 幀數 3 倍（25 → 75）

### 視頻放大 (Real-ESRGAN)

- **Real-ESRGAN**: 基於 GAN 的超分辨率
- `x2`: 2 倍放大（1024 → 2048）
- `x4`: 4 倍放大（1024 → 4096）
- `anime_6B`: 針對動畫風格優化（推薦 Pixar）

### CRF 值（視頻質量）

- `15`: 近乎無損（Ultra）
- `17`: 極高質量（High）
- `19`: 高質量（Medium）
- `23`: 標準質量（Draft）

## 最佳實踐

1. **先測試單個視頻**: 確認質量符合預期
2. **使用 Medium 進行快速預覽**: 7 小時完成 420 個
3. **最終版用 High 或 Ultra**: 品質保證
4. **分批處理**: 每次 1-2 個角色，方便管理
5. **定期備份**: 生成的視頻及時備份

## 下一步

1. ✅ 安裝所有依賴和插件
2. 🎬 測試各質量預設
3. 📊 選擇適合的質量級別
4. 🚀 開始批量生成
5. 🎨 後製處理（如需要）

---

**完整文檔**: 本文件
**快速開始**: 運行 `python svd_enhanced_batch.py --quality medium --characters miguel --max-videos 1 --wait`
