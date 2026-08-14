# LeRobot 数据格式研究笔记

这个目录用于从“磁盘文件 → 单帧样本 → 时间窗口 → VLA 训练批次”四个层次研究 LeRobotDataset，而不是重复官方文档。

## 先回答核心问题

不能笼统地说“目前很多 VLA 都用 LeRobot 数据格式训练”。更准确的说法是：

- 在 **LeRobot 项目及其已接入的策略** 中，训练入口会统一通过 `LeRobotDataset` 读取数据，因此 ACT、Diffusion、SmolVLA、Pi0/Pi0.5 等在这个仓库里的训练适配通常面向 LeRobot 格式。
- 在更广泛的 VLA 生态中，仍常见 RLDS/TFDS、Open X-Embodiment、自定义 HDF5、WebDataset、原始 Parquet/视频等格式。模型论文使用什么原始数据格式，与某个开源实现后来支持 LeRobot 格式，是两件不同的事。
- LeRobot 更像一个正在扩大的机器人数据交换与训练接口，并不是所有 VLA 的唯一事实标准。

因此研究时应分开记录：**原始数据格式、转换后的 LeRobot 格式、模型训练时实际消费的字段**。

## 推荐阅读顺序

1. 阅读 [01_format_and_shapes.md](./01_format_and_shapes.md)，建立 v3.0 的文件结构和张量形状概念。
2. 按 [02_huggingface_inspection.md](./02_huggingface_inspection.md) 选一个小数据集，只看元数据，再看一条样本。
3. 如果目标是 LIBERO-OOD，先读 [03_libero_ood_dataset_selection.md](./03_libero_ood_dataset_selection.md)，固定 OOD 协议再选训练集。
4. 对 task、episode、frame、state 和 action 还不熟悉时，阅读 [04_libero_plus_format_explained.md](./04_libero_plus_format_explained.md)。
5. 要理解 Hub 的 `data/meta/videos` 目录和实际读取 shape，阅读 [05_HuggingFace数据集目录与LeRobotDataset读取.md](./05_HuggingFace数据集目录与LeRobotDataset读取.md)。
6. 对一个目标 VLA 检查 policy 配置和 processor，填写下面的研究表。
7. 最后才下载视频或完整数据集，避免一开始消耗大量磁盘和带宽。

## 每个数据集的研究记录模板

| 项目 | 记录 |
|---|---|
| Hub `repo_id` | |
| LeRobot 版本 | |
| 原始数据来源/原始格式 | |
| robot type | |
| FPS | |
| episode 数 / frame 数 | |
| task 数及示例 | |
| `observation.state` shape / 含义 | |
| `action` shape / 含义 | |
| camera keys / 分辨率 | |
| 是否有 language/task 字段 | |
| 目标 policy | |
| policy 实际使用的 observation keys | |
| observation history | |
| action horizon/chunk size | |
| 是否需要字段重命名或转换 | |
| 已发现的风险 | |

## 仓库内的事实来源

- 正式格式说明：`docs/source/lerobot-dataset-v3.mdx`
- 核心读取接口：`src/lerobot/datasets/lerobot_dataset.py`
- 元数据接口：`src/lerobot/datasets/dataset_metadata.py`
- 训练数据配置：`src/lerobot/configs/default.py`
- 加载示例：`examples/dataset/load_lerobot_dataset.py`
- 外部数据转换示例：`examples/port_datasets/`

> 本笔记按当前仓库代码记录：`CODEBASE_VERSION = "v3.0"`。以后切换分支或更新仓库时，应先重新确认版本。
