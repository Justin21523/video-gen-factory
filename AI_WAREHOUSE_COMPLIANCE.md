# AI_WAREHOUSE 3.0 合规说明

本项目完全遵循 AI_WAREHOUSE 3.0 存储规范。

## ✅ 合规检查清单

### 1. 模型存储位置

- **✅ SVD模型**: `/mnt/c/ai_cache/huggingface/`
  - 通过 `cache_dir` 参数指定
  - 自动下载到正确位置

- **✅ 其他AI模型**: `/mnt/c/ai_models/video/`
  - 预留用于手动下载的模型

### 2. 缓存目录

- **✅ HuggingFace缓存**: `/mnt/c/ai_cache/huggingface/`
  - 环境变量: `HF_HOME`
  - 环境变量: `TRANSFORMERS_CACHE`

- **✅ Torch缓存**: `/mnt/c/ai_cache/torch/`
  - 环境变量: `TORCH_HOME`

- **✅ 通用缓存**: `/mnt/c/ai_cache/`
  - 环境变量: `XDG_CACHE_HOME`

### 3. 项目代码

- **✅ 项目位置**: `/mnt/c/ai_projects/video-gen-factory/`
  - 符合 `ai_projects/<project_name>` 规范

### 4. 数据输出

- **✅ 视频输出**: `/mnt/data/videos/processed/`
  - 生成的视频存储在数据盘

- **✅ 临时文件**: `/mnt/c/tmp/` 或 `/mnt/data/tmp/`
  - 临时下载和解压

## 📁 完整目录映射

### /mnt/c (2TB - 模型和代码)

```
/mnt/c/
├── ai_models/
│   └── video/              # 视频相关模型（预留）
├── ai_cache/
│   ├── huggingface/        # ✅ SVD模型缓存（自动）
│   ├── torch/              # ✅ Torch缓存
│   └── pip/                # pip缓存
├── ai_projects/
│   └── video-gen-factory/  # ✅ 本项目
└── tmp/                    # 临时文件
```

### /mnt/data (4TB - 数据集和训练)

```
/mnt/data/
├── videos/
│   ├── raw/                # 原始视频
│   └── processed/          # ✅ 生成的视频输出
├── extracted/
│   └── frames/             # 提取的帧
├── training/
│   ├── runs/               # 训练运行
│   └── logs/               # 训练日志
└── tmp/                    # 临时数据
```

## 🔧 环境变量设置

### 方法1：运行环境设置脚本（推荐）

```bash
./setup_warehouse_env.sh
```

这会：
1. 设置所有必要的环境变量
2. 创建所需的目录结构
3. 可选地添加到 `~/.bashrc` 使其持久化

### 方法2：手动设置

```bash
export HF_HOME=/mnt/c/ai_cache/huggingface
export TRANSFORMERS_CACHE=/mnt/c/ai_cache/huggingface
export TORCH_HOME=/mnt/c/ai_cache/torch
export XDG_CACHE_HOME=/mnt/c/ai_cache
```

### 方法3：代码自动设置

`svd_pure_python.py` 会在启动时自动设置这些环境变量，无需手动配置。

## 📊 磁盘使用预估

### SVD模型下载

- **模型大小**: 约 3-5GB
- **存储位置**: `/mnt/c/ai_cache/huggingface/`
- **第一次运行**: 需要下载，约5-10分钟
- **后续运行**: 直接从缓存加载

### 视频生成输出

- **单个视频**: 约 50-200MB (取决于质量和时长)
  - 1024×576, 300帧, 60fps, 5秒 ≈ 100MB
- **批量生成**: 420个视频 ≈ 42GB
- **存储位置**: `/mnt/data/videos/processed/`

### 磁盘空间建议

- **最小可用空间**:
  - `/mnt/c`: 10GB (模型 + 缓存)
  - `/mnt/data`: 50GB (视频输出)

- **推荐可用空间**:
  - `/mnt/c`: 50GB
  - `/mnt/data`: 200GB

## ✅ 合规验证

运行以下命令验证设置：

```bash
# 检查环境变量
echo "HF_HOME: $HF_HOME"
echo "TORCH_HOME: $TORCH_HOME"

# 检查目录是否存在
ls -ld /mnt/c/ai_cache/huggingface
ls -ld /mnt/c/ai_models/video
ls -ld /mnt/data/videos/processed

# 检查磁盘空间
df -h /mnt/c
df -h /mnt/data
```

## 🚫 禁止操作

根据 AI_WAREHOUSE 3.0 规范，**绝对不要**：

1. ❌ 在 `$HOME` 下存储大型模型或数据集
2. ❌ 在系统盘 `/` 下存储AI相关文件
3. ❌ 使用旧的 `/mnt/data/ai_data/` 路径
4. ❌ 让缓存默认到 `~/.cache/` 或 `~/.torch/`

## 📝 代码示例

### Python脚本中设置环境变量

```python
import os

# 设置AI_WAREHOUSE 3.0规范的环境变量
os.environ['HF_HOME'] = '/mnt/c/ai_cache/huggingface'
os.environ['TRANSFORMERS_CACHE'] = '/mnt/c/ai_cache/huggingface'
os.environ['TORCH_HOME'] = '/mnt/c/ai_cache/torch'
os.environ['XDG_CACHE_HOME'] = '/mnt/c/ai_cache'
```

### 加载模型时指定缓存目录

```python
from diffusers import StableVideoDiffusionPipeline

pipe = StableVideoDiffusionPipeline.from_pretrained(
    "stabilityai/stable-video-diffusion-img2vid-xt",
    cache_dir="/mnt/c/ai_cache/huggingface"  # 明确指定
)
```

---

**本项目完全符合 AI_WAREHOUSE 3.0 规范** ✅

更新时间: 2025-12-21
