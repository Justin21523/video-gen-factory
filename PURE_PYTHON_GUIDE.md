# 纯Python SVD视频生成指南

## 🎯 特点

✅ **不依赖ComfyUI** - 纯Python实现
✅ **60fps, 5秒输出** - 300帧流畅视频
✅ **Upscale提升画质** - 4x放大后缩回原尺寸
✅ **高稳定性** - 优化参数避免角色错乱
✅ **简单易用** - 一行命令搞定

---

## 📦 安装

### 1. 运行安装脚本

```bash
./setup_pure_python.sh
```

### 2. 手动安装（如果脚本失败）

```bash
# 核心库
pip install --upgrade diffusers transformers accelerate

# 图像处理
pip install opencv-python-headless pillow numpy

# PyTorch (如果还没有)
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

---

## 🚀 快速开始

### 基础用法

```bash
python svd_pure_python.py \
  --input your_image.png \
  --output video.mp4
```

**输出：**
- 分辨率：1024×576
- 帧数：300帧
- FPS：60
- 时长：5秒
- 稳定性：高

### 最高稳定性（推荐）

```bash
python svd_pure_python.py \
  --input your_image.png \
  --output video.mp4 \
  --motion 50 \
  --guidance 4.0 \
  --steps 30
```

---

## 📊 参数说明

| 参数 | 默认值 | 范围 | 说明 |
|------|--------|------|------|
| `--input` | - | - | **必需**：输入图片路径 |
| `--output` | output.mp4 | - | 输出视频路径 |
| `--motion` | 80 | 1-255 | 运动强度（越低越稳定） |
| `--guidance` | 3.5 | 1.0-6.0 | 引导强度（越高越贴近输入） |
| `--steps` | 25 | 15-40 | 采样步数（越高质量越好） |
| `--upscale` | 4 | 2-4 | 临时放大倍数 |
| `--no-upscale` | - | - | 跳过upscale步骤 |

---

## 🎨 稳定性配置

### 🟢 最高稳定性（角色几乎不变）

```bash
python svd_pure_python.py \
  --input image.png \
  --motion 50 \
  --guidance 4.0 \
  --steps 30
```

**特点：**
- Motion: 50（微小动作）
- Guidance: 4.0（高度贴近输入）
- Steps: 30（最高质量）
- 适合：需要角色高度一致的场景

### 🟡 平衡模式（推荐日常使用）

```bash
python svd_pure_python.py \
  --input image.png \
  --motion 80 \
  --guidance 3.5 \
  --steps 25
```

**特点：**
- Motion: 80（适度运动）
- Guidance: 3.5（平衡）
- Steps: 25（标准质量）
- 适合：大部分场景

### 🔴 创意模式（更多运动）

```bash
python svd_pure_python.py \
  --input image.png \
  --motion 150 \
  --guidance 2.5 \
  --steps 20
```

**特点：**
- Motion: 150（较大运动）
- Guidance: 2.5（更多变化）
- Steps: 20（快速）
- 适合：动作场景

---

## 🔧 工作流程

```
输入图片 (PNG/JPG)
    ↓
[1] SVD生成 (diffusers)
    - 1024×576
    - 25帧
    - 稳定性优化
    ↓
[2] 插值到300帧
    - 线性插值
    - 25帧 → 300帧 (12x)
    ↓
[3] Upscale提升画质
    - 放大: 1024×576 → 4096×2304 (4x)
    - 缩小: 4096×2304 → 1024×576
    - 目的：提升细节和清晰度
    ↓
[4] 保存视频
    - MP4格式
    - 60fps
    - 5秒时长
```

---

## 💡 Upscale原理

**为什么要先放大再缩小？**

```
原始帧 (1024×576)
    ↓
放大4x (4096×2304)  ← 使用高质量算法(Lanczos)增加细节
    ↓
缩小回原尺寸 (1024×576)  ← 保留增强的细节，减少噪点
    ↓
