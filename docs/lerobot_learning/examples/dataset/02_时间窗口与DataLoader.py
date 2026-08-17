"""阅读版：观察时间窗口、action chunk 和 DataLoader 的形状变化。

这是理解 VLA 训练输入最重要的 Dataset 示例之一：

    一个 frame       -> dataset[index]
    一个时间窗口     -> [T, ...]
    一个 batch        -> [B, T, ...]

`delta_timestamps` 的每个数字都是“相对于当前 frame 的时间偏移”，单位是秒。
例如 [-2*dt, -dt, 0] 表示取当前时刻之前两个 frame、之前一个 frame 和当前 frame。
"""

import torch

from lerobot.datasets import LeRobotDataset, LeRobotDatasetMetadata


def main() -> None:
    repo_id = "lerobot/libero"

    # 先读 metadata，获取 fps 和相机列名。
    metadata = LeRobotDatasetMetadata(repo_id)
    dt = 1.0 / metadata.fps
    camera_key = metadata.camera_keys[0]

    # 这里故意使用 frame 间隔构造时间，而不是硬编码 0.1 秒。
    # 这样即使数据集 fps 改变，时间偏移仍然落在合法的采样网格上。
    delta_timestamps = {
        # 给模型 3 张连续历史/当前图片。
        camera_key: [-2 * dt, -dt, 0.0],
        # 同样给模型 3 个时刻的 proprioceptive state。
        "observation.state": [-2 * dt, -dt, 0.0],
        # 取当前时刻开始的 8 步未来 action，形成一个短 action chunk。
        "action": [i * dt for i in range(8)],
    }

    # dataset[0] 仍然代表“以第 0 个 frame 为中心的一条样本”，
    # 但其中的图片/state/action 已经带有时间维度 T。
    dataset = LeRobotDataset(repo_id, episodes=[0], delta_timestamps=delta_timestamps)
    sample = dataset[0]

    print(f"fps={metadata.fps}, dt={dt:.4f}s")
    print("单个带时间窗口样本的形状：")
    print(f"  {camera_key}:              {tuple(sample[camera_key].shape)}")
    print(f"  observation.state:         {tuple(sample['observation.state'].shape)}")
    print(f"  action:                    {tuple(sample['action'].shape)}")
    print(f"  task:                      {sample['task']}")

    # DataLoader 负责把多个样本拼成 batch。
    # 因此图片会从 [T,C,H,W] 变成 [B,T,C,H,W]，action 会从 [T,A] 变成 [B,T,A]。
    dataloader = torch.utils.data.DataLoader(
        dataset,
        batch_size=2,
        shuffle=True,
        num_workers=0,  # 初学者先用 0，避免多进程错误；稳定后再增大。
    )
    batch = next(iter(dataloader))

    print("\nDataLoader batch 的形状：")
    print(f"  {camera_key}:              {tuple(batch[camera_key].shape)}")
    print(f"  observation.state:         {tuple(batch['observation.state'].shape)}")
    print(f"  action:                    {tuple(batch['action'].shape)}")

    # 这个打印非常值得记住：
    # B 是 batch size，T 是时间窗口长度，C/H/W 是图片维度，A 是 action 维度。
    # Pi05 等 VLA 会在 processor 中继续调整 dtype、归一化方式和文本输入。
    print("\n维度含义：B=batch，T=时间步，C=通道，H/W=图像高宽，A=动作维度")


if __name__ == "__main__":
    main()
