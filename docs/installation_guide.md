# ComfyUI + AnimateDiff 完整安装指南

> 针对 Linux 系统（Ubuntu/Debian）+ NVIDIA GPU（RTX 5080, 16GB VRAM）

---

## 第一步：系统环境准备

### 1.1 检查系统要求

```bash
# 检查NVIDIA驱动
nvidia-smi

# 应该看到：
# - NVIDIA RTX 5080
# - CUDA Version: 12.x 或更高
# - Driver Version: 535.xx 或更高
```

**成功标准**: 能看到GPU信息和CUDA版本
**常见问题**: 如果看不到，需要先安装NVIDIA驱动：
```bash
sudo ubuntu-drivers autoinstall
sudo reboot
```

### 1.2 安装Python 3.10+

```bash
# 检查Python版本
python3 --version

# 如果版本低于3.10，安装Python 3.10
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip
```

### 1.3 安装必要系统依赖

```bash
sudo apt install -y \
    git \
    wget \
    libgl1-mesa-glx \
    libglib2.0-0 \
    ffmpeg \
    build-essential
```

---

## 第二步：安装 ComfyUI

### 2.1 克隆 ComfyUI 仓库

```bash
cd ~/
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
```

### 2.2 创建Python虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate

# 验证虚拟环境已激活（提示符前应有 (venv) 标识）
```

### 2.3 安装PyTorch（CUDA 12.x版本）

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**验证安装**:
```bash
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0)}')"
```

**成功标准**:
```
PyTorch: 2.x.x+cu121
CUDA available: True
GPU: NVIDIA GeForce RTX 5080
```

**常见错误**: 如果CUDA不可用，重新检查NVIDIA驱动版本

### 2.4 安装ComfyUI依赖

```bash
pip install -r requirements.txt
```

### 2.5 首次启动测试

```bash
python main.py --preview-method auto

# 成功标志：
# - 看到 "To see the GUI go to: http://127.0.0.1:8188"
# - 浏览器打开 http://127.0.0.1:8188 能看到ComfyUI界面
```

**常见问题**:
- 端口被占用：使用 `--port 8189` 更换端口
- 显存不足：添加 `--lowvram` 参数

按 `Ctrl+C` 停止服务

---

## 第三步：安装必要 Custom Nodes

### 3.1 安装 ComfyUI Manager（推荐）

```bash
cd ~/ComfyUI/custom_nodes
git clone https://github.com/ltdrdata/ComfyUI-Manager.git
```

重启ComfyUI，界面右侧会出现 "Manager" 按钮

### 3.2 安装 ComfyUI-AnimateDiff-Evolved

**方法1：通过Manager安装**（推荐）
1. 启动ComfyUI
2. 点击 "Manager" → "Install Custom Nodes"
3. 搜索 "AnimateDiff-Evolved"
4. 点击 Install

**方法2：手动安装**
```bash
cd ~/ComfyUI/custom_nodes
git clone https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved.git
cd ComfyUI-AnimateDiff-Evolved
pip install -r requirements.txt
```

### 3.3 安装 VideoHelperSuite

```bash
cd ~/ComfyUI/custom_nodes
git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git
cd ComfyUI-VideoHelperSuite
pip install -r requirements.txt
```

### 3.4 安装 ControlNet Auxiliary Preprocessors

```bash
cd ~/ComfyUI/custom_nodes
git clone https://github.com/Fannovel16/comfyui_controlnet_aux.git
cd comfyui_controlnet_aux
pip install -r requirements.txt
```

### 3.5 安装 IP-Adapter Plus

```bash
cd ~/ComfyUI/custom_nodes
git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus.git
```

### 3.6 安装 FreeU Advanced

```bash
cd ~/ComfyUI/custom_nodes
git clone https://github.com/WASasquatch/FreeU_Advanced.git
```

### 3.7 重启ComfyUI验证

```bash
cd ~/ComfyUI
source venv/bin/activate
python main.py
```

在界面中右键 → Add Node，应该能看到：
- AnimateDiff Evolved
- VideoHelperSuite
- ControlNet Preprocessors
- IPAdapter
- FreeU

**常见问题**:
- 看不到新节点：清除浏览器缓存（Ctrl+Shift+R）
- 节点报错：检查requirements.txt是否都安装成功

---

## 第四步：下载必要模型

### 4.1 创建模型目录结构

```bash
cd ~/ComfyUI
mkdir -p models/checkpoints
mkdir -p models/controlnet
mkdir -p models/animatediff_models
mkdir -p models/animatediff_motion_lora
mkdir -p models/ipadapter
mkdir -p models/clip_vision
mkdir -p models/upscale_models
```

### 4.2 下载 Base Stable Diffusion 模型

**选择1: DreamShaper 8**（推荐，适合皮克斯风格）
```bash
cd ~/ComfyUI/models/checkpoints
wget https://huggingface.co/Lykon/DreamShaper/resolve/main/DreamShaper_8_pruned.safetensors
```

**选择2: ToonYou Beta6**（更偏动画风格）
```bash
cd ~/ComfyUI/models/checkpoints
wget https://huggingface.co/Hosioka/ToonYou/resolve/main/ToonYou_beta6.safetensors
```

**文件大小**: 约 2-4GB
**下载时间**: 取决于网速，约10-30分钟

### 4.3 下载 AnimateDiff Motion Module

```bash
cd ~/ComfyUI/models/animatediff_models