结果：画质提升，细节更清晰
```

**对比：**
| 方法 | 画质 | 处理时间 | 文件大小 |
|------|------|---------|---------|
| 不upscale | 中等 | 快 | 正常 |
| upscale 2x | 较好 | 中等 | 正常 |
| upscale 4x | 最好 | 较慢 | 正常 |

---

## 📝 使用示例

### 示例1：单张图片测试

```bash
# 假设你有一张图片: miguel.png
python svd_pure_python.py \
  --input miguel.png \
  --output miguel_test.mp4 \
  --motion 80 \
  --guidance 3.5
```

**预计时间：** 2-5分钟（取决于GPU）

### 示例2：批量处理多张图片

创建批处理脚本 `batch_process.sh`:

```bash
#!/bin/bash

for img in input_images/*.png; do
    basename=$(basename "$img" .png)
    echo "处理: $basename"

    python svd_pure_python.py \
      --input "$img" \
      --output "output_videos/${basename}.mp4" \
      --motion 80 \
      --guidance 3.5 \
      --steps 25
done

echo "完成！"
```

运行：
```bash
chmod +x batch_process.sh
./batch_process.sh
```

### 示例3：不同稳定性对比

```bash
# 高稳定性
python svd_pure_python.py --input test.png --output test_stable.mp4 --motion 50 --guidance 4.0

# 平衡模式
python svd_pure_python.py --input test.png --output test_balanced.mp4 --motion 80 --guidance 3.5

# 创意模式
python svd_pure_python.py --input test.png --output test_creative.mp4 --motion 150 --guidance 2.5
```

---

## ⚡ 性能优化

### GPU内存不足？

1. **跳过upscale**：
```bash
python svd_pure_python.py --input image.png --no-upscale
```

2. **降低upscale倍数**：
```bash
python svd_pure_python.py --input image.png --upscale 2
```

3. **减少采样步数**：
```bash
python svd_pure_python.py --input image.png --steps 15
```

### 加速生成

1. **使用较少步数**：
```bash
--steps 20  # 而不是 30
```

2. **跳过upscale**：
```bash
--no-upscale
```

---

## 🐛 故障排除

### 问题1：CUDA out of memory

**解决方案：**
```bash
# 方案1：跳过upscale
python svd_pure_python.py --input image.png --no-upscale

# 方案2：使用CPU（慢）
CUDA_VISIBLE_DEVICES="" python svd_pure_python.py --input image.png
```

### 问题2：模型下载慢

**解决方案：**
```bash
# 使用镜像源
export HF_ENDPOINT=https://hf-mirror.com
python svd_pure_python.py --input image.png
```

### 问题3：角色仍然不稳定

**解决方案：**
```bash
# 使用最保守的参数
python svd_pure_python.py \
  --input image.png \
  --motion 30 \      # 极低运动
  --guidance 5.0 \   # 极高引导
  --steps 40         # 极高质量
```

---

## 📊 输出质量预期

| 配置 | 稳定性 | 画质 | 流畅度 | 生成时间 |
|------|--------|------|--------|---------|
| 默认 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 2-5分钟 |
| 高稳定 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 3-6分钟 |
| 快速模式 | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 1-3分钟 |

---

## 🎬 完整示例

### 从准备到生成

```bash
# 1. 安装依赖
./setup_pure_python.sh

# 2. 准备图片
mkdir -p input_images output_videos
cp your_character.png input_images/

# 3. 测试生成（高稳定性）
python svd_pure_python.py \
  --input input_images/your_character.png \
  --output output_videos/test.mp4 \
  --motion 50 \
  --guidance 4.0 \
  --steps 30

# 4. 查看结果
# 输出在 output_videos/test.mp4
# 规格：1024×576, 300帧, 60fps, 5秒
```

---

## ✨ 总结

### 推荐命令（一般使用）

```bash
python svd_pure_python.py --input image.png --output video.mp4
```

### 推荐命令（最高稳定性）

```bash
python svd_pure_python.py \
  --input image.png \
  --output video.mp4 \
  --motion 50 \
  --guidance 4.0 \
  --steps 30
```

### 快速测试命令

```bash
python svd_pure_python.py \
  --input image.png \
  --output test.mp4 \
  --steps 20 \
  --no-upscale
```

---

**享受纯Python的SVD视频生成！** 🎉
