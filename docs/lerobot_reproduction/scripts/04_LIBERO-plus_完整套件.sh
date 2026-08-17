#!/usr/bin/env bash
set -euo pipefail

# LIBERO-plus 冒烟成功之后才运行。

ENV_DIR="${ENV_DIR:-.venv-libero-plus}"
POLICY_PATH="${POLICY_PATH:-lerobot/smolvla_libero}"
N_EPISODES="${N_EPISODES:-10}"
SEED="${SEED:-1000}"
export MUJOCO_GL="${MUJOCO_GL:-egl}"

OUTPUT_DIR="outputs/reproduction/libero_plus/full/$(echo "$POLICY_PATH" | tr '/' '_')"
mkdir -p "$OUTPUT_DIR"

UV_PROJECT_ENVIRONMENT="$ENV_DIR" uv run --no-sync lerobot-eval \
  --output_dir="$OUTPUT_DIR" \
  --policy.path="$POLICY_PATH" \
  --env.type=libero_plus \
  --env.task=libero_spatial,libero_object,libero_goal,libero_10 \
  --env.control_mode=relative \
  --env.init_states=true \
  --env.hard_reset=true \
  --env.max_parallel_tasks=1 \
  --eval.batch_size=1 \
  --eval.n_episodes="$N_EPISODES" \
  --seed="$SEED"
