# 04：LIBERO-plus 评测

LIBERO-plus 使用和 vanilla LIBERO 类似的任务名与 observation/action schema，但安装包不同、场景加入了视觉和初始状态等扰动。它不是另一个训练数据格式，而是一个仿真鲁棒性 benchmark。

## 第一步：确认 plus 环境

先完成 [01_环境准备.md](./01_环境准备.md) 中的 `.venv-libero-plus`、LIBERO-plus fork 和 assets 安装。然后执行：

```bash
export LIBERO_PLUS_ENV=.venv-libero-plus
UV_PROJECT_ENVIRONMENT="$LIBERO_PLUS_ENV" uv run --no-sync python -c \
  "import libero; print(libero.__file__)"
```

确认路径指向 `third_party/LIBERO-plus` 对应的包后再继续。

## 第二步：单 task、单 episode 冒烟

使用和 vanilla LIBERO 相同的模型：

```bash
export POLICY_PATH=lerobot/smolvla_libero
export ENV_DIR=.venv-libero-plus
export MUJOCO_GL=egl

bash docs/lerobot_reproduction/scripts/03_LIBERO-plus_冒烟.sh
```

如果 vanilla LIBERO 能运行而 plus 失败，优先检查：

1. 当前 Python 是否真的来自 `.venv-libero-plus`；
2. `assets.zip` 是否解压到正确位置；
3. `hf-libero` 是否已经从 plus 环境卸载；
4. `MUJOCO_GL` 和 MuJoCo 是否可用。

## 第三步：完整四 suite

冒烟成功后：

```bash
export POLICY_PATH=lerobot/smolvla_libero
bash docs/lerobot_reproduction/scripts/04_LIBERO-plus_完整套件.sh
```

第一轮先不要在 `lerobot/libero_plus` 上训练。建议先记录：

```text
LIBERO 标准成功率
LIBERO-plus 扰动成功率
性能下降 = LIBERO 成功率 - LIBERO-plus 成功率
```

这个差值可以作为之后做 processor、图像增强、action chunk 或 harness 改动的初始 baseline。
