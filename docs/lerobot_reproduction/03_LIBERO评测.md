# 03：LIBERO 评测

## 第一步：单 task、单 episode 冒烟

先确保当前目录是仓库根目录，并且已经完成 [01_环境准备.md](./01_环境准备.md)。

默认使用小模型：

```bash
export POLICY_PATH=lerobot/smolvla_libero
export ENV_DIR=.venv-libero
export MUJOCO_GL=egl

bash docs/lerobot_reproduction/scripts/01_LIBERO_冒烟.sh
```

这个脚本只运行 `libero_spatial` 的 `task_id=0`、1 个 episode。成功的标准不是成功率高，而是：

- policy 能被加载；
- MuJoCo 能创建环境；
- observation key 能进入 processor；
- action 能返回环境；
- episode 能正常结束并写出日志。

## 第二步：换成 Pi05

冒烟流程正常后，只改模型路径：

```bash
export POLICY_PATH=lerobot/pi05_libero_finetuned_v044
bash docs/lerobot_reproduction/scripts/01_LIBERO_冒烟.sh
```

如果 Pi05 需要显式覆盖动作步数，可以直接手动执行：

```bash
UV_PROJECT_ENVIRONMENT=.venv-libero uv run --no-sync lerobot-eval \
  --output_dir=outputs/reproduction/libero/pi05_smoke \
  --policy.path=lerobot/pi05_libero_finetuned_v044 \
  --policy.n_action_steps=10 \
  --env.type=libero \
  --env.task=libero_spatial \
  --env.task_ids='[0]' \
  --env.control_mode=relative \
  --env.init_states=true \
  --env.hard_reset=true \
  --env.max_parallel_tasks=1 \
  --eval.batch_size=1 \
  --eval.n_episodes=1 \
  --seed=1000
```

## 第三步：完整四 suite

只有冒烟成功后，才执行：

```bash
export POLICY_PATH=lerobot/smolvla_libero
bash docs/lerobot_reproduction/scripts/02_LIBERO_完整套件.sh
```

完整脚本包含：

```text
libero_spatial, libero_object, libero_goal, libero_10
```

每个 task 运行 10 个 episode 时，四个 suite 合计 400 个 episode。初步调试阶段可以先把脚本中的 `N_EPISODES=10` 改为 `1`。

## 评测时不要先改这些东西

- 不要先调 action chunk；
- 不要先改 control mode；
- 不要先打开 soft reset；
- 不要先提高并行 batch；
- 不要把失败归因于模型，先看日志中的 key、依赖和渲染错误。
