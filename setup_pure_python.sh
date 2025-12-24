#!/bin/bash
# 纯Python SVD系统安装脚本

echo "================================"
echo "🔧 安装纯Python SVD系统依赖"
echo "================================"

# 安装核心依赖
echo ""
echo "1️⃣ 安装diffusers和transformers..."
pip install --upgrade diffusers transformers accelerate

# 安装图像处理库
echo ""
echo "2️⃣ 安装图像处理库..."
pip install opencv-python-headless pillow numpy

# 安装PyTorch（如果还没有）
echo ""
echo "3️⃣ 检查PyTorch..."
python -c "import torch; print(f'PyTorch版本: {torch.__version__}')" 2>/dev/null || {
    echo "需要安装PyTorch，请访问: https://pytorch.org/get-started/locally/"
    echo "推荐命令（CUDA 11.8）:"
    echo "pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118"
}

# 验证安装
echo ""
echo "4️⃣ 验证安装..."
python3 << 'EOF'
import sys

def check_package(name, import_name=None):
    if import_name is None:
        import_name = name
    try:
        module = __import__(import_name)
        version = getattr(module, '__version__', 'unknown')
        print(f"✓ {name}: {version}")
        return True
    except ImportError:
        print(f"✗ {name}: 未安装")
        return False

print("\n依赖检查:")
all_ok = True
all_ok &= check_package('torch')
all_ok &= check_package('diffusers')
all_ok &= check_package('transformers')
all_ok &= check_package('opencv-python', 'cv2')
all_ok &= check_package('PIL', 'PIL')
all_ok &= check_package('numpy')

if all_ok:
    print("\n✅ 所有依赖已安装！")
else:
    print("\n❌ 部分依赖缺失，请检查")
    sys.exit(1)
EOF

echo ""
echo "================================"
echo "✅ 安装完成！"
echo "================================"
echo ""
echo "使用方法:"
echo "  python svd_pure_python.py --input your_image.png --output video.mp4"
echo ""
echo "更多选项:"
echo "  --motion 80        # 运动强度 (50=稳定, 150=运动大)"
echo "  --guidance 3.5     # 引导强度 (越高越贴近输入)"
echo "  --steps 25         # 采样步数"
echo "  --upscale 4        # 临时放大倍数"
echo ""
