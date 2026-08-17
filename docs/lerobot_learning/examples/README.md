# LeRobot Python 示例阅读区

这里不是对官方 `examples/` 的修改，而是面向初学者的中文注释版。原始示例仍然保留在仓库的 `examples/` 目录中；本目录只复制并改写最适合当前学习路线的部分。

## 推荐阅读顺序

### Dataset

1. [01_读取LeRobotDataset.py](./dataset/01_读取LeRobotDataset.py)
2. [02_时间窗口与DataLoader.py](./dataset/02_时间窗口与DataLoader.py)
3. [03_图像增强.py](./dataset/03_图像增强.py)

读完后应能回答：

- `LeRobotDatasetMetadata` 和 `LeRobotDataset` 的区别是什么；
- `dataset[i]` 返回一个 frame 还是一个 batch；
- 为什么单张图片是 `[C,H,W]`，加上时间窗口后变成 `[T,C,H,W]`；
- `DataLoader` 为什么又多出一个 batch 维度；
- action chunk 是如何通过 `delta_timestamps` 取出来的。

### Training

1. [01_Pi05全量微调命令.py](./training/01_Pi05全量微调命令.py)
2. [02_Pi05_LoRA微调命令.py](./training/02_Pi05_LoRA微调命令.py)
3. [03_训练核心流程阅读版.py](./training/03_训练核心流程阅读版.py)

训练示例中的 `RUN_TRAIN = False` 是有意设置的：第一次阅读时只打印命令，确认数据、模型、GPU 和输出目录后，再手动改成 `True`。不要在没有检查参数的情况下直接启动 Pi05 训练。

## 对照的官方源文件

- 数据集读取：`examples/dataset/load_lerobot_dataset.py`
- 图像增强：`examples/dataset/use_dataset_image_transforms.py`
- 训练入口：`src/lerobot/scripts/lerobot_train.py`
- Pi05 说明：`docs/source/pi05.mdx`
- PEFT/LoRA 说明：`docs/source/peft_training.mdx`

## 运行前提

这些文件中的命令优先使用 `uv run` 或已经由 `uv sync` 创建的环境。Dataset 示例会从 Hugging Face Hub 读取 `lerobot/libero` 的 metadata/数据；训练示例默认不会真正运行训练。
