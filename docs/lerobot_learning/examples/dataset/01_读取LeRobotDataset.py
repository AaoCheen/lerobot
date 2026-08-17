"""阅读版：读取 LeRobot 数据集中的 metadata 和单个 frame。

这个文件对应官方 examples/dataset/load_lerobot_dataset.py 的核心内容，
但去掉了与第一次学习无关的 Hub 全量搜索，并换成了 LIBERO 数据集。

第一次运行前请记住：
1. 这里只是读取数据，不会训练模型；
2. 第一次访问 Hugging Face 数据集可能会下载视频和 parquet 文件；
3. dataset[0] 返回的是一个 frame 的字典，不是 batch；
4. 图片在 LeRobotDataset 中通常已经转换为 PyTorch 的 [C, H, W]。
"""

from pprint import pprint

from lerobot.datasets import LeRobotDataset, LeRobotDatasetMetadata


def main() -> None:
    # repo_id 是 Hugging Face Hub 上的数据集标识。
    # 这里使用 Pi05 文档中对应 LIBERO 的数据集；也可以替换成你自己的数据集。
    repo_id = "lerobot/libero"

    # Metadata 只负责读取数据集的“目录信息”：总 episode 数、fps、feature 形状、
    # 相机名字和统计量等。它不会立刻把全部视频帧加载进内存。
    metadata = LeRobotDatasetMetadata(repo_id)
    print("数据集 metadata：")
    print(f"  episodes: {metadata.total_episodes}")
    print(f"  frames:   {metadata.total_frames}")
    print(f"  fps:      {metadata.fps}")
    print(f"  cameras:  {metadata.camera_keys}")
    print(f"  tasks:    {metadata.tasks}")

    # features 是数据集的“列定义”。它告诉我们每一列的 dtype、shape 和 names。
    # 例如 observation.state 是机器人状态，action 是监督信号，
    # observation.images.* 是相机图像。
    print("\n数据集 features：")
    pprint(metadata.features)

    # episodes=[0] 表示只读取第 0 个 episode，适合第一次检查形状。
    # 如果不传 episodes，LeRobotDataset 会把整个数据集作为训练数据读取。
    dataset = LeRobotDataset(repo_id, episodes=[0])
    print("\n选中的数据：")
    print(f"  selected episodes: {dataset.num_episodes}")
    print(f"  selected frames:   {dataset.num_frames}")

    # LeRobotDataset 实现了 PyTorch Dataset 接口，所以 dataset[0] 是一个样本。
    # 在这里，“样本”默认对应一个时间点 frame，不是一个 episode，也不是一个 batch。
    sample = dataset[0]
    print("\n第一个 frame 的字段：")
    for key, value in sample.items():
        # task 是文本，其他字段通常是 Tensor；用 getattr 让打印代码兼容两者。
        shape = getattr(value, "shape", None)
        dtype = getattr(value, "dtype", None)
        print(f"  {key}: type={type(value).__name__}, shape={shape}, dtype={dtype}")

    # 相机 feature 的 metadata shape 常写成 [H, W, C]，这是数据文件的通用描述。
    # 但取出来的图片 Tensor 通常是 [C, H, W]，这是 PyTorch 的 channel-first 约定。
    for camera_key in metadata.camera_keys:
        if camera_key not in sample:
            continue
        image = sample[camera_key]
        print(f"\n相机 {camera_key}：")
        print(f"  metadata shape (H,W,C): {metadata.features[camera_key]['shape']}")
        print(f"  Tensor shape (C,H,W):    {tuple(image.shape)}")

    # episode 元数据保存了每个 episode 在扁平 frame 表中的起止位置。
    # 这能帮助你理解：episode 是连续 frame 的一段，而不是单独的一张图片。
    episode_index = 0
    start = metadata.episodes["dataset_from_index"][episode_index]
    end = metadata.episodes["dataset_to_index"][episode_index]
    print(f"\n第 {episode_index} 个 episode 的扁平 frame 范围：[{start}, {end})")
    print(f"该 episode 的 frame 数量：{end - start}")


if __name__ == "__main__":
    main()
