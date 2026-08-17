#!/usr/bin/env bash
set -euo pipefail

# 第一个可执行实验：一个 suite 中的一个 task，只跑一个 episode。
# 用法：POLICY_PATH=lerobot/smolvla_libero bash docs/lerobot_reproduction/scripts/01_LIBERO_冒烟.sh

ENV_DIR="${ENV_DIR:-.venv-libero}"
POLICY_PATH="${POLICY_PATH:-lerobot/smolvla_libero}"
TASK_ID="${TASK_ID:-0}"
SEED="${SEED:-1000}"
export MUJOCO_GL="${MUJOCO_GL:-egl}"

OUTPUT_DIR="outputs/reproduction/libero/smoke/$(echo "$POLICY_PATH" | tr '/' '_')"
mkdir -p "$OUTPUT_DIR"

echo "policy=$POLICY_PATH"
echo "env=$ENV_DIR"
echo "output=$OUTPUT_DIR"

UV_PROJECT_ENVIRONMENT="$ENV_DIR" uv run --no-sync lerobot-eval \
  --output_dir="$OUTPUT_DIR" \
  --policy.path="$POLICY_PATH" \
  --env.type=libero \
  --env.task=libero_spatial \
  --env.task_ids="[$TASK_ID]" \
  --env.control_mode=relative \
  --env.init_states=true \
  --env.hard_reset=true \
  --env.max_parallel_tasks=1 \
  --eval.batch_size=1 \
  --eval.n_episodes=1 \
  --seed="$SEED"
