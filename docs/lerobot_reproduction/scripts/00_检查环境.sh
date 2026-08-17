#!/usr/bin/env bash
set -euo pipefail

# 这个脚本只检查环境，不下载模型，不创建 MuJoCo episode。
# 运行位置应是 lerobot 仓库根目录。

ENV_DIR="${ENV_DIR:-.venv-libero}"

echo "== Git =="
git branch --show-current
git status --short --branch

echo
echo "== Tools =="
command -v uv || true
uv --version || true
command -v nvidia-smi || true
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv || true

echo
echo "== Python environment =="
if [[ -x "$ENV_DIR/bin/python" ]]; then
  "$ENV_DIR/bin/python" --version
  "$ENV_DIR/bin/python" -c "import torch; print('torch=', torch.__version__); print('cuda=', torch.cuda.is_available())"
else
  echo "找不到 $ENV_DIR/bin/python；先阅读并执行 01_环境准备.md。"
  exit 1
fi

echo
echo "MUJOCO_GL=${MUJOCO_GL:-未设置，服务器上通常应为 egl}"
