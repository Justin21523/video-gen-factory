# 快速开始 - AI_WAREHOUSE 3.0 合规版

## 🎯 系统概述

**纯Python SVD视频生成系统**
- ❌ 不使用ComfyUI
- ✅ 遵循AI_WAREHOUSE 3.0规范
- ✅ 自动60fps, 5秒输出
- ✅ Upscale提升画质后缩回原尺寸
- ✅ 高稳定性，避免角色错乱

## 🚀 快速开始（3步）

### 步骤1：设置环境（一次性）

```bash
cd /mnt/c/ai_projects/video-gen-factory

# 运行环境设置脚本
./setup_warehouse_env.sh
```

### 步骤2：安装依赖（一次性）

```bash
# 安装Python依赖
./setup_pure_python.sh
```

### 步骤3：生成视频

```bash
# 基础用法（推荐）
python svd_pure_python.py \
  --input your_image.png \
  --output video.mp4

# 最高稳定性
python svd_pure_python.py \
  --input your_image.png \
  --output video.mp4 \
  --motion 50 \
  --guidance 4.0 \
  --steps 30
```

**第一次运行**：会自动下载SVD模型到 `/mnt/c/ai_cache/huggingface/`（约3-5GB，需5-10分钟）

**后续运行**：直接使用缓存模型，快速启动

## 📊 输出规格

所有视频输出：
- **分辨率**: 1024×576
- **帧数**: 300帧
- **FPS**: 60
- **时长**: 5秒
- **画质**: Upscale 4x后缩回（细节增强）

## 🗂️ 文件存储位置

### 模型和缓存（自动）
```
/mnt/c/ai_cache/huggingface/  ← SVD模型（自动下载）
/mnt/c/ai_cache/torch/         ← Torch缓存
```

### 输入图片（手动准备）
```
/mnt/c/ai_projects/video-gen-factory/input_images/
```

### 视频输出（自动生成）
```
/mnt/c/ai_projects/video-gen-factory/  ← 默认输出位置
或
/mnt/data/videos/processed/            ← 推荐（数据盘）
```

## 🎨 稳定性调优

| 场景 | motion | guidance | steps | 效果 |
|------|--------|----------|-------|------|
| **最高稳定** | 50 | 4.0 | 30 | 角色几乎不变 |
| **平衡模式** | 80 | 3.5 | 25 | 适度运动 |
| **创意模式** | 150 | 2.5 | 20 | 较大运动 |

## 💡 常用命令

### 测试单张图片

```bash
python svd_pure_python.py \
  --input test.png \
  --output test_output.mp4 \
  --steps 15 \
  --no-upscale  # 跳过upscale加快测试
```

### 高质量生成

```bash
python svd_pure_python.py \
  --input character.png \
  --output character_hq.mp4 \
  --motion 50 \
  --guidance 4.0 \
  --steps 30 \
  --upscale 4
```

### 批量处理

```bash
# 创建批处理脚本
for img in input_images/*.png; do
    name=$(basename "$img" .png)
    python svd_pure_python.py \
      --input "$img" \
      --output "/mnt/data/videos/processed/${name}.mp4" \
      --motion 80 \
      --guidance 3.5
done
```

## ✅ AI_WAREHOUSE 3.0 合规

本系统完全遵循规范：

- ✅ 模型存储: `/mnt/c/ai_cache/huggingface/`
- ✅ 缓存目录: `/mnt/c/ai_cache/`
- ✅ 项目代码: `/mnt/c/ai_projects/video-gen-factory/`
- ✅ 视频输出: `/mnt/data/videos/processed/`
- ✅ 环境变量: HF_HOME, TORCH_HOME等已设置

详见：`AI_WAREHOUSE_COMPLIANCE.md`

## 🐛 常见问题

### Q: 第一次运行很慢？
A: 正常，需要下载SVD模型（3-5GB）。后续运行会很快。

### Q: 内存不足？
A: 使用 `--no-upscale` 跳过upscale步骤，或降低 `--steps`

### Q: 角色不稳定？
A: 降低 `--motion` (例如50)，提高 `--guidance` (例如4.0)

### Q: 想要更快的生成？
A: 降低 `--steps` 到15-20，使用 `--no-upscale`

## 📚 完整文档

- `PURE_PYTHON_GUIDE.md` - 详细使用指南
- `AI_WAREHOUSE_COMPLIANCE.md` - 存储规范说明
- `setup_warehouse_env.sh` - 环境设置脚本
- `setup_pure_python.sh` - 依赖安装脚本

---

**立即开始：**

```bash
# 1. 设置环境
./setup_warehouse_env.sh

# 2. 准备图片
cp your_image.png input_images/

# 3. 生成视频
python svd_pure_python.py --input input_images/your_image.png --output video.mp4
```

**享受60fps、5秒、高稳定性的SVD视频生成！** 🎉
