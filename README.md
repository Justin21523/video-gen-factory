# 🎬 Video Generation Factory

> 注意：此目录已整合进 `ai-gen-hub`。默认使用 `${AI_HUB_ROOT}/video-gen-factory`（可通过环境变量 `VIDEO_FACTORY_ROOT` 覆盖）。

> 使用 ComfyUI + AnimateDiff 将 3D 动画逐帧图片转换为 AI 风格化短视频
>
> **目标风格**：电影级 3D 动画（皮克斯感）- 温暖、家庭向、高品质

---

## 📋 项目概述

本项目提供完整的工作流，将 3D 动画帧序列转换为风格化视频，同时：
- ✅ 保留原始动作和镜头节奏
- ✅ 应用电影级光影材质（S1/S2/S3 三档风格）
- ✅ 维持角色跨片段一致性（L1/L2 两种方案）
- ✅ 支持批次处理多段素材
- ✅ 针对 16GB VRAM 优化

**硬件要求**：
- GPU: NVIDIA RTX 5080 (16GB VRAM)
- 系统: Linux (Ubuntu/Debian)
- 存储: 遵循 `/mnt/c` 和 `/mnt/data` 分区结构

---

## 🗂️ 目录结构（遵循 AI_WAREHOUSE 3.0 规范）

```
# 项目代码
/mnt/c/ai_projects/video-gen-factory/    # 本项目
├── config/
│   └── style_presets.yaml               # S1/S2/S3 风格参数配置
├── docs/
│   └── installation_guide.md            # 详细安装指南
├── scripts/
│   ├── batch_processor.py               # 批次处理脚本
│   └── overlap_blend.py                 # 分段拼接脚本
├── workflows/                           # ComfyUI workflow JSON (需手动创建)
├── input_sequences/                     # 输入帧序列目录
├── reference_images/                    # 角色参考图
├── output_videos/                       # 输出视频
└── README.md                            # 本文档

# ComfyUI 安装位置
/mnt/c/ai_tools/comfyui/                 # ComfyUI 主目录

# 模型存储（遵循规范）
/mnt/c/ai_models/
├── stable-diffusion/                    # Base SD 模型
│   ├── DreamShaper_8_pruned.safetensors
│   └── ToonYou_beta6.safetensors
├── controlnet/                          # ControlNet 模型
│   ├── control_v11f1p_sd15_depth.pth
│   └── control_v11p_sd15_softedge.pth
├── video/                               # AnimateDiff motion modules
│   ├── mm_sd_v15_v2.ckpt
│   └── mm_sd_v15_v3.ckpt
└── clip/                                # CLIP 和 IP-Adapter
    ├── CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors
    ├── ip-adapter-faceid_sd15.bin
    └── ip-adapter-plus_sd15.safetensors

# 数据集和训练输出（如有需要）
/mnt/data/datasets/                      # 大量帧序列数据
/mnt/data/training/                      # LoRA 训练输出
/mnt/data/extracted/                     # 提取的帧/masks
```

---

## 🚀 快速开始

### 第一步：环境配置

```bash
# 激活 conda 环境（优先使用 ai_env）
conda activate ai_env

# 如果遇到依赖冲突，创建专用环境
conda create -n video_env python=3.10 -y
conda activate video_env

# 安装 PyTorch 2.7.1 + CUDA 12.8
pip install torch==2.7.1 torchvision==0.22.1 torchaudio==2.7.1 \
    --index-url https://download.pytorch.org/whl/cu128

# 设置环境变量（添加到 ~/.bashrc）
export HF_HOME=/mnt/c/ai_cache/huggingface
export TRANSFORMERS_CACHE=/mnt/c/ai_cache/huggingface
export TORCH_HOME=/mnt/c/ai_cache/torch
export XDG_CACHE_HOME=/mnt/c/ai_cache
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
```

### 第二步：安装 ComfyUI（如果尚未安装）

ComfyUI 已安装在 `/mnt/c/ai_tools/comfyui/`。如需重新安装或更新：

