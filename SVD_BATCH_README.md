# SVD 批量視頻生成系統

使用 Stable Video Diffusion (SVD) 為 14 個 Pixar 角色批量生成 420 個視頻。

## 系統概述

- **總視頻數**: 420 個（14 角色 × 30 張圖片）
- **每個角色**: 30 張圖片（action: 10, expression: 10, pose: 10）
- **選圖方式**: 從每個類別隨機抽取 10 張
- **輸出格式**: MP4 (H.264, 1024×576, 16fps, 25 幀)

## 文件結構

```
video-gen-factory/
├── workflows/
│   └── svd_template.json              # SVD workflow 模板
├── svd_workflow_generator.py          # SVD workflow 生成器
├── svd_batch_generate.py              # 批量生成主腳本
└── SVD_BATCH_README.md                # 本文件
```

## 前置需求

### 1. ComfyUI 環境

建議創建專門的 ComfyUI 虛擬環境：

```bash
# 創建虛擬環境
conda create -n comfyui python=3.10 -y
conda activate comfyui

# 安裝 PyTorch（保持版本穩定）
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 安裝 ComfyUI 依賴
cd /mnt/c/ai_tools/comfyui
pip install -r requirements.txt

# 修復可能的依賴問題
pip install "transformers>=4.41.0,<5.0.0"
pip install "huggingface-hub>=0.16.4,<1.0"
```

### 2. SVD 模型下載

下載 Stable Video Diffusion XT 1.1 模型：

```bash
# 模型位置
mkdir -p /mnt/c/ai_tools/comfyui/models/checkpoints

# 下載 SVD-XT (約 10GB)
# 方法 1: 使用 huggingface-cli
huggingface-cli download stabilityai/stable-video-diffusion-img2vid-xt-1-1 \
  --local-dir /mnt/c/ai_tools/comfyui/models/checkpoints/svd_xt_1_1

# 方法 2: 手動下載
# 訪問: https://huggingface.co/stabilityai/stable-video-diffusion-img2vid-xt-1-1
# 下載 svd_xt_1_1.safetensors 到 models/checkpoints/
```

### 3. 檢查角色圖片數據

```bash
# 確認數據目錄存在
ls /mnt/data/ai_data/synthetic_lora_data/generated_data/

# 應該包含這些角色目錄:
# miguel, alberto, luca, giulia, ian_lightfoot, barley_lightfoot,
# russell, elio, miguel_child, alberto_human, luca_human,
# giulia_summer, ian_confident, elio_space
```

## 使用方法

### 測試模式（推薦先運行）

測試整個流程但不實際提交到 ComfyUI：

```bash
cd /mnt/c/ai_projects/video-gen-factory

# 測試單個角色
python svd_batch_generate.py --dry-run --characters miguel

# 測試所有角色
python svd_batch_generate.py --dry-run

# 測試前 10 個視頻
python svd_batch_generate.py --dry-run --max-videos 10
```

### 正式生成

#### 1. 啟動 ComfyUI

```bash
# 在專門的終端中啟動
conda activate comfyui
cd /mnt/c/ai_tools/comfyui
python main.py --port 8188 --listen 0.0.0.0
```

等待看到 "To see the GUI go to: http://127.0.0.1:8188"

#### 2. 測試單個視頻

先測試一個視頻確保系統正常：

```bash
# 只生成 miguel 的第一個視頻
python svd_batch_generate.py --characters miguel --max-videos 1 --wait
```

成功後檢查輸出：

```bash
ls -lh /mnt/c/ai_tools/comfyui/output/miguel_*.mp4
```

#### 3. 批量生成單個角色

```bash
# 生成 miguel 的所有 30 個視頻
python svd_batch_generate.py --characters miguel --wait

# 生成多個角色
python svd_batch_generate.py --characters miguel alberto luca --wait
```

#### 4. 批量生成所有 420 個視頻

```bash
# 生成所有角色的所有視頻（需要較長時間）
python svd_batch_generate.py --wait
```

**預計時間**:
- 單個視頻約 30-60 秒
- 420 個視頻約 3.5-7 小時

### 後台運行（長時間任務）

