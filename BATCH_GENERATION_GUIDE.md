# 🚀 批量視頻生成系統使用指南

## 系統架構

```
video-gen-factory/
├── characters/              # 角色配置檔
│   ├── miguel.yaml         # Miguel 角色設定
│   ├── alberto.yaml        # Alberto 角色設定
│   └── ...                 # 其他角色
├── workflows/              # ComfyUI workflow 模板
│   └── miguel_cogvideox_base.json
├── input/                  # 參考圖片
│   ├── miguel_ref.png
│   └── ...
├── output/                 # 生成的影片
│   └── CogVideoX_1_5_I2V_*.mp4
├── workflow_generator.py   # Workflow 產生器
└── batch_generate.py       # 批量生成主程式
```

## 快速開始

### 1. 確認 ComfyUI 運行中

```bash
# 檢查 ComfyUI 是否在運行
curl http://127.0.0.1:8188

# 如果沒有運行，啟動它
cd /mnt/c/ai_tools/comfyui
conda activate ai_env
python main.py
```

### 2. 準備參考圖片

將角色參考圖片放到 `input/` 目錄：

```bash
# 確認圖片存在
ls /mnt/c/ai_projects/video-gen-factory/input/miguel_ref.png
```

**重要**: ComfyUI 需要圖片在其 `input/` 目錄中，請確認：
- `/mnt/c/ai_tools/comfyui/input/miguel_ref.png` 存在
- 或建立符號連結：
  ```bash
  ln -s /mnt/c/ai_projects/video-gen-factory/input/* /mnt/c/ai_tools/comfyui/input/
  ```

### 3. 測試單個場景生成

```bash
cd /mnt/c/ai_projects/video-gen-factory

# 預覽模式（不實際執行）
python batch_generate.py --character miguel --scene dancing --dry-run

# 實際生成 Miguel 跳舞場景
python batch_generate.py --character miguel --scene dancing
```

### 4. 批量生成單個角色的所有場景

```bash
# 生成 Miguel 的所有場景（dancing, playing, walking, singing）
python batch_generate.py --character miguel
```

### 5. 批量生成所有角色的所有場景

```bash
# 先預覽
python batch_generate.py --all --dry-run

# 實際執行（會花很長時間！）
python batch_generate.py --all
```

## 角色配置檔格式

### `characters/角色名.yaml`

```yaml
character:
  name: "角色全名"
  lora_path: "路徑/到/lora.safetensors"  # 可選
  lora_strength: 0.8
  reference_images:
    - "/完整/路徑/到/參考圖.png"

  # 基礎描述（會自動加到每個場景的 prompt 前面）
  base_description: "角色基本特徵描述"

  # 場景列表
  scenes:
    - id: "場景ID"  # 用於檔名，例: miguel_dancing_with_guitar.mp4
      prompt: "場景動作描述"
      negative: "負向提示詞"
      seed: 123456  # 隨機種子，固定可重現

generation_settings:
  model: "kijai/CogVideoX-5b-1.5-I2V"
  steps: 25         # 採樣步數，越高越慢但品質更好
  cfg: 6.0          # CFG scale，控制 prompt 影響力
  sampler: "CogVideoXDDIM"
  scheduler: "CogVideoX"
  width: 1360       # 輸出解析度
  height: 768
  frame_rate: 16    # 輸出 fps
  output_prefix: "角色名"  # 輸出檔名前綴
```

## 添加新角色

### 步驟 1: 創建角色配置檔

```bash
cp characters/miguel.yaml characters/新角色名.yaml
```

### 步驟 2: 編輯配置檔

修改以下內容：
- `character.name`: 角色全名
- `character.lora_path`: LoRA 路徑（如果有）
- `character.reference_images`: 參考圖片路徑
- `character.base_description`: 角色基本特徵
- `character.scenes`: 想要生成的場景列表
- `generation_settings.output_prefix`: 輸出檔名前綴

### 步驟 3: 準備參考圖片

```bash
# 複製參考圖片到 input 目錄
cp /路徑/到/角色圖.png input/新角色_ref.png

# 同時複製到 ComfyUI 的 input 目錄
cp input/新角色_ref.png /mnt/c/ai_tools/comfyui/input/
```

### 步驟 4: 測試生成

```bash
# 預覽
python batch_generate.py --character 新角色名 --dry-run

# 生成第一個場景測試
python batch_generate.py --character 新角色名 --scene 場景ID
```

## 進階使用

### 自訂 Workflow 模板