```bash
cd /mnt/c/ai_tools
git clone https://github.com/comfyanonymous/ComfyUI.git comfyui
cd comfyui

# 安装依赖
pip install -r requirements.txt

# 安装必要 Custom Nodes
cd custom_nodes

# 1. ComfyUI-AnimateDiff-Evolved
git clone https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved.git
cd ComfyUI-AnimateDiff-Evolved && pip install -r requirements.txt && cd ..

# 2. VideoHelperSuite
git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git
cd ComfyUI-VideoHelperSuite && pip install -r requirements.txt && cd ..

# 3. ControlNet Aux
git clone https://github.com/Fannovel16/comfyui_controlnet_aux.git
cd comfyui_controlnet_aux && pip install -r requirements.txt && cd ..

# 4. IP-Adapter Plus
git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus.git

# 5. FreeU Advanced
git clone https://github.com/WASasquatch/FreeU_Advanced.git
```

### 第三步：下载模型（如果尚未下载）

所有模型存储在 `/mnt/c/ai_models/` 下（遵循规范）：

```bash
# Base SD 模型
cd /mnt/c/ai_models/stable-diffusion
wget https://huggingface.co/Lykon/DreamShaper/resolve/main/DreamShaper_8_pruned.safetensors

# AnimateDiff Motion Modules
cd /mnt/c/ai_models/video
wget https://huggingface.co/guoyww/animatediff/resolve/main/mm_sd_v15_v2.ckpt
wget https://huggingface.co/guoyww/animatediff/resolve/main/mm_sd_v15_v3.ckpt

# ControlNet 模型
cd /mnt/c/ai_models/controlnet
wget https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/control_v11f1p_sd15_depth.pth
wget https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/control_v11p_sd15_softedge.pth

# IP-Adapter 和 CLIP
cd /mnt/c/ai_models/clip
wget https://huggingface.co/h94/IP-Adapter-FaceID/resolve/main/ip-adapter-faceid_sd15.bin
wget https://huggingface.co/h94/IP-Adapter/resolve/main/models/ip-adapter-plus_sd15.safetensors
wget https://huggingface.co/h94/IP-Adapter/resolve/main/models/image_encoder/model.safetensors
mv model.safetensors CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors
```

**注意**：ComfyUI 需要创建符号链接指向这些模型目录：

```bash
cd /mnt/c/ai_tools/comfyui

# 创建模型符号链接
ln -s /mnt/c/ai_models/stable-diffusion models/checkpoints
ln -s /mnt/c/ai_models/controlnet models/controlnet
ln -s /mnt/c/ai_models/video models/animatediff_models
ln -s /mnt/c/ai_models/clip models/clip_vision
ln -s /mnt/c/ai_models/clip models/ipadapter
```

### 第四步：准备输入数据

```bash
# 创建场景目录
mkdir -p /mnt/c/ai_projects/video-gen-factory/input_sequences/scene_01_test

# 将你的帧序列放入（格式：frame_0001.png - frame_0144.png）
# 命名规则：frame_XXXX.png（4位零填充）

# 如果有角色参考图（L2方案需要）
mkdir -p /mnt/c/ai_projects/video-gen-factory/reference_images
# 放入 3张正脸 + 4张全身照
```

### 第五步：启动 ComfyUI

```bash
cd /mnt/c/ai_tools/comfyui
conda activate ai_env  # 或 video_env

python main.py --highvram --preview-method auto
# 浏览器打开: http://127.0.0.1:8188
```

---

## 📊 风格参数规格（S1/S2/S3）

所有参数详见 `config/style_presets.yaml`。

### S1：保守风格（Conservative）
- **目标**：轻微增强光影材质，最大化保留原始动作
- **Denoise**: 0.35-0.45 | **CFG**: 6.5-7.5 | **Steps**: 20-22
- **适用**：高保真要求、多角色场景、首次测试
- **VRAM**（768x432）: 9-10GB

### S2：中等风格（Balanced）
- **目标**：电影级光影升级，明显艺术化处理
- **Denoise**: 0.55-0.65 | **CFG**: 8-10 | **Steps**: 25-28
- **适用**：追求电影品质、单主角场景
- **VRAM**（768x432）: 11-12GB（含 IP-Adapter）

