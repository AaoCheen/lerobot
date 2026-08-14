# LeRobotDataset v3.0：文件、样本与批次形状

## 1. 磁盘层

典型结构如下：

```text
dataset_root/
├── meta/
│   ├── info.json
│   ├── stats.json
│   ├── tasks.parquet
│   └── episodes/chunk-xxx/file-xxx.parquet
├── data/chunk-xxx/file-xxx.parquet
└── videos/<camera_key>/chunk-xxx/file-xxx.mp4
```

- `meta/info.json`：版本、FPS、robot type、feature 名称、dtype、逻辑 shape 和路径模板。
- `meta/stats.json`：归一化所需的统计量。
- `meta/tasks.parquet`：自然语言任务与整数 task index 的映射。
- `meta/episodes/`：episode 边界、长度、任务以及数据/视频定位信息。
- `data/`：逐 frame 的低维信号，例如 state、action、timestamp 和索引。
- `videos/`：按 camera key 分开存储的视频。

v3.0 是 **file-based**：一个 Parquet/MP4 文件通常包含多个 episode。episode 是由元数据重建的逻辑视图，不能再假定“一集一个文件”。

## 2. 单个 frame 的逻辑样本

`dataset[i]` 通常返回一个字典，常见内容为：

```python
{
    "observation.state": Tensor[state_dim],
    "action": Tensor[action_dim],
    "observation.images.front": Tensor[C, H, W],
    "timestamp": Tensor[],
    "frame_index": Tensor[],
    "episode_index": Tensor[],
    "task_index": Tensor[],
    "task": str,
}
```

具体 key 不是全局固定的，必须以目标数据集的 `meta/info.json["features"]` 和实际 `dataset[0]` 为准。

一个容易混淆的细节：元数据中的图像逻辑 shape 通常是 `[H, W, C]`，但读取后的 PyTorch tensor 是 `[C, H, W]`。

## 3. 时间窗口

VLA 很少只消费一个孤立 frame。LeRobot 用 `delta_timestamps` 表达相对当前时刻的历史 observation 和未来 action：

```python
delta_timestamps = {
    "observation.images.front": [-0.2, -0.1, 0.0],
    "observation.state": [-0.2, -0.1, 0.0],
    "action": [i / fps for i in range(16)],
}
```

此时单条样本的大致形状变为：

```text
image:  [T_obs, C, H, W]
state:  [T_obs, state_dim]
action: [T_action, action_dim]
```

时间差应与 `1 / fps` 对齐。边界处还应检查 padding 及其 mask，不能仅看 tensor shape。

## 4. DataLoader 批次

加上 batch 维后：

```text
image:  [B, T_obs, C, H, W]
state:  [B, T_obs, state_dim]
action: [B, T_action, action_dim]
```

如果没有为某个 key 配置时间窗口，可能没有 `T` 维。因此记录 shape 时必须同时记录加载配置，不能只抄一组数字。

## 5. 从数据格式到目标 VLA

判断某个 VLA 是否能直接训练，至少核对：

1. policy 需要哪些 key，数据集是否都有；
2. state/action 每一维的物理含义、顺序和单位是否匹配；
3. 相机数量、命名、分辨率和通道顺序是否匹配；
4. task 文本在哪里生成，是否进入 tokenizer/processor；
5. observation history、action horizon 与 FPS 是否匹配；
6. normalization 使用数据集 stats、ImageNet stats，还是模型自带统计量；
7. episode 边界处的 padding/mask 如何处理。

“能被 `LeRobotDataset` 加载”只说明存储兼容，不等于语义上能直接用于任意 VLA。
