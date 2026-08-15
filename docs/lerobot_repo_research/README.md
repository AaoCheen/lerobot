# LeRobot 仓库能力、VLA 模型与 Benchmark 概览

> 本笔记以当前 `my_forks/lerobot` 的 `main` 基线代码和仓库内文档为准。LeRobot 更新较快，模型和 benchmark 列表以后可能变化。

## 1. 这个仓库可以用来做什么

LeRobot 是一个面向机器人学习的 PyTorch 工具库。它把以下环节放在同一套接口中：

```text
遥操作机器人
→ 采集演示轨迹
→ 保存为 LeRobotDataset
→ 训练或微调策略/VLA
→ 在模拟 benchmark 中评测
→ 部署到真实机器人执行任务
```

主要能力包括：

1. **控制机器人硬件**：机器人、相机、电机和遥操作设备都有统一接口。
2. **采集数据**：用 `lerobot-record` 记录视频、机器人 state、action 和自然语言 task。
3. **管理数据集**：使用 LeRobotDataset v3.0 读取、写入、转换、切分、合并和上传数据。
4. **训练策略**：通过统一的 `lerobot-train` 训练传统模仿学习策略或大型 VLA。
5. **评测策略**：通过 `lerobot-eval` 在模拟环境中运行 rollout 并统计成功率。
6. **部署模型**：通过 `lerobot-rollout` 在真实机器人或环境中持续观察和执行动作。
7. **扩展组件**：可以接入新的机器人、policy、processor、数据集和 benchmark。

常用入口：

```text
lerobot-record       采集数据
lerobot-train        训练或微调模型
lerobot-eval         在 benchmark 中评测
lerobot-rollout      部署策略并运行 rollout
lerobot-teleoperate  遥操作机器人
lerobot-replay       回放已记录动作
```

## 2. 能不能微调 VLA

可以，这是 LeRobot 的核心用途之一。

基本思路是：

```text
预训练 VLA checkpoint
+ LeRobot 格式的机器人数据集
→ lerobot-train
→ 适配目标机器人、相机、动作空间和任务的新 checkpoint
```

以 SmolVLA 为例：

```bash
lerobot-train \
  --policy.path=lerobot/smolvla_base \
  --dataset.repo_id=<用户名>/<数据集> \
  --batch_size=64 \
  --steps=20000 \
  --output_dir=outputs/train/my_smolvla \
  --job_name=my_smolvla_training \
  --policy.device=cuda
```

这条命令表示：读取一个预训练 SmolVLA，使用指定 LeRobotDataset 继续训练。

不同 VLA 的 checkpoint 参数并不完全相同：

- 有些使用 `--policy.path=<checkpoint>`；
- 有些使用 `--policy.type=<类型>` 和 `--policy.pretrained_path=<checkpoint>`；
- GR00T 等模型还有自己的 base model 和 embodiment 配置。

因此真正开始前应先阅读对应的 `docs/source/<模型名>.mdx`，不要把一个模型的命令直接套到另一个模型上。

### 常见微调方式

```text
全量微调
训练 VLM、视觉编码器和动作专家，效果潜力较大，但显存需求最高。

冻结视觉/VLM
只训练动作专家或投影层，显存需求更低。

PEFT / LoRA
只训练少量 adapter 参数，适合算力有限或数据量较小的情况。

从零训练小策略
ACT、Diffusion 等策略通常可以直接在自己的演示数据上训练。
```

### 数据必须满足什么

至少需要核对：

- 图像 key 和模型期望的相机 key 是否一致；
- `observation.state` 的维度、顺序和含义；
- `action` 的维度、单位以及相对/绝对控制方式；
- FPS、历史 observation 长度和 action chunk 长度；
- 是否有自然语言 `task`；
- normalization statistics 是否正确。

“能够被 `LeRobotDataset` 加载”不代表能够直接微调任意 VLA。不同机器人之间通常还需要 processor、`rename_map` 或动作表示转换。

## 3. 当前仓库中的 VLA 模型

下面列的是当前官方文档明确展示的视觉-语言-动作模型或相关大型机器人基础策略。

| 模型 | LeRobot policy type | 定位 |
|---|---|---|
| SmolVLA | `smolvla` | Hugging Face 的轻量 VLA，约 450M，适合入门微调 |
| π₀ / Pi0 | `pi0` | Physical Intelligence 系列 VLA |
| π₀-FAST | `pi0_fast` | 使用 FAST 动作表示的 Pi0 变体 |
| π₀.₅ / Pi05 | `pi05` | Pi 系列后续 VLA，支持动作专家微调等配置 |
| MolmoAct2 | `molmoact2` | AllenAI 的 VLA，支持全量、LoRA和动作专家微调 |
| VLA-JEPA | `vla_jepa` | 将视觉表征/world model 与动作生成结合的 VLA |
| EO-1 | `eo1` | 接入 LeRobot policy 接口的大型机器人策略 |
| LingBot-VA | `lingbot_va` | 面向视频/动作建模的 VLA |
| FastWAM | `fastwam` | World Action Model，可用标准训练接口训练 |
| EVO1 | `evo1` | 分阶段训练动作头和 VLM 的 VLA |
| NVIDIA GR00T N1.7 | `groot` | 多 embodiment 机器人基础模型 |
| X-VLA | `xvla` | 跨 embodiment VLA |
| WALL-OSS / WallX | `wall_x` | WALL-OSS checkpoint 的 LeRobot policy 集成 |

### 哪个适合先尝试

如果目的是理解完整微调流程，建议顺序为：

