# Pixar 风格 + IP-Adapter + AnimateDiff 工作流构建指南

## 环境信息
- **GPU**: RTX 5080 16GB (可用 ~12.7GB)
- **目标输出**: 1024x576 @ 30fps, 3-6秒
- **角色**: Miguel (905张参考图片)
- **风格**: Pixar 3D 人物风格

## ComfyUI 访问地址
打开浏览器访问：http://localhost:8188

---

## 工作流架构

### 方案选择
由于您的 PixarXL 模型是 218MB，这是一个 **LoRA 文件**，我们将使用：
- **基础模型**: SD 1.5 (v1-5-pruned-emaonly.safetensors)
- **LoRA**: PixarXL.safetensors
- **Motion Module**: mm_sd_v15_v2.ckpt
- **IP-Adapter**: ip-adapter-plus_sd15.safetensors

### VRAM 预估
- 基础推理: ~6-7GB
- IP-Adapter: +4GB
- AnimateDiff (16帧): +2-3GB
- **总计**: ~12-14GB (✓ 您的 16GB 足够)

---

## 第一步：基础节点搭建

### 1. 加载 Checkpoint
节点：`Load Checkpoint`
- **ckpt_name**: `v1-5-pruned-emaonly.safetensors`

### 2. 加载 LoRA（Pixar 风格）
节点：`Load LoRA`
- 连接：
  - model ← Load Checkpoint 的 MODEL
  - clip ← Load Checkpoint 的 CLIP
- **lora_name**: `PixarXL.safetensors`
- **strength_model**: 0.8-1.0
- **strength_clip**: 0.8-1.0

### 3. 正向提示词 (Positive Prompt)
节点：`CLIP Text Encode (Prompt)`
- 连接：clip ← Load LoRA 的 CLIP
- **text**:
```
pixar style, 3d character, miguel from coco movie, high quality,
detailed facial features, expressive eyes, vibrant colors,
professional lighting, cinematic composition
```

### 4. 负向提示词 (Negative Prompt)
节点：`CLIP Text Encode (Prompt)`
- 连接：clip ← Load LoRA 的 CLIP
- **text**:
```
low quality, blurry, distorted, deformed, bad anatomy,
ugly, pixelated, compression artifacts, watermark
```

---

## 第二步：IP-Adapter 集成（角色一致性）

### 5. 加载 IP-Adapter 模型
节点：`IPAdapter Unified Loader` (来自 IPAdapter Plus)
- **ipadapter_file**: `ip-adapter-plus_sd15.safetensors`

### 6. 准备参考图片
节点：`Load Image`
- **image**: 从您的 Miguel 参考图片中选择 3-5 张最具代表性的：
  - 正脸特写
  - 侧脸
  - 不同表情

**重要提示**：如果需要使用多张参考图，可以使用 `IPAdapter Batch` 节点。

### 7. 应用 IP-Adapter
节点：`IPAdapter Apply`
- 连接：
  - model ← Load LoRA 的 MODEL
  - ipadapter ← IPAdapter Unified Loader
  - image ← Load Image
- **weight**: 0.7-0.9 (控制角色一致性强度)
- **weight_type**: `original`

---

## 第三步：AnimateDiff 动态生成

### 8. 加载 AnimateDiff Motion Module
节点：`ADE_AnimateDiffLoaderGen1`
- **model_name**: `mm_sd_v15_v2.ckpt`

### 9. 加载输入图像序列
节点：`VHS_LoadImagesPath` (来自 VideoHelperSuite)
- **directory**: `/mnt/c/ai_projects/video-gen-factory/input_sequences/scene_01_test`
- **image_load_cap**: 48 (对应 30fps 下约 1.6 秒，可以根据需要调整)
- **skip_first_images**: 0
- **select_every_nth**: 1 (如果源是 60fps 想降到 30fps，设为 2)

**重要**：您需要先准备测试图像序列！命名格式：
```
frame_0001.png
frame_0002.png
frame_0003.png
...
frame_0048.png
```

### 10. AnimateDiff 采样器
节点：`ADE_AnimateDiffSampler`
- 连接：
  - model ← IPAdapter Apply 的 MODEL
  - m_models ← ADE_AnimateDiffLoaderGen1
  - positive ← CLIP Text Encode (Positive)
  - negative ← CLIP Text Encode (Negative)
  - latent_image ← (需要将图像转换为 latent，见下一步)