# 下载 v2 版本（稳定）
wget https://huggingface.co/guoyww/animatediff/resolve/main/mm_sd_v15_v2.ckpt

# 下载 v3 版本（更流畅的运动）
wget https://huggingface.co/guoyww/animatediff/resolve/main/mm_sd_v15_v3.ckpt
```

**文件大小**: 每个约1.7GB

### 4.4 下载 ControlNet 模型

```bash
cd ~/ComfyUI/models/controlnet

# Depth ControlNet（必需）
wget https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/control_v11f1p_sd15_depth.pth

# Softedge/HED ControlNet（可选）
wget https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/control_v11p_sd15_softedge.pth
```

**文件大小**: 每个约1.4GB

### 4.5 下载 IP-Adapter 模型

```bash
cd ~/ComfyUI/models/ipadapter

# IP-Adapter-FaceID（角色面部一致性）
wget https://huggingface.co/h94/IP-Adapter-FaceID/resolve/main/ip-adapter-faceid_sd15.bin

# IP-Adapter Plus（整体造型一致性）
wget https://huggingface.co/h94/IP-Adapter/resolve/main/models/ip-adapter-plus_sd15.safetensors
```

### 4.6 下载 CLIP Vision 模型（IP-Adapter必需）

```bash
cd ~/ComfyUI/models/clip_vision

wget https://huggingface.co/h94/IP-Adapter/resolve/main/models/image_encoder/model.safetensors
mv model.safetensors CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors
```

### 4.7 下载 Upscale 模型（用于两阶段放大策略）

```bash
cd ~/ComfyUI/models/upscale_models

# Real-ESRGAN 4x
wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth
```

### 4.8 验证模型完整性

```bash
cd ~/ComfyUI

# 检查所有模型文件
find models/ -type f -name "*.safetensors" -o -name "*.ckpt" -o -name "*.pth" -o -name "*.bin" | sort
```

**应该看到**:
```
models/checkpoints/DreamShaper_8_pruned.safetensors
models/controlnet/control_v11f1p_sd15_depth.pth
models/controlnet/control_v11p_sd15_softedge.pth
models/animatediff_models/mm_sd_v15_v2.ckpt
models/animatediff_models/mm_sd_v15_v3.ckpt
models/ipadapter/ip-adapter-faceid_sd15.bin
models/ipadapter/ip-adapter-plus_sd15.safetensors
models/clip_vision/CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors
models/upscale_models/RealESRGAN_x4plus.pth
```

**总磁盘占用**: 约 10-15GB

---

## 第五步：配置优化（针对16GB VRAM）

### 5.1 创建启动脚本

```bash
cd ~/ComfyUI
nano start.sh
```

添加以下内容：
```bash
#!/bin/bash
source venv/bin/activate
python main.py \
    --highvram \
    --preview-method auto \
    --use-split-cross-attention \
    --disable-xformers
```

保存并赋予执行权限：
```bash
chmod +x start.sh
```

**启动参数说明**:
- `--highvram`: 16GB VRAM使用此选项
- `--use-split-cross-attention`: 降低峰值VRAM使用
- `--disable-xformers`: 避免某些GPU的兼容性问题

**VRAM不足时的替代方案**:
```bash
# 如果经常OOM，使用：
python main.py --normalvram

