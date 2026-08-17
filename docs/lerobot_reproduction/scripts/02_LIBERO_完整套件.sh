#!/usr/bin/env bash
set -euo pipefail

# 冒烟成功之后才运行这个脚本。
# 默认每个 task 10 个 episode，四个 suite 合计约 400 个 episode。

ENV_DIR="${ENV_DIR:-.venv-libero}"
POLICY_PATH="${POLICY_PATH:-lerobot/smolvla_libero}"
N_EPISODES="${N_EPISODES:-10}"
SEED="${SEED:-1000}"
export MUJOCO_GL="${MUJOCO_GL:-egl}"

OUTPUT_DIR="outputs/reproduction/libero/full/$(echo "$POLICY_PATH" | tr '/' '_')"
mkdir -p "$OUTPUT_DIR"

UV_PROJECT_ENVIRONMENT="$ENV_DIR" uv run --no-sync lerobot-eval \
  --output_dir="$OUTPUT_DIR" \
  --policy.path="$POLICY_PATH" \
  --env.type=libero \
  --env.task=libero_spatial,libero_object,libero_goal,libero_10 \
  --env.control_mode=relative \
  --env.init_states=true \
  --env.hard_reset=true \
  --env.max_parallel_tasks=1 \
  --eval.batch_size=1 \
  --eval.n_episodes="$N_EPISODES" \
  --seed="$SEED"
