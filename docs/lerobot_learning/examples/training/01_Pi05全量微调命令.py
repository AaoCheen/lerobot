"""阅读版：构造 Pi05 全量微调命令。

这个文件的目的不是重新实现训练器，而是把 `lerobot-train` 命令拆开解释。
默认 RUN_TRAIN=False，所以直接运行只会打印命令，不会启动 GPU 训练。

本例的含义是：

    lerobot/pi05_libero_base
        -> 在 lerobot/libero 上更新全部可训练参数
        -> outputs/pi05_libero_full

如果 `freeze_vision_encoder=false` 且 `train_expert_only=false`，Pi05 的默认配置就是全量微调。
"""

import shlex
import subprocess


# 第一次阅读和检查参数时保持 False；确认数据、显存和输出目录后才改为 True。
RUN_TRAIN = False


def build_command() -> list[str]:
    # 每一个字符串都是传给命令行解析器的一个参数。
    # 与把整条命令拼成一个字符串相比，list 形式更不容易遇到引号和空格问题。
    return [
        "lerobot-train",
        # 训练 demonstrations 的来源。
        "--dataset.repo_id=lerobot/libero",
        # 使用 Pi05 的 policy 配置。
        "--policy.type=pi05",
        # pretrained_path 只表示“从哪里加载初始权重”；训练配置仍由下面参数和数据集决定。
        "--policy.pretrained_path=lerobot/pi05_libero_base",
        # Pi05 LIBERO 复现文档使用 mean/std，避免旧数据没有 q01/q99 时出错。
        '--policy.normalization_mapping={"ACTION":"MEAN_STD","STATE":"MEAN_STD","VISUAL":"IDENTITY"}',
        # 每次推理实际执行 10 步 action；它不能大于 chunk_size。
        "--policy.n_action_steps=10",
        # LIBERO 数据通常只有两个真实相机；这里补一个空相机以匹配 checkpoint 的输入布局。
        "--policy.empty_cameras=1",
        # 两个冻结开关都关闭，表示不主动冻结视觉编码器或 VLM。
        "--policy.freeze_vision_encoder=false",
        "--policy.train_expert_only=false",
        # Pi05 常用 bfloat16 以降低显存；硬件不支持时需要改成 float32。
        "--policy.dtype=bfloat16",
        "--policy.device=cuda",
        # 先保存到本地，避免第一次运行误上传 Hub。
        "--policy.push_to_hub=false",
        "--output_dir=outputs/pi05_libero_full",
        "--job_name=pi05_libero_full",
        "--batch_size=64",
        "--steps=30000",
        "--save_freq=5000",
        "--seed=1000",
    ]


def main() -> None:
    command = build_command()
    print("将要执行的命令：\n")
    # shlex.join 会自动为 JSON 等特殊参数加上 shell 引号，输出可以直接复制到终端。
    print(shlex.join(command))

    if not RUN_TRAIN:
        print("\nRUN_TRAIN=False：本次只打印命令，没有启动训练。")
        return

    # subprocess.run 会在当前 uv 环境中调用 lerobot-train。
    # 真正运行前应先执行：uv sync --locked --extra training --extra pi --extra libero
    subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
