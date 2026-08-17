"""阅读版：在训练读取阶段加入图像增强。

图像增强不会修改 Hugging Face Hub 上的原始视频；它只在取样时对 Tensor 做变换。
这使得你可以把“是否增强、增强强度、随机顺序”作为论文实验变量，而不用重新采集数据。

第一次阅读时重点看：
1. ImageTransformsConfig 如何描述增强策略；
2. ImageTransforms 如何被传给 LeRobotDataset；
3. 同一个 dataset index 在不同随机增强下可能产生不同图片。
"""

import torch
from torchvision.transforms import v2

from lerobot.datasets import LeRobotDataset
from lerobot.transforms import ImageTransformConfig, ImageTransforms, ImageTransformsConfig


def main() -> None:
    repo_id = "lerobot/libero"

    # 不加 image_transforms 时，拿到的是原始解码后的图像 Tensor。
    dataset_original = LeRobotDataset(repo_id, episodes=[0])

    # LeRobot 自己的配置式增强：
    # - enable=True：打开增强；
    # - max_num_transforms：一次最多抽取几个变换；
    # - random_order：是否随机改变变换的执行顺序；
    # - weight：不同增强被抽到的相对概率。
    config = ImageTransformsConfig(
        enable=True,
        max_num_transforms=2,
        random_order=True,
        tfs={
            "brightness": ImageTransformConfig(
                weight=1.0,
                type="ColorJitter",
                kwargs={"brightness": (0.8, 1.2)},
            ),
            "contrast": ImageTransformConfig(
                weight=1.0,
                type="ColorJitter",
                kwargs={"contrast": (0.8, 1.2)},
            ),
        },
    )
    dataset_lerobot_transforms = LeRobotDataset(
        repo_id,
        episodes=[0],
        image_transforms=ImageTransforms(config),
    )

    camera_key = dataset_original.meta.camera_keys[0]
    original = dataset_original[0][camera_key]
    transformed = dataset_lerobot_transforms[0][camera_key]
    print(f"相机列：{camera_key}")
    print(f"原始图片：{tuple(original.shape)}, dtype={original.dtype}")
    print(f"增强图片：{tuple(transformed.shape)}, dtype={transformed.dtype}")

    # 也可以直接传 torchvision v2 的变换组合。
    # 这种方式适合你已经熟悉 torchvision，想快速写一个实验版本的情况。
    torchvision_transforms = v2.Compose(
        [
            v2.ColorJitter(brightness=0.2, contrast=0.2),
            v2.RandomRotation(degrees=5),
        ]
    )
    dataset_torchvision = LeRobotDataset(
        repo_id,
        episodes=[0],
        image_transforms=torchvision_transforms,
    )
    print(f"torchvision 增强图片：{tuple(dataset_torchvision[0][camera_key].shape)}")


if __name__ == "__main__":
    main()
