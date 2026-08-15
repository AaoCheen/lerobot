# LeRobot Benchmark、模拟环境与训练数据集

> 本笔记按当前 `my_forks/lerobot` 仓库的 benchmark 文档整理。这里必须区分：benchmark、模拟器、任务框架和训练数据集不是同一个东西。

## 1. 先区分四个概念

```text
底层模拟器 simulator
例如 MuJoCo、SAPIEN、Isaac Sim，负责物理计算和渲染。

任务框架 environment/task framework
例如 robosuite、ManiSkill、dm_control，负责封装机器人、场景和任务接口。

Benchmark
例如 LIBERO、RoboTwin，定义任务集合、数据、成功条件和评测协议。

Dataset
保存专家演示，用于训练或微调模型；评测时通常不重放训练数据。
```

因此，“LIBERO”不是和 MuJoCo 并列的底层 simulator。更准确的层次是：

```text
LIBERO benchmark
→ 基于 robosuite
→ robosuite 使用 MuJoCo
```

## 2. LeRobot 中各 benchmark 运行在哪里

| Benchmark | 底层模拟器 | 上层环境/任务框架 | 机器人与动作特点 | LeRobot 训练数据 |
|---|---|---|---|---|
| LIBERO | MuJoCo | robosuite + LIBERO | Franka Panda，8维 state，7维末端相对动作 | `lerobot/libero`；也可用同 schema 的 `HuggingFaceVLA/libero` |
| LIBERO-plus | MuJoCo | robosuite + LIBERO-plus | 与 LIBERO 相同的 Panda/动作接口，增加多类 OOD 扰动 | `lerobot/libero_plus` |
| RoboCerebra | MuJoCo | LIBERO/robosuite stack | Panda，长时序任务，7维动作，多级自然语言子任务 | `lerobot/robocerebra_unified` |
| Meta-World MT50 | MuJoCo | Meta-World | Sawyer 操作任务，Meta-World 自己的任务与控制接口 | `lerobot/metaworld_mt50` |
| RoboCasa365 | MuJoCo | robosuite + RoboCasa | PandaOmron 移动操作平台，12维动作 | 单任务示例 `pepijn223/robocasa_CloseFridge`，另有 RoboCasa demonstrations |
| VLABench | MuJoCo | dm_control + VLABench | Franka Panda，语言条件长时序任务，7维动作 | `VLABench/vlabench_primitive_ft_lerobot_video`、`VLABench/vlabench_composite_ft_lerobot_video` |
| RoboTwin 2.0 | SAPIEN | RoboTwin | 双臂机器人，14维 joint-space 动作，强 domain randomization | `lerobot/robotwin_unified` |
| RoboMME | SAPIEN | ManiSkill + RoboMME | Panda，记忆型任务，支持 8维 joint-angle 或7维 ee-pose | `lerobot/robomme` |
| IsaacLab Arena | NVIDIA Isaac Sim | IsaacLab + IsaacLab Arena + EnvHub | GR1、G1 等人形/全身机器人，GPU 并行模拟 | NVIDIA Arena、Lightwheel 等 LeRobot 格式数据集 |

### 按底层模拟器分组

```text
MuJoCo 系：
LIBERO
LIBERO-plus
RoboCerebra
Meta-World
RoboCasa365
VLABench

SAPIEN 系：
RoboTwin 2.0
RoboMME（通过 ManiSkill）

NVIDIA Isaac Sim 系：
IsaacLab Arena
```

但“同属 MuJoCo”不代表数据或模型可以直接互换。LIBERO、Meta-World、RoboCasa 和 VLABench 仍然可能使用不同机器人、相机、state、action、任务定义和控制频率。

## 3. 每个 benchmark 是否有对应数据集

通常有，因为模仿学习和 VLA 微调需要专家 demonstrations。但 benchmark 与数据集不是严格的一一绑定关系。

例如 LIBERO 有两份 LeRobot 兼容数据：

```text
lerobot/libero
HuggingFaceVLA/libero
```

两者 demonstrations 和 schema 相同，主要区别是视频/图片存储方式。

一个外部数据集只要与目标 benchmark 在以下方面兼容，也可能用于训练：

- embodiment；
- 相机和 observation keys；
- state 维度、顺序和物理含义；
- action 维度、单位和相对/绝对控制方式；
- FPS 和 action horizon；
- 自然语言 task；
- normalization statistics。

评测阶段则是：

```text
加载训练好的 checkpoint
→ 启动 benchmark 模拟环境
→ 模型在线接收新 observation
→ 模型产生 action
→ 环境判断成功或失败
```

它不是简单地重放训练 dataset 中的某个 episode。

## 4. 写论文是否应挑同一模拟器下的几个数据集

答案是：**可以降低工程变量，但“同一 simulator”不是最重要的公平性条件，也不是所有论文都应该这样选。**

真正决定实验是否公平的是：

