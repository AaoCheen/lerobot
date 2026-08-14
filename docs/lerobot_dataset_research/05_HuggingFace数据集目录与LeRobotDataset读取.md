# Hugging Face 上 `lerobot/libero_plus` 的目录结构与读取形状

数据集主页：<https://huggingface.co/datasets/lerobot/libero_plus>

这篇笔记回答两个问题：

1. Hugging Face 仓库里的 `data/`、`meta/`、`videos/` 分别保存什么；
2. 使用 `LeRobotDataset` 时，`dataset[i]` 实际取到什么、shape 是什么。

## 一、先看完整结构

`lerobot/libero_plus` 是 LeRobotDataset v3.0 格式，主要目录可以简化为：

```text
lerobot/libero_plus/
├── data/
│   └── chunk-000/
│       ├── file-000.parquet
│       ├── file-001.parquet
│       └── ...
│
├── meta/
│   ├── info.json
│   ├── stats.json
│   ├── tasks.parquet
│   └── episodes/
│       └── chunk-000/
│           └── file-000.parquet
│
├── videos/
│   ├── observation.images.front/
│   │   └── chunk-000/
│   │       ├── file-000.mp4
│   │       ├── file-001.mp4
│   │       └── ...
│   └── observation.images.wrist/
│       └── chunk-000/
│           ├── file-000.mp4
│           ├── file-001.mp4
│           └── ...
│
└── README.md
```

Hub 页面入口：