如果需要使用不同的 workflow（例如 CogVideoX + LoRA），可以：

1. 在 ComfyUI 中建立並測試新的 workflow
2. 儲存為 JSON 檔案到 `workflows/` 目錄
3. 修改 `batch_generate.py` 中的模板路徑：

```python
self.generator = WorkflowGenerator(
    template_path='/路徑/到/新模板.json'
)
```

### 並行生成（進階）

當前版本是循序生成（一次一個），如需並行處理：

```bash
# 手動在多個終端中執行不同角色
# Terminal 1:
python batch_generate.py --character miguel

# Terminal 2:
python batch_generate.py --character alberto

# Terminal 3:
python batch_generate.py --character luca
```

### 監控生成進度

```bash
# 查看 ComfyUI 日誌
tail -f /mnt/c/ai_tools/comfyui/comfyui.log

# 查看輸出目錄
ls -lht /mnt/c/ai_tools/comfyui/output/ | head -20
```

## 輸出檔案位置

生成的影片預設在：

```
/mnt/c/ai_tools/comfyui/output/CogVideoX_1_5_I2V_*.mp4
```

檔名格式：
```
角色前綴_場景ID_00001.mp4
```

例如：
- `miguel_dancing_with_guitar_00001.mp4`
- `miguel_playing_guitar_00002.mp4`
- `alberto_vespa_riding_00001.mp4`

## 疑難排解

### 問題 1: "找不到角色配置"

```bash
# 檢查配置檔是否存在
ls characters/角色名.yaml

# 確認檔名拼寫正確（區分大小寫）
```

### 問題 2: "參考圖片未找到"

```bash
# 將圖片複製到 ComfyUI input 目錄
cp input/*.png /mnt/c/ai_tools/comfyui/input/

# 或建立符號連結
ln -sf /mnt/c/ai_projects/video-gen-factory/input /mnt/c/ai_tools/comfyui/input/project_refs
```

### 問題 3: "提交失敗" 或 "連線錯誤"

```bash
# 檢查 ComfyUI 是否運行
curl http://127.0.0.1:8188

# 重啟 ComfyUI
cd /mnt/c/ai_tools/comfyui
conda activate ai_env
python main.py
```

### 問題 4: 生成時間太長

調整配置檔中的參數：

```yaml
generation_settings:
  steps: 15         # 降低步數（從 25 → 15）
  width: 1024       # 降低解析度（從 1360 → 1024）
  height: 576       # （從 768 → 576）
```

### 問題 5: VRAM 不足

CogVideoX-5B-1.5-I2V 需要約 12-16GB VRAM：

- 確認沒有其他程式佔用 GPU
- 降低解析度
- 一次只生成一個場景
- 關閉其他 GPU 程式

## 效能參考

### 單個場景生成時間（RTX 5080 16GB）

| 解析度 | Steps | 預估時間 |
|--------|-------|----------|
| 1360x768 | 25 | 5-8 分鐘 |
| 1024x576 | 25 | 3-5 分鐘 |
| 1360x768 | 15 | 3-5 分鐘 |
| 512x512  | 15 | 1-2 分鐘 |

### 批量生成時間預估

- **單個角色 4 個場景**: 約 20-30 分鐘
- **5 個角色 × 4 場景**: 約 2-3 小時

## 下一步優化

可考慮的改進方向：

1. **並行處理**: 修改腳本支援多個 ComfyUI instance
2. **Resume 功能**: 中斷後可繼續未完成的任務
3. **品質驗證**: 自動檢測生成失敗或品質問題
4. **Web UI**: 建立網頁介面管理批量任務
5. **LoRA 支援**: 當 CogVideoX 支援 LoRA 時整合
6. **通知系統**: 完成後發送 Discord/Email 通知

## 範例 Workflow

### 每日生成工作流

```bash
#!/bin/bash
# daily_generation.sh

cd /mnt/c/ai_projects/video-gen-factory

# 1. 先預覽今天要生成的內容
python batch_generate.py --all --dry-run > preview.txt
cat preview.txt

# 2. 確認無誤後開始生成
python batch_generate.py --all 2>&1 | tee generation.log

# 3. 完成後整理輸出
mkdir -p output/$(date +%Y%m%d)
cp /mnt/c/ai_tools/comfyui/output/*.mp4 output/$(date +%Y%m%d)/

echo "✅ 批量生成完成！輸出在 output/$(date +%Y%m%d)/"
```

---

**當前狀態**: ✅ 系統已就緒，可開始測試生成！
