#!/bin/bash
# AI_WAREHOUSE 3.0 环境设置脚本
# 确保所有模型和缓存都存储在正确位置

echo "================================"
echo "🏭 AI_WAREHOUSE 3.0 环境设置"
echo "================================"

# 设置环境变量
export HF_HOME=/mnt/c/ai_cache/huggingface
export TRANSFORMERS_CACHE=/mnt/c/ai_cache/huggingface
export TORCH_HOME=/mnt/c/ai_cache/torch
export XDG_CACHE_HOME=/mnt/c/ai_cache

echo ""
echo "✓ 环境变量已设置:"
echo "  HF_HOME=$HF_HOME"
echo "  TRANSFORMERS_CACHE=$TRANSFORMERS_CACHE"
echo "  TORCH_HOME=$TORCH_HOME"
echo "  XDG_CACHE_HOME=$XDG_CACHE_HOME"

# 创建必要的目录结构
echo ""
echo "创建目录结构..."

# 缓存目录 (/mnt/c/ai_cache)
mkdir -p /mnt/c/ai_cache/huggingface
mkdir -p /mnt/c/ai_cache/torch
mkdir -p /mnt/c/ai_cache/pip

# 模型目录 (/mnt/c/ai_models)
mkdir -p /mnt/c/ai_models/video
mkdir -p /mnt/c/ai_models/stable-diffusion
mkdir -p /mnt/c/ai_models/controlnet
mkdir -p /mnt/c/ai_models/lora
mkdir -p /mnt/c/ai_models/embeddings

# 项目输出目录 (/mnt/data)
mkdir -p /mnt/data/videos/processed
mkdir -p /mnt/data/videos/raw
mkdir -p /mnt/data/extracted/frames
mkdir -p /mnt/data/training/runs
mkdir -p /mnt/data/training/logs

echo "✓ 目录结构创建完成"

# 验证磁盘空间
echo ""
echo "磁盘空间检查:"
echo "  /mnt/c (模型和代码，2TB):"
df -h /mnt/c | tail -1 | awk '{print "    使用: " $3 " / " $2 " (" $5 ")"}'
echo "  /mnt/data (数据集和训练，4TB):"
df -h /mnt/data | tail -1 | awk '{print "    使用: " $3 " / " $2 " (" $5 ")"}'

# 添加到 .bashrc (可选)
echo ""
read -p "是否将环境变量添加到 ~/.bashrc? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    cat >> ~/.bashrc << 'EOF'

# AI_WAREHOUSE 3.0 环境变量
export HF_HOME=/mnt/c/ai_cache/huggingface
export TRANSFORMERS_CACHE=/mnt/c/ai_cache/huggingface
export TORCH_HOME=/mnt/c/ai_cache/torch
export XDG_CACHE_HOME=/mnt/c/ai_cache
EOF
    echo "✓ 环境变量已添加到 ~/.bashrc"
    echo "  运行 'source ~/.bashrc' 或重新登录以生效"
else
    echo "⚠️  未添加到 ~/.bashrc，当前会话有效"
    echo "  如需持久化，请手动运行: source ./setup_warehouse_env.sh"
fi

echo ""
echo "================================"
echo "✅ AI_WAREHOUSE 3.0 环境设置完成"
echo "================================"
echo ""
echo "目录说明:"
echo "  /mnt/c/ai_models/    - 所有模型权重"
echo "  /mnt/c/ai_cache/     - HuggingFace/Torch缓存"
echo "  /mnt/c/ai_projects/  - 代码项目"
echo "  /mnt/data/datasets/  - 数据集"
echo "  /mnt/data/training/  - 训练输出"
echo "  /mnt/data/videos/    - 视频输出"
echo ""