# 极端情况（<8GB VRAM）：
python main.py --lowvram --novram
```

### 5.2 环境变量优化

```bash
nano ~/.bashrc
```

添加：
```bash
# ComfyUI优化
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
export CUDA_VISIBLE_DEVICES=0
```

生效：
```bash
source ~/.bashrc
```

---

## 第六步：验证安装完成

### 6.1 启动ComfyUI

```bash
cd ~/ComfyUI
./start.sh
```

### 6.2 加载测试Workflow

1. 打开 http://127.0.0.1:8188
2. 右键空白处 → "Add Node" → "loaders" → "Load Checkpoint"
3. 选择 DreamShaper_8_pruned
4. 验证模型能正确加载（无报错）

### 6.3 测试AnimateDiff节点

1. Add Node → AnimateDiff Evolved → Load AnimateDiff Model
2. 选择 mm_sd_v15_v2.ckpt
3. 验证motion module能加载

### 6.4 测试ControlNet节点

1. Add Node → ControlNet → Load ControlNet Model
2. 选择 control_v11f1p_sd15_depth.pth
3. 验证ControlNet能加载

### 6.5 测试IP-Adapter节点

1. Add Node → ipadapter → IPAdapterModelLoader
2. 选择 ip-adapter-plus_sd15.safetensors
3. 验证IP-Adapter能加载

**成功标准**: 所有节点都能正常加载，无红色报错

---

## 常见错误排除

### 错误1: "CUDA out of memory"

**原因**: VRAM不足

**解决方案**:
1. 降低分辨率（1280→1024→768→512）
2. 减少Context Length（24→16→12）
3. 启用VAE Tiling
4. 使用 `--lowvram` 启动参数
5. 关闭其他占用GPU的程序

### 错误2: "No module named 'xxx'"

**原因**: Python依赖未安装

**解决方案**:
```bash
source ~/ComfyUI/venv/bin/activate
pip install xxx
```

### 错误3: "Failed to load model"

**原因**: 模型文件损坏或路径错误

**解决方案**:
```bash
# 检查文件大小
ls -lh ~/ComfyUI/models/checkpoints/

# 重新下载损坏的模型
cd ~/ComfyUI/models/checkpoints
rm DreamShaper_8_pruned.safetensors
wget https://huggingface.co/Lykon/DreamShaper/resolve/main/DreamShaper_8_pruned.safetensors
```

### 错误4: "AnimateDiff node not found"

**原因**: custom node未正确安装

**解决方案**:
```bash
cd ~/ComfyUI/custom_nodes/ComfyUI-AnimateDiff-Evolved
git pull
pip install -r requirements.txt
# 重启ComfyUI
```

### 错误5: 视频导出失败 "ffmpeg not found"

**原因**: ffmpeg未安装

**解决方案**:
```bash
sudo apt install ffmpeg
ffmpeg -version  # 验证安装
```

### 错误6: IP-Adapter报错 "CLIP model not found"

**原因**: CLIP Vision模型缺失或路径错误

**解决方案**:
```bash
cd ~/ComfyUI/models/clip_vision
ls -lh  # 应该看到 CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors
# 如果没有，重新下载（见4.6步骤）
```

---

## 性能基准测试

在RTX 5080 (16GB VRAM) + ComfyUI + AnimateDiff环境下的预期性能：

| 分辨率 | Context | Batch | Steps | 预计VRAM | 生成速度（3秒/72帧） |
|--------|---------|-------|-------|----------|---------------------|
| 512x288 | 24 | 4 | 20 | 6-7GB | 2-3分钟 |
| 768x432 | 16 | 2 | 25 | 10-11GB | 4-6分钟 |
| 1024x576 | 16 | 1 | 26 | 13-14GB | 6-10分钟 |
| 1280x720 | 12 | 1 | 25 | 15-15.8GB | 12-18分钟 |

**注**: 实际速度受模型、ControlNet数量、IP-Adapter使用等影响

---

## 下一步

安装完成后，请参考：
- **README.md** - 完整使用教学和工作流搭建
- **config/style_presets.yaml** - S1/S2/S3风格参数
- **scripts/batch_processor.py** - 批次处理脚本

开始你的第一个测试：
1. 准备一组3D动画逐帧图片（frame_0001.png - frame_0072.png）
2. 从512x288分辨率的MVP开始
3. 使用S1保守风格参数
4. 逐步升级到最终1280x720输出

**祝你成功！**
