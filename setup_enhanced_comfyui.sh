#!/bin/bash
# ComfyUI 增強版環境設置 - 包含 RIFE 和 Real-ESRGAN

set -e

echo "========================================="
echo "🎬 ComfyUI 增強版環境設置"
echo "包含: SVD + RIFE + Real-ESRGAN"
echo "========================================="

# 顏色定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

COMFYUI_DIR="/mnt/c/ai_tools/comfyui"

# 檢查 ComfyUI 目錄
if [ ! -d "$COMFYUI_DIR" ]; then
    echo -e "${RED}❌ ComfyUI 目錄不存在: $COMFYUI_DIR${NC}"
    exit 1
fi

cd "$COMFYUI_DIR"

echo ""
echo "1️⃣  安裝 PyTorch (CUDA 12.8)..."
pip install torch==2.7.1 torchvision==0.22.1 torchaudio==2.7.1 --index-url https://download.pytorch.org/whl/cu128

echo ""
echo "2️⃣  安裝 ComfyUI-Frame-Interpolation (RIFE)..."
cd custom_nodes

if [ -d "ComfyUI-Frame-Interpolation" ]; then
    echo -e "${YELLOW}⚠️  ComfyUI-Frame-Interpolation 已存在，跳過克隆${NC}"
    cd ComfyUI-Frame-Interpolation
    git pull
else
    git clone https://github.com/Fannovel16/ComfyUI-Frame-Interpolation
    cd ComfyUI-Frame-Interpolation
fi

pip install -r requirements.txt

# 下載 RIFE 模型
echo ""
echo "3️⃣  下載 RIFE 模型..."
mkdir -p ckpts
cd ckpts

if [ -f "rife47.pth" ]; then
    echo -e "${GREEN}✅ rife47.pth 已存在${NC}"
else
    echo "下載 RIFE 4.7 模型..."
    wget https://github.com/hzwer/Practical-RIFE/releases/download/v4.7/rife47.pth
    echo -e "${GREEN}✅ RIFE 模型下載完成${NC}"
fi

cd "$COMFYUI_DIR/custom_nodes"

echo ""
echo "4️⃣  安裝 ComfyUI-VideoHelperSuite..."
if [ -d "ComfyUI-VideoHelperSuite" ]; then
    echo -e "${YELLOW}⚠️  ComfyUI-VideoHelperSuite 已存在，跳過克隆${NC}"
    cd ComfyUI-VideoHelperSuite
    git pull
else
    git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite
    cd ComfyUI-VideoHelperSuite
fi

pip install -r requirements.txt

cd "$COMFYUI_DIR"

echo ""
echo "5️⃣  安裝 Real-ESRGAN..."
pip install realesrgan basicsr facexlib gfpgan

echo ""
echo "6️⃣  下載 Real-ESRGAN 模型..."
mkdir -p models/upscale_models
cd models/upscale_models

# RealESRGAN x4 anime (推薦 Pixar)
if [ -f "RealESRGAN_x4plus_anime_6B.pth" ]; then
    echo -e "${GREEN}✅ RealESRGAN_x4plus_anime_6B.pth 已存在${NC}"
else
    echo "下載 RealESRGAN x4 anime 模型..."
    wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-animevideov3.pth \
         -O RealESRGAN_x4plus_anime_6B.pth
    echo -e "${GREEN}✅ RealESRGAN x4 anime 模型下載完成${NC}"
fi

# RealESRGAN x2 通用
if [ -f "RealESRGAN_x2plus.pth" ]; then
    echo -e "${GREEN}✅ RealESRGAN_x2plus.pth 已存在${NC}"
else
    echo "下載 RealESRGAN x2 模型..."
    wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.1/RealESRGAN_x2plus.pth
    echo -e "${GREEN}✅ RealESRGAN x2 模型下載完成${NC}"
fi

# RealESRGAN x4 通用
if [ -f "RealESRGAN_x4plus.pth" ]; then
    echo -e "${GREEN}✅ RealESRGAN_x4plus.pth 已存在${NC}"
else
    echo "下載 RealESRGAN x4 模型..."
    wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth
    echo -e "${GREEN}✅ RealESRGAN x4 模型下載完成${NC}"
fi

cd "$COMFYUI_DIR"

echo ""
echo "7️⃣  檢查 SVD 模型..."
cd models/checkpoints

if [ -f "svd_xt_1_1.safetensors" ]; then
    echo -e "${GREEN}✅ SVD 模型已存在${NC}"
else
    echo -e "${YELLOW}⚠️  SVD 模型未找到${NC}"
    echo "請手動下載:"
    echo "  huggingface-cli download stabilityai/stable-video-diffusion-img2vid-xt-1-1 \\"
    echo "    svd_xt_1_1.safetensors --local-dir ."
fi

cd "$COMFYUI_DIR"

echo ""
echo "8️⃣  測試 PyTorch..."
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA version: {torch.version.cuda}')"

echo ""
echo "========================================="
echo -e "${GREEN}✅ 增強版環境設置完成！${NC}"
echo "========================================="
echo ""
echo "已安裝組件:"
echo "  ✅ PyTorch 2.7.1 (CUDA 12.8)"
echo "  ✅ ComfyUI-Frame-Interpolation (RIFE)"
echo "  ✅ ComfyUI-VideoHelperSuite"
echo "  ✅ Real-ESRGAN"
echo "  ✅ RIFE 4.7 模型"
echo "  ✅ Real-ESRGAN 模型 (x2, x4, x4 anime)"
echo ""
echo "下一步:"
echo "  1. 啟動 ComfyUI:"
echo "     cd $COMFYUI_DIR"
echo "     python main.py --port 8188"
echo ""
echo "  2. 測試增強版生成:"
echo "     cd /mnt/c/ai_projects/video-gen-factory"
echo "     python svd_enhanced_batch.py --quality high --characters miguel --max-videos 1 --wait"
echo ""
