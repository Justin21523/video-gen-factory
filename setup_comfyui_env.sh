#!/bin/bash
# ComfyUI 專用環境設置腳本

set -e  # 遇到錯誤立即退出

echo "========================================="
echo "🔧 ComfyUI 專用環境設置"
echo "========================================="

# 檢查 conda 是否安裝
if ! command -v conda &> /dev/null; then
    echo "❌ 未找到 conda，請先安裝 Miniconda 或 Anaconda"
    exit 1
fi

# 環境名稱
ENV_NAME="comfyui"

# 檢查環境是否已存在
if conda env list | grep -q "^${ENV_NAME} "; then
    echo "⚠️  環境 '${ENV_NAME}' 已存在"
    read -p "是否刪除並重新創建？(y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "刪除舊環境..."
        conda env remove -n ${ENV_NAME} -y
    else
        echo "取消安裝"
        exit 0
    fi
fi

# 創建新環境
echo ""
echo "1️⃣  創建 Python 3.10 環境..."
conda create -n ${ENV_NAME} python=3.10 -y

# 激活環境
echo ""
echo "2️⃣  激活環境..."
source ~/miniconda3/etc/profile.d/conda.sh
conda activate ${ENV_NAME}

# 安裝 PyTorch（保持穩定版本）
echo ""
echo "3️⃣  安裝 PyTorch (CUDA 11.8)..."
pip install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cu118

# 安裝 ComfyUI 依賴
echo ""
echo "4️⃣  安裝 ComfyUI 依賴..."
cd /mnt/c/ai_tools/comfyui

if [ -f requirements.txt ]; then
    pip install -r requirements.txt
else
    echo "⚠️  未找到 requirements.txt"
fi

# 安裝額外依賴
echo ""
echo "5️⃣  安裝額外依賴..."
pip install "transformers>=4.41.0,<5.0.0"
pip install "huggingface-hub>=0.16.4,<1.0"
pip install "numpy>=1.26.0,<2.0.0"
pip install requests pyyaml

# 安裝批量生成腳本依賴
echo ""
echo "6️⃣  安裝批量生成腳本依賴..."
pip install pillow tqdm

# 測試 PyTorch
echo ""
echo "7️⃣  測試 PyTorch..."
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA version: {torch.version.cuda}')"

echo ""
echo "========================================="
echo "✅ 環境設置完成！"
echo "========================================="
echo ""
echo "使用方法:"
echo "  conda activate ${ENV_NAME}"
echo "  cd /mnt/c/ai_tools/comfyui"
echo "  python main.py --port 8188"
echo ""
echo "測試設置:"
echo "  conda activate ${ENV_NAME}"
echo "  cd /mnt/c/ai_projects/video-gen-factory"
echo "  python test_svd_setup.py"
echo ""