1. 不同方法是否使用相同训练数据、split 和 demonstrations；
2. 是否使用相同 benchmark 版本、task 和成功条件；
3. 是否使用相同 observation、action 表示和控制频率；
4. 是否使用相同 episode 数量、初始状态和随机种子；
5. 是否存在训练任务、测试任务或扰动泄漏；
6. 每个 baseline 是否得到合理且一致的调参预算。

仅仅都使用 MuJoCo，并不能保证公平。例如：

```text
LIBERO：Panda，7维动作，双相机
RoboCasa：移动 PandaOmron，12维动作，厨房大场景
Meta-World：Sawyer，不同任务接口
```

虽然底层都是 MuJoCo，它们之间的差异仍然很大。

## 5. 不同论文目标对应的选择方式

### 方案 A：研究 LIBERO-OOD 或视觉鲁棒性

最推荐使用：

```text
训练：lerobot/libero
ID评测：标准 LIBERO
OOD评测：LIBERO-plus
```

优点：

- LIBERO 和 LIBERO-plus 共享接近的 simulator stack；
- robot、state 和 action 接口基本一致；
- 主要变化集中在布局、相机、语言、光照、纹理和噪声；
- 更容易把性能变化归因于 OOD，而不是机器人或控制空间变化。

如果用 `lerobot/libero_plus` 训练后再测试 LIBERO-plus，就不再是纯 zero-shot OOD。必须建立严格的 perturbation/task/seed held-out split，并称为 OOD adaptation 或 robustness fine-tuning。

### 方案 B：研究长时序规划和记忆

可以考虑：

```text
LIBERO-Long
RoboCerebra
RoboMME
VLABench composite tasks
```

这些 benchmark 强调长时序、子目标或记忆，但 RoboMME 使用 SAPIEN/ManiSkill，不能把跨 benchmark 差异完全归因于规划能力。论文中应分别报告，而不是直接把成功率横向平均。

### 方案 C：研究跨环境/跨模拟器泛化

可以故意选择不同 simulator：

```text
MuJoCo：LIBERO 或 VLABench
SAPIEN：RoboTwin 或 RoboMME
Isaac Sim：IsaacLab Arena
```

这种设计能提供更广泛的外部有效性，但工程成本更高，而且模型必须适配不同 embodiment、action space 和依赖环境。

### 方案 D：比较多个 VLA 方法

如果论文重点是“方法 A 是否优于多个 baseline”，最稳妥的是先固定一个主 benchmark 和同一份训练数据：

```text
相同数据集
相同 train/test split
相同输入输出字段
相同 benchmark episodes
相同种子和评测次数
```

然后再增加第二个 benchmark 作为外部验证。不要一开始给每个模型选择不同数据集，再直接比较结果；否则数据质量和规模会成为严重混杂因素。

## 6. 对当前 LIBERO-OOD 研究的建议

如果你的核心问题是 VLA 在 OOD 条件下是否稳健，第一篇实验建议收窄为：

```text
主训练数据：lerobot/libero

ID测试：
LIBERO Spatial / Object / Goal / Long

OOD测试：
LIBERO-plus 的对象布局、相机、机器人初始状态、语言、光照、背景纹理、传感器噪声

模型：
选择 2–4 个能够使用同一 LIBERO schema 的 VLA
```

这样 robot embodiment、action space 和大部分任务语义保持一致，实验结论更容易解释。

在主实验完成后，再增加一个不同 simulator 的 benchmark，例如 RoboTwin 或 RoboMME，作为跨模拟器泛化补充，而不是一开始混在主表中。

## 7. 实验表格应该如何组织

对于 LIBERO/LIBERO-plus，可以使用：

| Model | Train data | LIBERO ID | Layout OOD | Camera OOD | Language OOD | Lighting OOD | Texture OOD | Noise OOD |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Model A | `lerobot/libero` | | | | | | | |
| Model B | `lerobot/libero` | | | | | | | |

要求所有方法使用：

- 同一数据 revision；
- 相同训练 episodes；
- 相同图像和 state/action schema；
- 相同 eval seeds；
- 相同每任务 episode 数；
- 至少报告均值，并尽量报告多随机种子的波动。

跨 simulator benchmark 应单独成表，因为其任务数量、动作空间、episode 长度和成功率难度不同，不应把不同 benchmark 的原始成功率直接混成一个没有解释的平均数。

## 8. 最终结论

```text
同一模拟器：减少物理引擎和渲染差异，适合控制变量实验；
同一 benchmark 和同一 dataset：比“同一模拟器”更重要；
不同模拟器：适合证明更广泛的泛化，但成本和混杂因素更高。
```

对当前 LIBERO-OOD 方向，最清晰的主线是：先使用同一 LIBERO simulator stack，标准 LIBERO 训练和 ID 测试，LIBERO-plus 做 OOD 测试；完成后再用 SAPIEN 或 Isaac Sim benchmark 做补充验证。