```bash
# 使用 nohup 後台運行
nohup python svd_batch_generate.py --wait > svd_batch.log 2>&1 &

# 查看日誌
tail -f svd_batch.log

# 查看進程
ps aux | grep svd_batch
```

## 參數說明

### motion_bucket_id（運動幅度）

系統自動為不同類別設置運動級別：

- **action** (180): 較大運動 - 適合動作場景
- **expression** (80): 微小運動 - 適合表情變化
- **pose** (127): 中等運動 - 適合姿勢展示

可選範圍: 1-255
- 1-50: 幾乎靜止
- 51-127: 輕微到中等運動
- 128-200: 明顯運動
- 201-255: 劇烈運動（可能不穩定）

### video_frames

SVD-XT 支援最多 25 幀（約 1.5 秒 @ 16fps）

### 其他參數

```python
width=1024          # 視頻寬度
height=576          # 視頻高度（SVD 推薦比例 16:9）
fps=16              # 幀率
steps=20            # 採樣步數（更高 = 更好質量但更慢）
cfg=2.5             # CFG 強度（SVD 推薦 2.5）
```

## 輸出組織

生成的視頻自動命名：

```
{角色}_{類別}_{索引}.mp4

範例:
miguel_action_001.mp4
miguel_action_002.mp4
miguel_expression_001.mp4
miguel_pose_001.mp4
alberto_action_001.mp4
...
```

## 監控和管理

### 查看 ComfyUI 狀態

```bash
# 查看隊列狀態
curl http://127.0.0.1:8188/queue

# 查看系統資源
curl http://127.0.0.1:8188/system_stats
```

### 清空隊列（如果需要）

```bash
# 清空所有待處理任務
curl -X POST http://127.0.0.1:8188/queue -d '{"clear": true}'
```

### 檢查生成進度

```bash
# 統計已生成的視頻數量
ls /mnt/c/ai_tools/comfyui/output/*.mp4 | wc -l

# 按角色統計
for char in miguel alberto luca giulia; do
  echo "$char: $(ls /mnt/c/ai_tools/comfyui/output/${char}_*.mp4 2>/dev/null | wc -l)"
done
```

## 故障排除

### VRAM 不足 (OOM)

降低分辨率或幀數：

```python
# 在 svd_batch_generate.py 中修改:
workflow = self.generator.generate_workflow(
    width=768,          # 降低寬度
    height=432,         # 降低高度
    video_frames=14,    # 減少幀數
    ...
)
```

### 生成質量不佳

調整參數：

```python
steps=30,           # 增加步數（更慢但質量更好）
cfg=3.0,            # 增加 CFG（更符合輸入圖片）
```

### ComfyUI 連接失敗

確保 ComfyUI 正在運行：

```bash
curl http://127.0.0.1:8188/system_stats
```

### 圖片找不到

檢查數據路徑：

```bash
# 確認圖片存在
ls /mnt/data/ai_data/synthetic_lora_data/generated_data/miguel/action/images/*.png | head
```

## 高級用法

### 自定義運動級別

編輯 `svd_batch_generate.py` 中的運動映射：

```python
# 為不同類別設置不同的運動級別
if category == 'action':
    motion_bucket_id = 200  # 改為更大運動
elif category == 'expression':
    motion_bucket_id = 50   # 改為更微小運動
```

### 只生成特定類別

修改腳本：

```python
# 只生成 action 類別
self.categories = ['action']
```

或在代碼中過濾：

```python
for category in ['action']:  # 只處理 action
    images = character_images.get(category, [])
    ...
```

## 下一步

1. **質量評估**: 查看生成的視頻，評估質量
2. **參數優化**: 根據結果調整 motion_bucket_id 等參數
3. **組織輸出**: 將視頻按角色和類別整理到子目錄
4. **創建預覽**: 生成視頻縮圖或 GIF 預覽

## 技術支援

- SVD 官方文檔: https://huggingface.co/stabilityai/stable-video-diffusion-img2vid-xt-1-1
- ComfyUI 文檔: https://github.com/comfyanonymous/ComfyUI
- 問題反饋: 查看 ComfyUI 日誌和錯誤信息