- **steps**: 20-25
- **cfg**: 7.0-8.0
- **sampler_name**: `euler_ancestral`
- **scheduler**: `normal`
- **denoise**: 0.55 (关键参数！控制风格化强度)
  - 0.35-0.45: 保守（S1）
  - 0.55-0.65: 中等（S2）推荐
  - 0.70-0.80: 强烈（S3）

### 11. 图像转 Latent
需要在步骤 9 和步骤 10 之间插入：
节点：`VAE Encode (for Inpainting)`
- 连接：
  - pixels ← VHS_LoadImagesPath 的 IMAGE
  - vae ← Load Checkpoint 的 VAE

---

## 第四步：后处理和输出

### 12. VAE 解码
节点：`VAE Decode`
- 连接：
  - samples ← ADE_AnimateDiffSampler 的 LATENT
  - vae ← Load Checkpoint 的 VAE

### 13. 调整分辨率（如果需要）
节点：`Image Scale`
- 连接：image ← VAE Decode
- **width**: 1024
- **height**: 576
- **upscale_method**: `lanczos`

### 14. 保存视频
节点：`VHS_VideoCombine` (来自 VideoHelperSuite)
- 连接：images ← Image Scale (或 VAE Decode)
- **frame_rate**: 30
- **format**: `video/h264-mp4`
- **save_output**: true
- **filename_prefix**: `miguel_pixar_test`

---

## 关键参数调优表

| 参数 | 推荐值（MVP） | 用途 |
|------|--------------|------|
| **Denoise** | 0.55-0.65 | 控制风格化强度，越高越偏离原始动画 |
| **IP-Adapter Weight** | 0.7-0.9 | 角色一致性强度 |
| **CFG Scale** | 7.0-8.0 | 提示词遵循度 |
| **Steps** | 20-25 | 推理步数，越高质量越好但越慢 |
| **Context Length** | 16 | AnimateDiff 一次处理的帧数 |
| **LoRA Strength** | 0.8-1.0 | Pixar 风格强度 |

---

## MVP 测试计划

### 阶段 1：最小测试（512x288, 16帧, 约1秒）
1. 准备 16 张测试图片
2. 设置分辨率为 512x288
3. Denoise = 0.55
4. 验证整个流程可以运行

### 阶段 2：短片段测试（512x288, 48帧, 约1.6秒）
1. 48 张图片
2. 检查帧间一致性
3. 调整 IP-Adapter weight

### 阶段 3：目标分辨率测试（1024x576, 48帧）
1. 升级到目标分辨率
2. 监控 VRAM 使用
3. 如果 VRAM 不足，考虑分段处理

### 阶段 4：完整时长（1024x576, 90-180帧, 3-6秒）
1. 使用 Context 分段策略
2. 批量处理

---

## 常见问题排查

### 1. VRAM 不足（OOM）
**解决方案**：
- 降低分辨率到 768x432
- 减少每批帧数（Context Length: 16 → 12）
- 关闭不必要的节点预览

### 2. 角色面部不一致
**解决方案**：
- 提高 IP-Adapter weight (0.7 → 0.85)
- 使用更多参考图片（3-5 张不同角度）
- 在 prompt 中添加详细的面部特征描述

### 3. 画面闪烁
**解决方案**：
- 降低 Denoise (0.65 → 0.55)
- 使用 `uniform` scheduler
- 启用 AnimateDiff 的 anti-flicker 选项（如果有）

### 4. 风格不够强烈
**解决方案**：
- 提高 Denoise (0.55 → 0.65)
- 增强 LoRA strength (0.8 → 1.0)
- 优化 Prompt（添加更多 Pixar 风格关键词）

---

## 保存工作流
构建完成后，请：
1. 点击 ComfyUI 右上角的 Save 按钮
2. 保存为 `/mnt/c/ai_projects/video-gen-factory/workflows/pixar_ipadapter_workflow.json`
3. 之后可以直接加载使用

---

## 下一步
完成工作流构建后，我们将：
1. 准备测试图像序列
2. 运行 MVP 测试
3. 根据结果调优参数
4. 批量处理完整场景