```text
SmolVLA
→ Pi0/Pi05
→ MolmoAct2、GR00T 或其他更大型模型
```

SmolVLA 的文档、基础 checkpoint 和标准微调命令最直接，但仍需要合适的 GPU 和高质量演示数据。

## 4. 仓库里还有哪些非 VLA 策略

`src/lerobot/policies/` 不等于“全部都是 VLA”。当前还包括：

| 策略 | policy type | 说明 |
|---|---|---|
| ACT | `act` | Action Chunking Transformer，经典模仿学习策略 |
| Diffusion Policy | `diffusion` | 用扩散模型生成动作序列 |
| VQ-BeT | `vqbet` | 基于离散动作 token 的行为生成策略 |
| TD-MPC | `tdmpc` | 强化学习/模型预测控制方向策略 |
| Multitask DiT | `multi_task_dit` | 多任务扩散 Transformer 动作策略 |
| Gaussian Actor | `gaussian_actor` | 高斯动作分布策略 |

此外，`rtc` 是 Real-Time Chunking 推理机制，不应当当作一个独立 VLA 模型。

## 5. 当前可以测试哪些 Benchmark

### 直接注册在 LeRobot 环境配置中的 benchmark

| Benchmark | `--env.type` | 主要测试内容 |
|---|---|---|
| LIBERO | `libero` | 多任务桌面操作、空间/物体/目标/长时序任务 |
| LIBERO-plus | `libero_plus` | 对布局、相机、语言、光照、纹理和噪声等 OOD 扰动的鲁棒性 |
| Meta-World | `metaworld` | 大量标准机械臂操作任务 |
| RoboCasa365 | `robocasa` | 厨房和家庭场景操作 |
| RoboTwin 2.0 | `robotwin` | 多任务、复杂场景和泛化评测 |
| RoboMME | `robomme` | 多 embodiment、多任务机器人评测 |
| VLABench | `vlabench` | 面向 VLA 的语言条件操作 benchmark |
| NVIDIA IsaacLab Arena | `isaaclab_arena` | 通过 EnvHub/IsaacLab 接入的模拟任务 |

仓库还提供 ALOHA 和 PushT 环境配置，适合传统 imitation learning 策略的训练与评测。

### 文档中列出的扩展 benchmark

当前 benchmark 文档还包括：

- RoboCerebra；
- EnvHub 中的更多环境；
- LeIsaac/IsaacLab 模拟环境。

其中部分 benchmark 通过外部包、Docker 镜像或 EnvHub 接入，不一定在基础安装后直接可运行。

## 6. 一个模型能否测试所有 Benchmark

不能默认可以。

要在某个 benchmark 上运行，至少需要同时满足：

```text
模型 checkpoint 可加载
+ 环境依赖安装完成
+ 相机和 state key 对齐
+ action 维度及控制方式一致
+ processor/rename_map 正确
+ 模型曾在相近 embodiment 或数据上训练
```

例如 LIBERO 常见输入输出为：

```text
两路 256×256 RGB 图像
8维 observation.state
7维 action
自然语言 task
```

如果 checkpoint 期望不同相机名或不同 action 表示，即使 shape 相同，也可能需要重命名或转换。

## 7. Benchmark 的基本评测方式

一般通过：

```bash
lerobot-eval \
  --policy.path=<模型checkpoint> \
  --env.type=<benchmark类型> \
  --env.task=<任务或suite> \
  --eval.n_episodes=10
```

一次 evaluation episode 表示模型从环境 reset 开始，持续观察并执行动作，直到成功或达到最大步数。最常见指标是 success rate：

```text
10个 episodes 中成功8个
→ success rate = 80%
```

不同 benchmark 的安装、task 名称、episode 长度和推荐评测次数不同，应以对应文档为准。

## 8. 推荐的研究路线

如果目标是研究 VLA 微调与 OOD，建议：

```text
第一步：理解 LeRobotDataset 的 frame / episode / task
第二步：用 SmolVLA 跑通一个小规模微调
第三步：在标准 LIBERO 上建立 ID baseline
第四步：直接在 LIBERO-plus 上测试 zero-shot OOD
第五步：再研究 Pi05、MolmoAct2 或 GR00T
```

不要一开始同时更换模型、数据集、动作表示和 benchmark，否则失败时很难确定问题来自哪一层。

## 9. 仓库内建议优先阅读的位置

```text
docs/source/index.mdx                 LeRobot 总体介绍
docs/source/lerobot-dataset-v3.mdx   数据格式
docs/source/smolvla.mdx              SmolVLA 微调
docs/source/pi0.mdx                  Pi0 训练
docs/source/pi05.mdx                 Pi05 训练与微调
docs/source/molmoact2.mdx            MolmoAct2 微调
docs/source/groot.mdx                GR00T 微调
docs/source/libero.mdx               LIBERO 训练和评测
docs/source/libero_plus.mdx          LIBERO-plus OOD 评测
src/lerobot/policies/                policy 实现
src/lerobot/envs/configs.py          已注册环境类型
```

## 结论

LeRobot 不只是机器人控制库，也是一套贯通数据采集、LeRobotDataset、策略/VLA 微调、模拟 benchmark 评测和真实机器人部署的工作流。它可以微调 SmolVLA、Pi0/Pi05、MolmoAct2、GR00T 等 VLA，也能训练 ACT、Diffusion 等传统策略；当前已直接接入 LIBERO、LIBERO-plus、Meta-World、RoboCasa365、RoboTwin、RoboMME、VLABench 和 IsaacLab Arena 等 benchmark。