### S3：强烈风格（Aggressive）
- **目标**：极致电影感，大幅重构光影材质
- **Denoise**: 0.7-0.8 | **CFG**: 10-13 | **Steps**: 30-35
- **适用**：艺术短片、概念验证
- **VRAM**：必须使用两阶段放大策略
- **注意**：需后期 deflicker 处理

---

## 👤 角色一致性方案（L1/L2）

### L1：基础方案（Prompt + Seed）
- **方法**：固定 Seed + 详细角色 prompt 模板
- **VRAM 开销**：+0GB
- **适用**：VRAM 紧张、简单角色设计
- **一致性**：中等（约70-80%）

### L2：高级方案（IP-Adapter）
- **方法**：IP-Adapter-FaceID（面部）+ IP-Adapter-Plus（整体）
- **VRAM 开销**：+3.5-4.5GB
- **参考图要求**：
  - FaceID: 3张 512x512 正脸特写（用你的 AI 生成角色图）
  - Plus: 4张 768x768 全身照（正/侧/背/45度）
- **一致性**：高（约90-95%）
- **适用**：多片段项目、固定主角 IP

---

## 🎯 MVP 实施路径（渐进式）

### 阶段1：512x288，12fps，3秒（验证）
- **VRAM**: 5-7GB | **耗时**: 2-3分钟
- **目标**：验证 pipeline 可运行
- **参数**：S1 风格，Context 24，仅 Depth ControlNet

### 阶段2：768x432，16fps，3-4秒（中等质量）
- **VRAM**: 10-12GB | **耗时**: 4-6分钟
- **目标**：测试 IP-Adapter 和角色一致性
- **参数**：S2 风格，Context 16，Depth+Softedge，IP-FaceID

### 阶段3：1024x576，16-20fps（高质量预演）
- **VRAM**: 13-15GB | **耗时**: 6-10分钟
- **目标**：压力测试 VRAM 管理
- **参数**：S2/S3，Context 16，完整 IP-Adapter，VAE Tiling

### 阶段4：1280x720，24fps（最终输出）★ 推荐路径
- **策略**：**两阶段放大**（768x432生成 → 1280x720放大）
- **VRAM**: 第1阶段 10-11GB + 第2阶段 8-9GB
- **耗时**: 约 9分钟/3秒
- **验收**：分辨率1280x720，24fps，角色一致，轻微闪烁可后期处理

---

## 🛠️ ComfyUI Workflow 搭建指南（核心节点）

### Workflow A：稳定保真版（推荐用于 S1/S2）

**节点流程**：
```
[LoadImage (VHS)] → [Depth Preprocessor]
    ↓
[CheckpointLoader] → [CLIP Text Encode (Positive/Negative)]
    ↓
[AnimateDiff Loader] → [AnimateDiff Model] (Context=16, mm_sd_v15_v2.ckpt)
    ↓
[Apply ControlNet (Depth, weight=0.75)]
    ↓
[KSampler] (Denoise=0.40, CFG=7.0, Steps=20, DPM++ 2M Karras)
    ↓
[VAE Decode] (启用 Tiling 如果 >=768)
    ↓
[Video Combine (VHS)] → MP4 输出
```

**关键参数**：
- **LoadImage (VHS)**: `Load Image Batch` 节点，目录指向 `input_sequences/scene_01/`
- **Depth Preprocessor**: `MiDaS-DepthMapPreprocessor`，Resolution=512
- **AnimateDiff Context**: 16帧（16GB VRAM 安全值）
- **KSampler Seed**: 固定值（如 42）用于 L1 一致性
- **VAE Tiling**: `VAETileDecode` 节点，Tile Size=512，Overlap=64

### Workflow B：电影风格版（用于 S3）

在 Workflow A 基础上添加：
```
[IP-Adapter Loader] → [IPAdapter Apply (FaceID)]
    ↓
[IP-Adapter Loader] → [IPAdapter Apply (Plus)]
    ↓
[FreeU] (b1=1.2, b2=1.3, s1=0.9, s2=0.2)
```