- [`data/`](https://huggingface.co/datasets/lerobot/libero_plus/tree/main/data)
- [`meta/`](https://huggingface.co/datasets/lerobot/libero_plus/tree/main/meta)
- [`videos/`](https://huggingface.co/datasets/lerobot/libero_plus/tree/main/videos)

重要概念：v3.0 是 **file-based**，一个 Parquet 或 MP4 文件通常包含很多 episode。不要把 `file-000.parquet` 理解成“episode 0”，也不要把 `file-000.mp4` 理解成“一条演示视频”。LeRobot 会利用元数据找出某个 episode 在共享文件中的位置。

## 二、`data/`：每个控制时刻的表格数据

`data/` 中是 Parquet 文件，主要保存适合用表格表达的逐 frame 数据，例如：

```text
observation.state
action
timestamp
frame_index
episode_index
index
task_index
```

可以把 Parquet 中的一行理解为一个控制时刻：

```text
第 i 行
├── 当前机器人状态 observation.state: 8个数
├── 当前时刻对应的专家 action: 7个数
├── 当前时间 timestamp
├── 当前 episode 内的 frame_index
├── 属于哪条轨迹 episode_index
├── 全数据集索引 index
└── 属于哪种语言任务 task_index
```

两张 RGB 图片本身不在这些 Parquet 行中，而是保存在 `videos/` 的 MP4 文件中。Parquet 中的时间、episode 和索引信息帮助 LeRobot 找到应该解码哪一帧视频。

### 为什么拆成 Parquet

因为 state、action 和各种索引是低维数值，用 Parquet 存储和筛选很高效；图片则更适合压缩成 MP4。这样不用把每一张 256×256 RGB 图片作为独立文件保存。

## 三、`videos/`：两路相机的连续图像

数据集有两个视频 feature：

```text
observation.images.front
observation.images.wrist
```

- `front`：场景前视/第三人称相机；
- `wrist`：机械臂腕部相机。

每路相机单独建立目录，里面是多个 MP4 shard。当前元数据给出的编码信息为：

```text
分辨率: 256 × 256
通道:   3（RGB）
FPS:    20
codec:  AV1
```

`front/file-000.mp4` 和 `wrist/file-000.mp4` 是两路不同视角，不是前后两段时间。LeRobot 根据当前 frame 的 timestamp，从相应 MP4 中解码同一时刻的两张图。

## 四、`meta/`：把 data、video、task 和 episode 连接起来

### `meta/info.json`

这是理解数据集的第一入口，记录：

- `codebase_version`: 当前为 `v3.0`；
- `robot_type`: `panda`；
- `fps`: `20`；
- `total_episodes`: `14,347`；
- `total_frames`: `2,238,036`；
- `total_tasks`: `40`；
- 每个 feature 的 dtype 和 shape；
- data/video 文件的路径模板。

当前路径模板是：

```text
data/chunk-{chunk_index:03d}/file-{file_index:03d}.parquet
videos/{video_key}/chunk-{chunk_index:03d}/file-{file_index:03d}.mp4
```

### `meta/tasks.parquet`

保存 `task_index` 与自然语言任务之间的映射。

逻辑上类似：

```text
task_index = 0 → “完成任务A的自然语言指令”
task_index = 1 → “完成任务B的自然语言指令”
...
```

data 中每个 frame 只需保存一个整数 `task_index`。`LeRobotDataset` 读取时会查这个表，并在返回字典中添加：

```python
sample["task"]  # Python str，自然语言指令
```

### `meta/episodes/`

保存每个 episode 的长度、任务、数据文件位置、视频起止位置/时间等信息。它告诉读取器：

```text
episode 123 从哪一行开始、到哪一行结束；
它的数据在哪个 Parquet shard；
两路视频在哪些 MP4 shard；
在视频中从什么时间开始解码。
```

这就是 v3.0 能把很多 episode 合并进少量大文件、同时仍然按 episode 访问的原因。

### `meta/stats.json`

保存 state、action 等 feature 的均值、标准差、最小值、最大值或分位数等统计量，主要用于模型训练时的 normalization / unnormalization。

这些统计量不是一条新训练样本，也不是机器人状态；它们是整个数据集的汇总信息。

## 五、应该使用 `LeRobotDataset` 吗

是。推荐让 `LeRobotDataset` 完成以下工作：

- 从 Hub 下载并缓存文件；
- 读取 Parquet；
- 根据 episode 元数据定位数据；
- 按 timestamp 解码两路视频；
- 把图像转成 PyTorch tensor；
- 把 `task_index` 还原成自然语言 `task`；
- 构造历史 observation 和未来 action window；
- 防止时间窗口越过 episode 边界。

基本用法：

```python
from lerobot.datasets import LeRobotDataset

dataset = LeRobotDataset(
    repo_id="lerobot/libero_plus",
    video_backend="torchcodec",  # 也可按环境使用 pyav
)

print("frames:", len(dataset))
sample = dataset[0]
```

`len(dataset)` 等于所选 episodes 中的 frame 总数。未筛选时是 `2,238,036`，所以 `dataset[0]` 取的是第一个 frame，不是第一个完整 episode。

如果只想先看一个 episode：

```python
dataset = LeRobotDataset(
    repo_id="lerobot/libero_plus",
    episodes=[0],
    video_backend="torchcodec",
)
```

这会限制到 episode 0，但 `dataset[i]` 仍然一次返回其中的一个 frame。

## 六、默认 `dataset[i]` 返回什么形状

不设置 `delta_timestamps` 时，单条样本大致是：

```python
sample = dataset[i]

{
    "observation.images.front": Tensor[3, 256, 256],
    "observation.images.wrist": Tensor[3, 256, 256],
    "observation.state": Tensor[8],
    "action": Tensor[7],
    "timestamp": Tensor[],
    "frame_index": Tensor[],
    "episode_index": Tensor[],
    "index": Tensor[],
    "task_index": Tensor[],
    "task": str,
}
```

这里的 `Tensor[]` 表示标量 tensor。

### 为什么 Hub 显示 `[256, 256, 3]`，读取后却是 `[3, 256, 256]`

两者描述的是不同层次：

```text
meta/info.json 存储逻辑: [H, W, C] = [256, 256, 3]
PyTorch 读取结果:       [C, H, W] = [3, 256, 256]
```

这不是数据错误，只是 PyTorch 通常采用 channel-first。

默认图像通常是 `float32`，数值在 `[0, 1]`。如果创建数据集时设置 `return_uint8=True`，则会返回 `uint8`、范围 `[0, 255]`。因此调试时应实际打印 dtype，不要只假定。

## 七、一次取多张历史图片和未来动作

VLA 训练经常需要 observation history 和 action chunk。可以用相对当前时刻的 `delta_timestamps`：

```python
fps = 20

delta_timestamps = {
    # 当前时刻及之前3个控制时刻，共4帧
    "observation.images.front": [-3 / fps, -2 / fps, -1 / fps, 0],
    "observation.images.wrist": [-3 / fps, -2 / fps, -1 / fps, 0],
    "observation.state": [-3 / fps, -2 / fps, -1 / fps, 0],

    # 当前动作及未来15个动作，共16步
    "action": [i / fps for i in range(16)],
}

dataset = LeRobotDataset(
    repo_id="lerobot/libero_plus",
    delta_timestamps=delta_timestamps,
    video_backend="torchcodec",
)

sample = dataset[100]
```

此时主要 shape 变为：

```text
observation.images.front: [4, 3, 256, 256]
observation.images.wrist: [4, 3, 256, 256]
observation.state:        [4, 8]
action:                   [16, 7]
```

这里：

- 第一维 `4` 是 observation 时间长度；
- 第一维 `16` 是 action chunk 长度；
- 每个 action 仍然是 7 维。

窗口接近 episode 开头或结尾时，LeRobot 会处理越界并提供相应 padding 信息，避免读到相邻 episode。

## 八、DataLoader 加上 batch 后的形状

```python
from torch.utils.data import DataLoader

loader = DataLoader(
    dataset,
    batch_size=8,
    shuffle=True,
    num_workers=4,
)

batch = next(iter(loader))
```

若使用上面的 4 帧 observation、16 步 action 配置：

```text
observation.images.front: [8, 4, 3, 256, 256]
observation.images.wrist: [8, 4, 3, 256, 256]
observation.state:        [8, 4, 8]
action:                   [8, 16, 7]
```

最前面的 `8` 是 batch size。

若没有设置 `delta_timestamps`，batch 大致是：

```text
observation.images.front: [8, 3, 256, 256]
observation.images.wrist: [8, 3, 256, 256]
observation.state:        [8, 8]
action:                   [8, 7]
```

字符串 `task` 经过 DataLoader 后通常是长度为 batch size 的字符串列表/序列。

## 九、打印真实 key、shape 和 dtype

首次使用时建议执行：

```python
from lerobot.datasets import LeRobotDataset

dataset = LeRobotDataset(
    repo_id="lerobot/libero_plus",
    episodes=[0],
    video_backend="torchcodec",
)

sample = dataset[0]

for key, value in sample.items():
    if hasattr(value, "shape"):
        print(
            key,
            "shape=", tuple(value.shape),
            "dtype=", value.dtype,
        )
    else:
        print(key, "type=", type(value).__name__, "value=", value)
```

不要一次下载整个数据集后才研究格式。可以先使用 `LeRobotDatasetMetadata` 只检查元数据：

```python
from pprint import pprint
from lerobot.datasets import LeRobotDatasetMetadata

meta = LeRobotDatasetMetadata("lerobot/libero_plus")
print(meta)
pprint(meta.features)
print(meta.tasks)
```

## 十、最容易混淆的五点

1. `data/file-000.parquet` 不是 episode 0，而是包含很多 frames/episodes 的数据 shard。
2. `videos/front/file-000.mp4` 不是一条 episode 视频，而是 front 相机的共享视频 shard。
3. `dataset[i]` 默认取一个 frame，不是完整 episode。
4. 图像元数据 shape 是 `[H,W,C]`，PyTorch 返回 shape 是 `[C,H,W]`。
5. 是否一次返回多帧、多步动作，不由磁盘目录决定，而由加载时的 `delta_timestamps` 和目标 policy 配置决定。

一句话总结：

```text
data/ 保存每个时刻的 state、action 和索引；
videos/ 保存两个摄像头的连续画面；
meta/ 描述 schema，并把 task、episode、Parquet 行与视频时间连接起来；
LeRobotDataset 把三者组装成模型可以直接使用的 PyTorch 样本。
```
