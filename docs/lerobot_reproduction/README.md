# LeRobot 初始复现实验：LIBERO 与 LIBERO-plus

这个目录是实验分支 `reproduce/my_branch1` 的起点，当前只做仿真评测，不做真实机器人部署，也不立刻改模型代码。

目标是先回答一个最基本的问题：

> 同一个 VLA checkpoint，在标准 LIBERO 和加入扰动的 LIBERO-plus 上分别表现如何？

## 必须按顺序阅读和执行

| 顺序 | 内容 | 你要做的事 |
| --- | --- | --- |
| 1 | [01_环境准备.md](./01_环境准备.md) | 检查 GPU、MuJoCo，并建立两个隔离环境 |
| 2 | [02_模型权重.md](./02_模型权重.md) | 选择第一个要评测的 VLA checkpoint |
| 3 | [03_LIBERO评测.md](./03_LIBERO评测.md) | 先跑一个 task、一个 episode 的冒烟测试，再跑完整套件 |
| 4 | [04_LIBERO-plus评测.md](./04_LIBERO-plus评测.md) | 在独立的 LIBERO-plus 环境中重复同一模型评测 |
| 5 | [05_结果记录表.md](./05_结果记录表.md) | 记录模型、数据 revision、seed、成功率和错误 |

对应的可执行脚本在 [scripts](./scripts) 目录中。每个脚本只做一件事；第一次不要直接跑完整 benchmark。

## 第一个推荐实验

先使用：

```text
模型：lerobot/smolvla_libero
标准环境：libero
扰动环境：libero_plus
任务：libero_spatial
task_id：[0]
每个 task 的 episode 数：1
seed：1000
```

原因是它已经针对 `lerobot/libero` 提供了 checkpoint，权重文件约 907 MB，适合先验证整条流程。流程跑通后，再换成 Pi05 和 XVLA。

## 推荐权重的角色

| checkpoint | 用途 | 初步建议 |
| --- | --- | --- |
| `lerobot/smolvla_libero` | 小型、已在 LIBERO 数据上训练的 VLA | 第一个冒烟和完整评测 |
| `lerobot/pi05_libero_finetuned_v044` | Pi05 的 LIBERO 微调 checkpoint | 主结果或高性能对照 |
| `lerobot/xvla-libero` | 独立的 XVLA 架构，已在 LIBERO 上训练/评测 | 第二个架构对照 |
| `lerobot/pi0fast-libero-v044` | Pi0-FAST 的 LIBERO checkpoint | 可选；需要额外处理相机 key |
| `lerobot/pi05_libero_base` | Pi05 的 LIBERO 起始权重 | 后续做全量微调，不作为第一个已训练 baseline |
| `lerobot/smolvla_base` | SmolVLA 通用基础权重 | 后续自己训练，不作为第一个已训练 baseline |

LIBERO-plus 是对 LIBERO 的扰动扩展。第一轮不要在 `lerobot/libero_plus` 上训练，而是把在标准 LIBERO 上训练或发布的 checkpoint 直接拿去 LIBERO-plus 测试；这样才有清楚的鲁棒性/OOD 含义。

## 结果可比性的最低要求

- 同一模型在 LIBERO 与 LIBERO-plus 上使用相同的 `seed`；
- 同一套 task、`task_id`、episode 数和 `batch_size`；
- 记录 LeRobot commit、模型 Hub revision、数据集 revision；
- 先使用 `--eval.batch_size=1`，排除并行环境造成的额外问题；
- 先通过单 task 冒烟测试，再运行四个 suite 的完整评测；
- 不把 LIBERO 训练集上的 loss 和 LIBERO-plus 成功率混为一个指标。

## 当前不做的事情

- 不进行 `lerobot-train`；
- 不进行 LoRA 或模型结构改动；
- 不同时安装 vanilla LIBERO 和 LIBERO-plus 到同一个环境；
- 不一开始运行 400 个以上 episode 的完整 benchmark；
- 不把 `lerobot/pi05_libero_finetuned_v044` 误称为从头训练的模型。