**注意事项**：
1. IP-Adapter 需要加载参考图（`LoadImage` 节点）
2. FaceID 和 Plus 串联应用，先 FaceID 后 Plus
3. Context 降至 12 以节省 VRAM

### 导出 Workflow
在 ComfyUI 中构建完成后：
1. 点击右侧菜单 "Save"
2. 导出为 JSON
3. 保存到 `/mnt/c/ai_projects/video-gen-factory/workflows/workflow_A_stable.json`

---

## 🔄 批次处理使用

```bash
cd /mnt/c/ai_projects/video-gen-factory

# 确保 ComfyUI 正在运行（http://127.0.0.1:8188）

# 处理所有场景，使用 S2 风格，768x432 分辨率
python scripts/batch_processor.py \
    --style S2_balanced \
    --resolution 768x432

# 多风格、多分辨率批处理
python scripts/batch_processor.py \
    --style S1_conservative S2_balanced \
    --resolution 512x288 768x432

# 仅模拟运行（dry-run）
python scripts/batch_processor.py \
    --style S2_balanced \
    --resolution 768x432 \
    --dry-run
```

**注意**：批次脚本会自动扫描 `input_sequences/` 下的所有子目录。

---

## 🔗 分段拼接（长片段 >5秒）

```bash
# 拼接两个片段（每段48-72帧）
python scripts/overlap_blend.py \
    --segments ./output_segment_01 ./output_segment_02 \
    --output ./final_video.mp4 \
    --overlap 16 \
    --fps 24 \
    --blend-mode cosine
```

**混合模式**：
- `linear`: 线性插值（最快）
- `cosine`: 余弦平滑（推荐，自然过渡）
- `cubic`: 三次 ease-in-out（最平滑）

---

## 📈 VRAM 优化策略（针对 16GB）

### 策略1：降低分辨率
- 1280x720 → 1024x576 → 768x432 → 512x288

### 策略2：调整 Context Length
| 分辨率 | 推荐 | 安全 | 激进 |
|--------|------|------|------|
| 512x288 | 24 | 32 | 48 |
| 768x432 | 16 | 24 | 32 |
| 1024x576 | 16 | 16 | 24 |
| 1280x720 | 12 | 16 | 16 |

### 策略3：两阶段放大（推荐用于 1280x720）
1. **阶段1**：生成 768x432 完整序列（VRAM 10-11GB）
2. **阶段2**：img2img 放大至 1280x720（Denoise=0.25，VRAM 8-9GB）

### 策略4：分段生成 + 拼接
- 120帧分2段，每段60-68帧（16帧 overlap）
- 使用 `overlap_blend.py` 无缝拼接

---

## ⚠️ 常见问题排除

### 1. CUDA out of memory
- **原因**：VRAM 不足
- **解决**：降低分辨率 / 减少 Context / 启用 VAE Tiling / 关闭 IP-Adapter-Plus

### 2. 严重闪烁
- **原因**：Denoise 过高 / ControlNet 权重过低
- **解决**：Denoise 从 0.65 降至 0.55 / Depth 权重提至 0.75-0.8

### 3. 角色崩坏
- **原因**：IP-Adapter 权重过低 / 参考图质量差
- **解决**：FaceID 权重提至 0.75-0.85 / 使用高质量 AI 生成参考图

### 4. 模型加载失败
- **原因**：模型路径错误 / 符号链接失效
- **解决**：检查 `/mnt/c/ai_models/` 结构 / 重新创建符号链接

---

## 📚 参考资源

- [ComfyUI-AnimateDiff-Evolved](https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved)
- [AnimateDiff 官方](https://github.com/guoyww/AnimateDiff)
- [IP-Adapter](https://github.com/tencent-ailab/IP-Adapter)
- [ControlNet](https://github.com/lllyasviel/ControlNet)

---

## 📝 后续步骤

1. **完成环境安装**（参考 `docs/installation_guide.md`）
2. **在 ComfyUI 中手动构建 Workflow A**
3. **从 512x288 MVP 开始测试**
4. **逐步升级到 1280x720 最终输出**
5. **使用批次脚本处理多段素材**

**祝你成功！**🎉
