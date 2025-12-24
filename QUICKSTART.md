# 🚀 SVD 批量生成 - 快速開始指南

生成 420 個 Pixar 角色視頻的最快路徑（10 分鐘內開始）

## 第一步：環境設置（5 分鐘）

```bash
cd /mnt/c/ai_projects/video-gen-factory

# 運行環境設置腳本
./setup_comfyui_env.sh

# 激活環境
conda activate comfyui
```

## 第二步：下載 SVD 模型（一次性，約 10GB）

```bash
# 進入模型目錄
cd /mnt/c/ai_tools/comfyui/models/checkpoints

# 下載 SVD-XT 模型
huggingface-cli download stabilityai/stable-video-diffusion-img2vid-xt-1-1 \
  svd_xt_1_1.safetensors --local-dir .
```

**或手動下載**:
1. 訪問 https://huggingface.co/stabilityai/stable-video-diffusion-img2vid-xt-1-1/tree/main
2. 下載 `svd_xt_1_1.safetensors` (約 10GB)
3. 放到 `/mnt/c/ai_tools/comfyui/models/checkpoints/`

## 第三步：啟動 ComfyUI（在新終端）

```bash
conda activate comfyui
cd /mnt/c/ai_tools/comfyui
python main.py --port 8188 --listen 0.0.0.0
```

等待看到：`To see the GUI go to: http://127.0.0.1:8188`

## 第四步：測試設置（在原終端）

```bash
cd /mnt/c/ai_projects/video-gen-factory
python test_svd_setup.py
```

應該看到所有測試通過 ✅

## 第五步：生成第一個視頻（測試）

```bash
# 生成 Miguel 的第一個視頻
python svd_batch_generate.py --characters miguel --max-videos 1 --wait
```

成功後檢查輸出：

```bash
ls -lh /mnt/c/ai_tools/comfyui/output/miguel_*.mp4
```

## 第六步：批量生成所有視頻

### 選項 A：分批生成（推薦）

每次生成一個角色的 30 個視頻：

```bash
# Miguel (30 個視頻，約 15-30 分鐘)
python svd_batch_generate.py --characters miguel --wait

# Alberto
python svd_batch_generate.py --characters alberto --wait

# Luca
python svd_batch_generate.py --characters luca --wait

# ... 依此類推
```

### 選項 B：全部生成（需要 4-7 小時）

```bash
# 後台運行所有 420 個視頻
nohup python svd_batch_generate.py --wait > svd_batch.log 2>&1 &

# 查看進度
tail -f svd_batch.log

# 或統計已生成數量
watch -n 30 'ls /mnt/c/ai_tools/comfyui/output/*.mp4 | wc -l'
```

## 常見問題

### Q: VRAM 不足怎麼辦？

編輯 `svd_batch_generate.py`，降低分辨率：

```python
workflow = self.generator.generate_workflow(
    width=768,          # 從 1024 降到 768
    height=432,         # 從 576 降到 432
    video_frames=14,    # 從 25 降到 14
    ...
)
```

### Q: 如何更改運動幅度？

在 `svd_batch_generate.py` 中修改：

```python
if category == 'action':
    motion_bucket_id = 200  # 增加運動（默認 180）
elif category == 'expression':
    motion_bucket_id = 50   # 減少運動（默認 80）
```

### Q: 視頻質量不好？

增加採樣步數：

```python
workflow = self.generator.generate_workflow(
    steps=30,           # 從 20 增加到 30
    cfg=3.0,            # 從 2.5 增加到 3.0
    ...
)
```

### Q: 只想生成特定類別？

```bash
# 在 svd_batch_generate.py 中修改:
self.categories = ['action']  # 只生成 action
```

## 輸出組織

生成後整理視頻：

```bash
# 創建按角色分類的目錄
cd /mnt/c/ai_tools/comfyui/output
for char in miguel alberto luca giulia; do
    mkdir -p $char
    mv ${char}_*.mp4 $char/
done
```

## 監控和統計

```bash
# 實時查看隊列
watch -n 5 'curl -s http://127.0.0.1:8188/queue | jq'

# 統計已生成視頻
find /mnt/c/ai_tools/comfyui/output -name "*.mp4" | wc -l

# 按角色統計
for char in miguel alberto luca giulia ian_lightfoot barley_lightfoot russell elio; do
    count=$(find /mnt/c/ai_tools/comfyui/output -name "${char}_*.mp4" | wc -l)
    echo "$char: $count 個視頻"
done
```

## 下一步

1. ✅ **質量檢查**: 隨機抽查生成的視頻
2. 📊 **統計分析**: 查看哪些參數效果最好
3. 🎨 **後製處理**: 考慮視頻編輯、特效等
4. 📦 **組織歸檔**: 整理和備份生成的視頻

---

**完整文檔**: 查看 `SVD_BATCH_README.md` 瞭解詳細信息
