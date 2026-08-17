# 03｜Policy 与 VLA

## 1. Policy 是什么

policy 是一个函数：

~~~text
observation + task
→ action
~~~

在 LeRobot 中，policy 通常负责：

- 编码图像；
- 编码 state；
- 编码 task/language；
- 预测一个 action 或 action chunk；
- 训练时计算 loss；
- 推理时输出可执行动作。

## 2. VLA 和普通 policy 的区别

~~~text
ACT / Diffusion
通常是视觉或状态到动作，任务条件可能较弱或另行编码。

VLA
通常把视觉、语言和动作放在同一套策略中，
输入图像 + 自然语言 task + state，输出动作。
~~~

当前仓库中可重点研究：

~~~text
SmolVLA   入门和微调最直接
Pi0       大型 VLA
Pi05      Pi 系列后续版本
MolmoAct2 VLM + action expert
VLA-JEPA 视觉表征和动作建模
GR00T     多 embodiment 基础模型
EVO1      分阶段训练的 VLA
X-VLA     跨 embodiment 方向
FastWAM   World Action Model
~~~

传统或非典型 VLA policy 包括：

~~~text
ACT、Diffusion、VQ-BeT、TD-MPC、Gaussian Actor、Multi-task DiT
~~~

## 3. 微调命令长什么样

SmolVLA 示例：

~~~bash
lerobot-train \
  --policy.path=lerobot/smolvla_base \
  --dataset.repo_id=<训练数据集> \
  --batch_size=64 \
  --steps=20000 \
  --output_dir=outputs/train/my_smolvla \
  --policy.device=cuda
~~~

Pi0/Pi05 等模型的参数可能使用：

~~~text
--policy.type
--policy.path
--policy.pretrained_path
--policy.freeze_vision_encoder
--policy.train_expert_only
--policy.dtype
~~~

不同模型不能机械复制命令。先读对应：

~~~text
docs/source/smolvla.mdx
docs/source/pi0.mdx
docs/source/pi05.mdx
docs/source/molmoact2.mdx
docs/source/groot.mdx
~~~

## 4. 一个 VLA 能否直接用于任何 benchmark

不能默认可以。必须对齐：

- embodiment；
- 相机数量和名字；
- observation.state；
- action space；
- relative/absolute action；
- task 字段；
- processor；
- normalization。

## 5. 如何开始做一个小改动

先不要改大模型。可以按风险从低到高：

~~~text
输入增强或图像 transform
→ processor 中增加一个可开关步骤
→ action chunk / temporal window 实验
→ loss 或采样策略改动
→ policy 内部结构改动
~~~

每次只改一个因素，并保留未改动 baseline。

