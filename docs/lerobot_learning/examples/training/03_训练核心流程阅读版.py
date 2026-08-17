"""阅读版：把 lerobot-train 的真实执行顺序写成可读的伪代码。

这不是第二个训练器，也不应该被当作可运行实现。它对应：

    src/lerobot/scripts/lerobot_train.py

目的只是先建立调用关系，再去读官方训练脚本的具体细节。
"""


def explain_training_flow() -> None:
    # 1. 解析命令行和 dataclass 配置。
    #    draccus 会把 --dataset.*、--policy.*、--peft.* 等参数组装成 cfg。
    print("1. 解析 TrainPipelineConfig")

    # 2. 创建 LeRobotDataset 和可选的 eval_dataset。
    #    这一步根据 dataset.repo_id、episodes、delta_timestamps 等设置读取数据。
    print("2. make_train_eval_datasets(cfg)")

    # 3. 根据 policy.type 建立 policy；如果指定 pretrained_path/path，就加载权重。
    #    对 Pi05 来说，这里会构造视觉语言模型、action expert 和 action projection。
    print("3. make_policy(cfg.policy, ds_meta=dataset.meta)")

    # 4. 如果 cfg.peft 不为空，把已有 policy 包装成 PEFT/LoRA policy。
    #    此时基础权重大多被冻结，optimizer 主要看到 adapter 参数和 modules_to_save。
    print("4. policy.wrap_with_peft(...)  # 仅在指定 --peft.* 时发生")

    # 5. 创建 preprocessor/postprocessor。
    #    preprocessor 负责把原始 batch 变成 policy 输入：dtype、归一化、重命名、图像处理、文本等；
    #    postprocessor 在 rollout/eval 时把 policy action 还原为环境需要的格式。
    print("5. make_pre_post_processors(...) ")

    # 6. 创建 optimizer、scheduler、DataLoader 和 accelerator。
    #    训练时不要手动猜哪些参数参与更新，应该让 optimizer 根据 requires_grad 选择参数。
    print("6. make_optimizer_and_scheduler(...) + DataLoader + Accelerator")

    # 7. 反复执行训练 step。
    #    下面四行是最核心的数学流程：前向得到 loss，反向得到梯度，optimizer 更新权重，scheduler 调整学习率。
    print("7. batch -> preprocessor -> policy(batch) -> loss.backward() -> optimizer.step()")

    # 8. 定期保存 checkpoint；里面通常包含模型、processor、训练配置和可选的 optimizer 状态。
    #    论文复现实验至少要保存 output_dir、训练命令、seed 和对应 checkpoint。
    print("8. save_checkpoint(...)")

    # 9. 如果配置了环境评测，训练过程中还可以调用 eval_policy_all；也可以训练结束后单独 lerobot-eval。
    print("9. optional: eval_policy_all(...) / lerobot-eval")


if __name__ == "__main__":
    explain_training_flow()
