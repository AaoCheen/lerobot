"""阅读版：从已有 Pi05 checkpoint 开始做 LoRA 微调。

本例从已经在 LIBERO 上微调过的：

    lerobot/pi05_libero_finetuned_v044

继续训练一个参数高效的 LoRA adapter。它不是从头训练，也不是再次全量更新基础模型。

第一次阅读时重点区分：
- `--policy.path`：读取 checkpoint 的配置和权重；
- `--peft.method_type=LORA`：让训练器用 PEFT 包装 policy；
- `--peft.r`：LoRA 的低秩大小，越大通常越接近全量微调，但参数也越多；
- Pi05 默认只对指定的 action expert/projection 模块加 adapter，不等于整个 VLM 都加 LoRA。
"""

import shlex
import subprocess


# 防止第一次阅读时误启动训练。
RUN_TRAIN = False


def build_command() -> list[str]:
    return [
        "lerobot-train",
        "--dataset.repo_id=lerobot/libero",
        # 对一个已经保存的 LeRobot checkpoint，使用 policy.path 最简单。
        # 它会读取 checkpoint 的 config.json 和模型权重，因此这里不再写 policy.type。
        "--policy.path=lerobot/pi05_libero_finetuned_v044",
        # 下面三个参数开启 LoRA。当前仓库需要 lerobot[peft] 依赖。
        "--peft.method_type=LORA",
        "--peft.r=16",
        "--peft.lora_alpha=32",
        # 使用新的输出目录，避免覆盖输入 checkpoint。
        "--output_dir=outputs/pi05_libero_lora",
        "--job_name=pi05_libero_lora",
        "--policy.push_to_hub=false",
        "--batch_size=32",
        "--steps=10000",
        "--save_freq=2000",
        "--seed=1000",
    ]


def main() -> None:
    command = build_command()
    print("将要执行的命令：\n")
    # shlex.join 会自动处理 shell 引号，避免复制命令时 JSON 参数失效。
    print(shlex.join(command))

    if not RUN_TRAIN:
        print("\nRUN_TRAIN=False：本次只打印命令，没有启动训练。")
        return

    # LoRA 训练前安装：
    # uv sync --locked --extra training --extra pi --extra peft --extra libero
    # Pi05 文档还提醒：EMA 不应与 PEFT adapter 一起使用；不要额外打开 ema.enable。
    subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
