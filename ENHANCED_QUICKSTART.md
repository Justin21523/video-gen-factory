# 🚀 SVD 增強版 - 快速開始（10 分鐘）

生成**高質量 Pixar 角色視頻**，包含幀插值和放大

## 一鍵設置（5 分鐘）

```bash
cd /mnt/c/ai_projects/video-gen-factory

# 運行增強版環境設置腳本
./setup_enhanced_comfyui.sh
```

這會自動：
- ✅ 安裝 PyTorch 2.7.1 (CUDA 12.8)
- ✅ 安裝 ComfyUI-Frame-Interpolation (RIFE)
- ✅ 安裝 ComfyUI-VideoHelperSuite
- ✅ 安裝 Real-ESRGAN
- ✅ 下載 RIFE 4.7 模型
- ✅ 下載 Real-ESRGAN 模型（x2, x4, x4 anime）

## 啟動 ComfyUI（新終端）

```bash
cd /mnt/c/ai_tools/comfyui
python main.py --port 8188 --listen 0.0.0.0
```

等待看到：`To see the GUI go to: http://127.0.0.1:8188`

## 測試各質量級別（5 分鐘）

```bash
cd /mnt/c/ai_projects/video-gen-factory

# 1. Draft 模式（最快 ~30秒）
python svd_enhanced_batch.py --quality draft --characters miguel --max-videos 1 --wait

# 2. Medium 模式（流暢度提升 ~1分鐘）
python svd_enhanced_batch.py --quality medium --characters miguel --max-videos 1 --wait

# 3. High 模式（推薦，高質量 ~2分鐘）
python svd_enhanced_batch.py --quality high --characters miguel --max-videos 1 --wait

# 4. Ultra 模式（極致品質 ~3-5分鐘，需要強大 GPU）
python svd_enhanced_batch.py --quality ultra --characters miguel --max-videos 1 --wait
```

## 查看結果

```bash
ls -lh /mnt/c/ai_tools/comfyui/output/miguel_*

# 對比不同質量
ffprobe /mnt/c/ai_tools/comfyui/output/miguel_action_001_draft.mp4
ffprobe /mnt/c/ai_tools/comfyui/output/miguel_action_001_high.mp4
```

## 開始批量生成

### 選項 A：分批生成（推薦）

```bash
# 每個角色單獨處理（High 質量）
python svd_enhanced_batch.py --quality high --characters miguel --wait      # 30 視頻 ~60分鐘
python svd_enhanced_batch.py --quality high --characters alberto --wait     # 30 視頻 ~60分鐘
python svd_enhanced_batch.py --quality high --characters luca --wait        # 30 視頻 ~60分鐘
# ... 繼續其他角色
```

### 選項 B：全部生成（需 14-35 小時）

```bash
# High 質量（14 小時）
nohup python svd_enhanced_batch.py --quality high --wait > high_batch.log 2>&1 &

# Ultra 質量（21-35 小時，最高品質）
nohup python svd_enhanced_batch.py --quality ultra --wait > ultra_batch.log 2>&1 &

# 查看進度
tail -f high_batch.log
```

## 質量對比一覽表

| 質量 | 分辨率 | 幀數 | 幀率 | 單視頻 | 420總時 | VRAM |
|------|--------|------|------|--------|---------|------|
| Draft | 1024×576 | 25 | 16fps | 30秒 | 3.5小時 | 10-12GB |
| Medium | 1024×576 | 50 | 30fps | 1分鐘 | 7小時 | 12-14GB |
| **High** ⭐ | **2048×1152** | **50** | **30fps** | **2分鐘** | **14小時** | **14-16GB** |
| Ultra | 4096×2304 | 50 | 30fps | 3-5分鐘 | 21-35小時 | 16-24GB |

## 監控進度

```bash
# 實時查看生成數量
watch -n 30 'echo "Draft: $(ls /mnt/c/ai_tools/comfyui/output/*_draft.mp4 2>/dev/null | wc -l)"; \
             echo "Medium: $(ls /mnt/c/ai_tools/comfyui/output/*_medium.mp4 2>/dev/null | wc -l)"; \
             echo "High: $(ls /mnt/c/ai_tools/comfyui/output/*_high.mp4 2>/dev/null | wc -l)"; \
             echo "Ultra: $(ls /mnt/c/ai_tools/comfyui/output/*_ultra.mp4 2>/dev/null | wc -l)"'

# 查看 ComfyUI 隊列
curl -s http://127.0.0.1:8188/queue | jq
```

## 故障排除

### VRAM 不足

```bash
# 使用較低質量
python svd_enhanced_batch.py --quality draft
# 或
python svd_enhanced_batch.py --quality medium
```

### 插件找不到

```bash
# 重新運行設置
./setup_enhanced_comfyui.sh

# 重啟 ComfyUI
```

### 模型下載失敗

```bash
# 手動下載 RIFE
cd /mnt/c/ai_tools/comfyui/custom_nodes/ComfyUI-Frame-Interpolation/ckpts
wget https://github.com/hzwer/Practical-RIFE/releases/download/v4.7/rife47.pth

# 手動下載 Real-ESRGAN
cd /mnt/c/ai_tools/comfyui/models/upscale_models
wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-animevideov3.pth \
     -O RealESRGAN_x4plus_anime_6B.pth
```

## 推薦工作流程

1. **測試階段**（1 小時）
   - 用 Draft 快速生成 10-20 個視頻預覽
   - 確認運動、構圖、風格符合預期

2. **中期生成**（1-2 天）
   - 用 Medium 生成所有 420 個視頻（7 小時）
   - 檢查質量，挑選需要重做的

3. **最終版本**（2-3 天）
   - 用 High 或 Ultra 生成最終版本（14-35 小時）
   - 對特別重要的視頻使用 Ultra

## 總結

**最快路徑**：
```bash
./setup_enhanced_comfyui.sh                    # 5 分鐘
啟動 ComfyUI                                    # 30 秒
測試 High 質量                                  # 2 分鐘
開始批量生成                                    # 14 小時
```

**推薦配置**：High 質量（2048×1152, 50幀, 30fps）

---

**詳細文檔**：`SVD_ENHANCED_README.md`
