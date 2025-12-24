# 以 AnimateDiff 將 3D 動畫逐幀圖片做成 AI 風格短片（給 LLMProvider Tooling 的指令書）

## 1) 背景與目標

我手上有大量 3D 動畫逐幀圖片（image sequence，可能是 PNG/JPG，具備連續幀的動作）。
我的目標是把這些逐幀圖片，透過 AI（Stable Diffusion 生態系）做成**幾秒鐘的動畫短片**，保留原始動作/鏡頭節奏，同時做：

* 風格化（例如：二次元、寫實電影感、賽博龐克、油畫等）
* 細節補全（材質、光影、氛圍）
* 幀與幀之間的穩定一致（避免閃爍、臉崩、細節跳動）
* 最後輸出 mp4/gif（可設定 fps、解析度、長度）

請你（LLMProvider）提供**從零開始到能產出影片**的完整教學與可復現流程，並且優先採用「可視化、容易擴充、適合專案化」的方案。

---

## 2) 技術路線選擇（你要先幫我判斷）

請你先詢問我以下資訊（用簡短清單問就好）：

1. 作業系統：Windows / Linux / macOS
2. 顯卡：NVIDIA 型號、VRAM（例如 8GB/12GB/24GB）
3. 我希望的輸出解析度與秒數（例如 512/768/1024；3–6 秒）
4. 來源是「逐幀圖片」還是「影片」（如果是影片，你要教我先抽幀）
5. 想要的風格（舉例讓我選）
6. 內容是否固定主角/角色（若固定，要強調一致性方案）

然後你做技術選型：

### A 路線（優先推薦）：ComfyUI 工作流

* ComfyUI + ComfyUI-AnimateDiff-Evolved（AnimateDiff 的 ComfyUI 強化整合）([GitHub][2])
* 搭配：影片/序列 I/O 節點（讀取逐幀、輸出 mp4/gif）、ControlNet/深度/邊緣控制、必要時加 IP-Adapter 之類的「角色一致」手段（如果合適）

### B 路線：Stable Diffusion WebUI（AUTOMATIC1111/Forge）

* 安裝 AnimateDiff 擴展，並教我用 img2img / controlnet 讓逐幀轉風格
* 注意：請先提醒我授權/商用限制（若我有商用打算要避開限制或換方案）([GitHub][3])

你要清楚說明為何選 A 或 B，並且給我「如果 VRAM 不夠」的降級策略（降低解析度、減少幀數、縮短 context length、分段生成再拼接等）。

---

## 3) 我需要的最終交付物（你要產出這些）

請你給我：

1. **完整安裝步驟**（逐行命令 + 下載放置路徑 + 常見錯誤排除）
2. **推薦模型清單**（基底模型選擇、Motion module/Lightning 的選擇原則）

   * AnimateDiff 是 plug-and-play motion module 概念，請用白話解釋我該怎麼挑([GitHub][1])
3. **ComfyUI 工作流搭建指南**（我可以照著做出第一支 3–5 秒短片）
4. **從逐幀到影片**的標準流程（含檔名規範、fps、幀數計算）
5. **穩定一致性的策略**（防閃爍、保臉、保服裝細節）
6. **參數建議表**（解析度、steps、CFG、denoise/strength、seed 策略、context 設定）
7. **批次化方案**：我有很多段動畫，要能批次跑（資料夾掃描、多段輸出、命名規則）
8. **品質檢查清單**：如何判斷哪裡出問題、要改哪個旋鈕
9. **最低可行版本（MVP）**：就算我設備普通，也能先做出第一個成果

---

## 4) 逐幀圖片 -> AI 風格短片（你要教的核心工作流）

你要以「我已經有 image sequence」為前提，教我做 **video-to-video / frame-to-frame 的風格轉換**，目標是保留動作。

請你至少提供兩種 workflow：

### Workflow 1：最穩定（保動作優先）

* 讀取逐幀圖片
* （可選）對每幀做控制訊號：depth / lineart / canny / pose（看哪個最適合保 3D 結構）
* 用 AnimateDiff 驅動「時間一致性」，搭配控制訊號讓每幀別亂跑
* 輸出影片

### Workflow 2：更有生成感（風格更強，但風險更高）

* 以關鍵幀/首幀做強約束
* 中間幀給較高自由度（但你要教我怎麼避免閃爍）
* 讓它看起來更「AI 生成」而不是單純濾鏡

若我想跑得快，你可以加一個 Workflow 3（可選）：用 AnimateDiff-Lightning 走低步數加速（並提醒品質可能的差異）。([Hugging Face][4])

---

## 5) 你輸出教學時的格式要求

* 每一步都要可執行（命令、路徑、放檔位置、節點怎麼接）
* 每一段都附「成功長怎樣」與「失敗常見原因」
* 先做最小成果（3 秒、低解析度），成功後再升級（更高解析度、更長、更穩定）

---

## 6) 你需要跟我確認的問題（不可省略）

在你開始給我一大串步驟前，你必須先問我：

* OS / GPU / VRAM
* 我是「逐幀圖片」還是「影片」
* 我想要的輸出秒數、fps、解析度
* 目標風格（我給你參考圖/文字）
* 是否需要固定角色一致（臉、服裝）

問完之後你再給「一條龍」方案與備用方案。

---
[1]: https://github.com/guoyww/AnimateDiff?utm_source=chatgpt.com "guoyww/AnimateDiff: Official implementation of ..."
[2]: https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved?utm_source=chatgpt.com "Kosinkadink/ComfyUI-AnimateDiff-Evolved"
[3]: https://github.com/continue-revolution/sd-webui-animatediff?utm_source=chatgpt.com "AnimateDiff for AUTOMATIC1111 Stable Diffusion WebUI"
[4]: https://huggingface.co/ByteDance/AnimateDiff-Lightning?utm_source=chatgpt.com "ByteDance/AnimateDiff-Lightning"
