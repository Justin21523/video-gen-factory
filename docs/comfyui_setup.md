# ComfyUI 配置指南（遵循 AI_WAREHOUSE 3.0 规范）

本文档说明如何配置 ComfyUI 以使用正确的模型路径和缓存目录。

---

## 1. 创建模型符号链接

由于 ComfyUI 默认从 `models/` 子目录加载模型，而我们的模型存储在 `/mnt/c/ai_models/`，需要创建符号链接。

```bash
cd /mnt/c/ai_tools/comfyui

# 备份原有 models 目录（如果存在）
if [ -d "models" ]; then
    mv models models_backup_$(date +%Y%m%d)
fi

# 创建新的 models 目录
mkdir -p models

# 创建符号链接到统一模型存储
ln -s /mnt/c/ai_models/stable-diffusion models/checkpoints
ln -s /mnt/c/ai_models/controlnet models/controlnet
ln -s /mnt/c/ai_models/video models/animatediff_models
ln -s /mnt/c/ai_models/clip models/clip_vision
ln -s /mnt/c/ai_models/clip models/ipadapter
ln -s /mnt/c/ai_models models/upscale_models

# 验证链接
ls -lh models/
```

**预期输出**：
```
checkpoints -> /mnt/c/ai_models/stable-diffusion
controlnet -> /mnt/c/ai_models/controlnet
animatediff_models -> /mnt/c/ai_models/video
clip_vision -> /mnt/c/ai_models/clip
ipadapter -> /mnt/c/ai_models/clip
```

---

## 2. 配置环境变量

编辑 `~/.bashrc` 添加以下环境变量：

```bash
nano ~/.bashrc
```

添加内容：

```bash
# ========== AI_WAREHOUSE 3.0 环境变量 ==========

# HuggingFace 缓存
export HF_HOME=/mnt/c/ai_cache/huggingface
export TRANSFORMERS_CACHE=/mnt/c/ai_cache/huggingface

# PyTorch 缓存
export TORCH_HOME=/mnt/c/ai_cache/torch

# 通用缓存
export XDG_CACHE_HOME=/mnt/c/ai_cache

# CUDA 内存优化
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
export CUDA_VISIBLE_DEVICES=0

# ComfyUI 路径（可选）
export COMFYUI_HOME=/mnt/c/ai_tools/comfyui
```

保存后生效：

```bash
source ~/.bashrc
```

---

## 3. 创建缓存目录

```bash
# 创建所有必要的缓存目录
mkdir -p /mnt/c/ai_cache/huggingface
mkdir -p /mnt/c/ai_cache/torch
mkdir -p /mnt/c/ai_cache/pip

# 设置权限
chmod -R 755 /mnt/c/ai_cache
```

---

## 4. ComfyUI 启动脚本

创建优化的启动脚本：

```bash
cd /mnt/c/ai_tools/comfyui
nano start_comfyui.sh
```

添加内容：

```bash
#!/bin/bash

# 激活 conda 环境
source ~/miniconda3/etc/profile.d/conda.sh
conda activate ai_env  # 或 video_env

# 设置环境变量（确保生效）
export HF_HOME=/mnt/c/ai_cache/huggingface
export TRANSFORMERS_CACHE=/mnt/c/ai_cache/huggingface
export TORCH_HOME=/mnt/c/ai_cache/torch
export XDG_CACHE_HOME=/mnt/c/ai_cache
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512

# 启动 ComfyUI（针对 16GB VRAM 优化）
python main.py \\
    --highvram \\
    --preview-method auto \\
    --use-split-cross-attention \\
    --port 8188

# 如果 VRAM 经常 OOM，使用：
# python main.py --normalvram --preview-method auto --port 8188
```

保存并赋予执行权限：

```bash
chmod +x start_comfyui.sh
```

使用：

```bash
cd /mnt/c/ai_tools/comfyui
./start_comfyui.sh
```

---

## 5. 验证配置

启动 ComfyUI 后，检查模型是否正确加载：

```bash
# 在浏览器打开
http://127.0.0.1:8188

# 在 ComfyUI 界面中：
# 1. 右键 → Add Node → loaders → Load Checkpoint
# 2. 点击模型下拉菜单
# 3. 应该能看到 DreamShaper_8_pruned.safetensors
```

检查缓存目录使用情况：

```bash
du -sh /mnt/c/ai_cache/*
```

---

## 6. 常见问题

### Q1: ComfyUI 找不到模型
**A**: 检查符号链接是否正确：
```bash
cd /mnt/c/ai_tools/comfyui
ls -la models/checkpoints  # 应该指向 /mnt/c/ai_models/stable-diffusion
```

### Q2: 缓存仍然写入 ~/.cache
**A**: 确保环境变量已生效：
```bash
echo $HF_HOME  # 应输出 /mnt/c/ai_cache/huggingface
```

如果为空，手动执行：
```bash
source ~/.bashrc
```

### Q3: AnimateDiff 节点找不到 motion module
**A**: 检查符号链接：
```bash
ls -lh /mnt/c/ai_tools/comfyui/models/animatediff_models
# 应该指向 /mnt/c/ai_models/video
```

### Q4: IP-Adapter 报错 CLIP model not found
**A**: 确保 CLIP 模型在正确位置：
```bash
ls -lh /mnt/c/ai_models/clip/CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors
```

并且符号链接正确：
```bash
ls -lh /mnt/c/ai_tools/comfyui/models/clip_vision
ls -lh /mnt/c/ai_tools/comfyui/models/ipadapter
```

---

## 7. 完整目录检查清单

运行以下命令验证所有配置：

```bash
#!/bin/bash

echo "=== 检查 ComfyUI 配置 ==="
echo ""

echo "1. ComfyUI 目录:"
ls -ld /mnt/c/ai_tools/comfyui
echo ""

echo "2. 模型符号链接:"
ls -lh /mnt/c/ai_tools/comfyui/models/
echo ""

echo "3. 模型存储目录:"
du -sh /mnt/c/ai_models/*
echo ""

echo "4. 缓存目录:"
du -sh /mnt/c/ai_cache/*
echo ""

echo "5. 环境变量:"
echo "HF_HOME=$HF_HOME"
echo "TORCH_HOME=$TORCH_HOME"
echo "XDG_CACHE_HOME=$XDG_CACHE_HOME"
echo ""

echo "6. Conda 环境:"
conda env list | grep -E "(ai_env|video_env)"
echo ""

echo "=== 检查完成 ==="
```

保存为 `check_config.sh` 并运行：

```bash
chmod +x check_config.sh
./check_config.sh
```

---

## 8. 迁移旧配置（如果有）

如果之前在其他位置安装了 ComfyUI 或模型：

```bash
# 移动旧模型到新位置
# 例如：从 ~/ComfyUI/models/checkpoints 移动到 /mnt/c/ai_models/stable-diffusion
mv ~/ComfyUI/models/checkpoints/*.safetensors /mnt/c/ai_models/stable-diffusion/

# 移动 AnimateDiff motion modules
mv ~/ComfyUI/models/animatediff_models/*.ckpt /mnt/c/ai_models/video/

# 移动 ControlNet
mv ~/ComfyUI/models/controlnet/*.pth /mnt/c/ai_models/controlnet/

# 然后删除旧的 ComfyUI 目录（可选）
# rm -rf ~/ComfyUI
```

---

## 9. 下一步

配置完成后：
1. 启动 ComfyUI: `./start_comfyui.sh`
2. 参考 README.md 构建第一个 Workflow
3. 从 512x288 MVP 开始测试

**祝配置顺利！**
