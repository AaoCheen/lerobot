# 在 Hugging Face 上检查 LeRobot 数据集

目标是按成本从低到高检查：仓库标签 → `info.json` → Parquet schema/样本 → 视频 → 完整加载。

以下命令均从 `repos/lerobot` 根目录执行。将示例数据集替换为你关心的 `namespace/name`。

## 1. 浏览器中先看什么

数据集检索入口：<https://huggingface.co/datasets?other=LeRobot>

进入一个数据集后依次看：

1. Dataset card：来源、机器人、采集任务、许可证；
2. Files and versions：是否有 `meta/info.json`，目录是否符合 v3.0；
3. Dataset Viewer：Parquet 的列、类型和示例值；
4. `meta/info.json`：`codebase_version`、`fps`、`robot_type`、`features`；
5. 视频文件：相机命名和真实视角。

不要只看 Viewer 的表格外观。图像往往在 MP4 中，Viewer 展示的 Parquet 列并不代表最终 `dataset[i]` 中已解码图像 tensor 的形状。

## 2. 只下载元数据

```bash
DATASET_ID=lerobot/pusht

uv run python - <<'PY'
from pprint import pprint
from lerobot.datasets import LeRobotDatasetMetadata

repo_id = "lerobot/pusht"
meta = LeRobotDatasetMetadata(repo_id)
print(meta)
print("fps:", meta.fps)
print("episodes:", meta.total_episodes)
print("frames:", meta.total_frames)
print("camera_keys:", meta.camera_keys)
print("tasks:")
pprint(meta.tasks)
print("features:")
pprint(meta.features)
PY
```

这是最推荐的第一步：只获取轻量元数据，不必先下载所有视频。

## 3. 用 Hub / Dataset Viewer API 看文件与 Parquet

列出数据集仓库文件：

```bash
DATASET_ID=lerobot/pusht
curl -s "https://huggingface.co/api/datasets/${DATASET_ID}/tree/main?recursive=true&expand=false" \
  | jq -r '.[].path' | head -100
```

直接查看 `info.json`：

```bash
DATASET_ID=lerobot/pusht
curl -sL "https://huggingface.co/datasets/${DATASET_ID}/resolve/main/meta/info.json" | jq
```

Dataset Viewer API 对普通 Hub 数据集很有用：

```bash
DATASET_ID=lerobot/pusht
curl -s "https://datasets-server.huggingface.co/is-valid?dataset=${DATASET_ID}" | jq
curl -s "https://datasets-server.huggingface.co/splits?dataset=${DATASET_ID}" | jq
curl -s "https://datasets-server.huggingface.co/parquet?dataset=${DATASET_ID}" | jq
curl -s "https://datasets-server.huggingface.co/size?dataset=${DATASET_ID}" | jq
```

并非所有 LeRobot 仓库都会被 Dataset Viewer 完整索引；遇到 API 不支持时，回到 `meta/info.json`、仓库文件列表和 `LeRobotDatasetMetadata`，不应据此判定数据集损坏。

## 4. 下载少量 episode 并查看真实返回值

```bash
uv run python - <<'PY'
from pprint import pprint
from lerobot.datasets import LeRobotDataset

repo_id = "lerobot/pusht"
ds = LeRobotDataset(repo_id, episodes=[0])
sample = ds[0]

print(ds)
for key, value in sample.items():
    shape = tuple(value.shape) if hasattr(value, "shape") else None
    dtype = getattr(value, "dtype", type(value).__name__)
    print(f"{key:40s} shape={shape!s:20s} dtype={dtype}")

print("feature schema:")
pprint(ds.features)
PY
```

如果当前只研究低维字段，可先尝试 `download_videos=False`；但访问图像 key 时仍需要视频，因此不能用这种模式验证最终图像 tensor。

## 5. 对目标 VLA 做代码追踪

选定一个 policy 后运行：

```bash
POLICY=smolvla
rg -n "delta_timestamps|observation.images|observation.state|action|chunk_size|n_action_steps" \
  "src/lerobot/policies/${POLICY}" src/lerobot/processor
```

把结果填入本目录 `README.md` 的研究表。最重要的链路是：

```text
meta/info.json features
  → LeRobotDataset.__getitem__
  → delta_timestamps 构造时间窗口
  → processor 重命名/归一化/tokenize
  → policy forward 所需 batch keys
```

## 6. 建议的第一个小实验

先只完成以下四项，不急着训练：

1. 选一个公开、小型、v3.0 数据集；
2. 保存其元数据摘要和 `dataset[0]` 的 key/shape；
3. 选一个目标 policy，找出它的时间窗口与输入 key；
4. 写出一张“数据字段 → policy 输入”的映射表。

完成后再判断是直接训练、重命名字段，还是需要写 port/conversion 脚本。
