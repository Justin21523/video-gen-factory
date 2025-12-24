# 🎬 一键开始 - Video Generation Factory

## ✅ 所有前置工作已完成！

您现在只需要 **2 个步骤** 就能生成 Pixar 风格的 Miguel 动画！

---

## 📋 已为您准备好的内容

### 1. 环境配置 ✓
- Ubuntu + RTX 5080 16GB
- ComfyUI 已安装并运行中
- 所有必要插件已安装
- VRAM 已优化（14.4GB 可用）

### 2. 模型文件 ✓
- **SDXL 基础模型**: sd_xl_base_1.0.safetensors (6.5GB)
- **Pixar 风格 LoRA**: PixarXL.safetensors (218MB)
- **AnimateDiff SDXL**: diffusion_pytorch_model.safetensors
- **IP-Adapter SDXL**: ip-adapter-plus_sdxl_vit-h.safetensors
- **CLIP Vision**: model.safetensors

### 3. Miguel 角色数据 ✓
- **参考图片**: 3 张精选（面部/姿势/动作）
  - `/mnt/c/ai_tools/comfyui/input/miguel_ref_face.png`
  - `/mnt/c/ai_tools/comfyui/input/miguel_ref_pose.png`
  - `/mnt/c/ai_tools/comfyui/input/miguel_ref_action.png`

### 4. 测试数据 ✓
- **测试图像序列**: 24 帧 (0.8 秒 @ 30fps)
  - 位置: `/mnt/c/ai_projects/video-gen-factory/input_sequences/scene_01_test/`
  - 格式: `frame_0001.png` 到 `frame_0024.png`

### 5. Workflow 配置 ✓
- **SDXL Workflow**: `workflows/pixar_ipadapter_animatediff_SDXL.json`
- 配置:
  - 输出分辨率: 1024x576
  - 帧率: 30fps
  - Denoise: 0.6 (中等风格化)
  - IP-Adapter 权重: 0.8 (强角色一致性)

---

## 🚀 开始生成（只需 2 步！）

### 方案 A：一键运行脚本（推荐）

```bash
cd /mnt/c/ai_projects/video-gen-factory
conda activate ai_env
python run_generation.py
```

**就这样！** 脚本会自动：
- 检查 ComfyUI 状态
- 提交 workflow
- 监控生成进度
- 完成后告诉您输出位置

**预计时间**: 约 5-10 分钟（24 帧）

---

### 方案 B：通过浏览器手动运行

#### 步骤 1：打开 ComfyUI
浏览器访问：http://localhost:8188

#### 步骤 2：加载 Workflow
1. 点击右上角的 **Load** 按钮
2. 选择文件：
   ```
   /mnt/c/ai_projects/video-gen-factory/workflows/pixar_ipadapter_animatediff_SDXL.json
   ```
3. 点击 **Queue Prompt** 开始生成

---

## 📂 输出位置

生成完成后，您的视频会保存在：

```
/mnt/c/ai_projects/video-gen-factory/output_videos/miguel_pixar_sdxl_*.mp4
```

同时还会保存单独的帧图片：

```
/mnt/c/ai_projects/video-gen-factory/output_videos/miguel_pixar_sdxl_frames_*.png
```

---

## 🎯 测试后的下一步

### 如果测试成功

**替换成您的真实 3D 动画帧**：
1. 将您的 3D 动画帧序列放到：
   ```
   /mnt/c/ai_projects/video-gen-factory/input_sequences/scene_01_test/
   ```
2. 删除现有的测试帧：
   ```bash
   rm /mnt/c/ai_projects/video-gen-factory/input_sequences/scene_01_test/*.png
   ```
3. 复制您的帧（确保命名格式为 `frame_XXXX.png`）
4. 再次运行 `python run_generation.py`

### 如果需要调整参数

编辑 workflow 文件中的关键参数：
```bash
nano workflows/pixar_ipadapter_animatediff_SDXL.json
```

**常用调整**：
- **Denoise** (节点 17)：控制风格化强度
  - 0.4-0.5: 保守（更接近原始）
  - 0.6-0.7: 中等（推荐）
  - 0.7-0.8: 强烈（更艺术化）

- **IP-Adapter Weight** (节点 9)：控制角色一致性
  - 0.6-0.7: 较弱
  - 0.8: 推荐
  - 0.9-1.0: 非常强

- **CFG Scale** (节点 17)：控制提示词遵循度
  - 6.0-7.0: 较自由
  - 7.5: 推荐
  - 8.0-9.0: 严格遵循

- **Steps** (节点 17)：推理步数
  - 20: 快速测试
  - 25: 推荐
  - 30-35: 最高质量（更慢）

---

## 🔧 如果遇到问题

### ComfyUI 未运行？
```bash
cd /mnt/c/ai_tools/comfyui
conda activate ai_env
python main.py --listen 0.0.0.0 --port 8188 --preview-method auto
```

### VRAM 不足 (OOM)？
1. 降低分辨率：编辑节点 11 的 width/height
   - 768x432 → 640x360
2. 减少帧数：编辑节点 10 的 image_load_cap
   - 24 → 16
3. 降低 Context Length：编辑节点 14
   - 16 → 12

### 角色不一致？
1. 提高 IP-Adapter weight（节点 9）：0.8 → 0.9
2. 降低 denoise（节点 17）：0.6 → 0.5
3. 在 Positive Prompt（节点 3）中添加更详细的角色描述

### 生成太慢？
1. 降低 steps（节点 17）：25 → 20
2. 使用更小的分辨率测试
3. 减少帧数

---

## 📊 系统状态

**当前配置**：
- GPU: RTX 5080 16GB
- 可用 VRAM: 14.4 GB
- ComfyUI: 运行中 (http://localhost:8188)
- Python环境: ai_env
- 测试数据: 24 帧序列已就绪
- 参考图片: 3 张 Miguel 图片已准备

**预估性能**：
- 24 帧 (768x432): ~5-8 分钟
- 48 帧 (768x432): ~10-15 分钟
- 24 帧 (1024x576): ~8-12 分钟

---

## 🎉 准备好了！

**您现在只需要运行**：

```bash
cd /mnt/c/ai_projects/video-gen-factory
conda activate ai_env
python run_generation.py
```

就可以看到 Miguel 的 Pixar 风格动画生成了！🚀

---

## 📞 需要帮助？

- **详细文档**: `README.md`
- **参数调优**: `config/style_presets.yaml`
- **Workflow 构建指南**: `docs/workflow_pixar_ipadapter_guide.md`
- **快速开始**: `QUICKSTART.md`
