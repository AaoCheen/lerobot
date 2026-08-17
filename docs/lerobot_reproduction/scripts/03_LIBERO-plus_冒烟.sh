#!/usr/bin/env bash
set -euo pipefail

# LIBERO-plus 必须使用独立环境；不要在 vanilla LIBERO 环境中执行。
# 用法：POLICY_PATH=lerobot/smolvla_libero ENV_DIR=.venv-libero-plus \
#   bash docs/lerobot_reproduction/scripts/03_LIBERO-plus_冒烟.sh

ENV_DIR="${ENV_DIR:-.venv-libero-plus}"
POLICY_PATH="${POLICY_PATH:-lerobot/smolvla_libero}"
TASK_ID="${TASK_ID:-0}"
SEED="${SEED:-1000}"
export MUJOCO_GL="${MUJOCO_GL:-egl}"

OUTPUT_DIR="outputs/reproduction/libero_plus/smoke/$(echo "$POLICY_PATH" | tr '/' '_')"
mkdir -p "$OUTPUT_DIR"

UV_PROJECT_ENVIRONMENT="$ENV_DIR" uv run --no-sync lerobot-eval \
  --output_dir="$OUTPUT_DIR" \
  --policy.path="$POLICY_PATH" \
  --env.type=libero_plus \
  --env.task=libero_spatial \
  --env.task_ids="[$TASK_ID]" \
  --env.control_mode=relative \
  --env.init_states=true \
  --env.hard_reset=true \
  --env.max_parallel_tasks=1 \
  --eval.batch_size=1 \
  --eval.n_episodes=1 \
  --seed="$SEED"
