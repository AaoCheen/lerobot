# LeRobot 初学者学习路线：从仿真到论文实验

这个目录面向一个明确目标：

~~~text
先理解 LeRobot
→ 在仿真 benchmark 中跑通 baseline
→ 做一个小而可验证的修改
→ 用公平实验验证提升
→ 整理成论文
~~~

本路线暂时不包含真实机器人、相机、电机和遥操作部署。重点放在：

- LeRobot 提供了哪些训练、微调和评测接口；
- VLA policy 如何接入；
- benchmark 和模拟环境如何工作；
- 如何扩展 policy、processor、benchmark 或实验 harness；
- 如何把一次代码改动变成可复现的论文实验。

## 推荐阅读顺序

1. [00_仓库地图与核心概念.md](./00_仓库地图与核心概念.md)
2. [01_先跑通仿真工作流.md](./01_先跑通仿真工作流.md)
3. [02_数据集与训练输入.md](./02_数据集与训练输入.md)
4. [03_Policy与VLA.md](./03_Policy与VLA.md)
5. [04_训练微调与评测接口.md](./04_训练微调与评测接口.md)
6. [05_Benchmark与模拟环境.md](./05_Benchmark与模拟环境.md)
7. [06_扩展点与Harness方向.md](./06_扩展点与Harness方向.md)
8. [07_论文实验路线.md](./07_论文实验路线.md)
9. [08_Docker与环境管理.md](./08_Docker与环境管理.md)

已有的细节笔记：

- [LeRobotDataset 数据格式](../lerobot_dataset_research/README.md)
- [LeRobot 仓库能力与模型总览](../lerobot_repo_research/README.md)
- [Benchmark、模拟器与训练集关系](../lerobot_repo_research/benchmark.md)

## 先记住三个层次

~~~text
Dataset       训练时给模型看的 demonstrations
Policy        根据 observation 预测 action 的模型
Benchmark     评测模型能否在环境中完成任务
~~~

~~~text
lerobot-train  → 训练/微调
lerobot-eval   → 仿真 benchmark 评测
LeRobotDataset → 读取训练数据
Processor      → 对齐 observation、action 和 policy 输入
~~~

## 本目录的实验原则

- 先固定一个 benchmark 和一个数据集，再改代码；
- 先跑通原始 baseline，再做改动；
- 一次只改变一个主要因素；
- 记录代码 commit、数据 revision、模型 checkpoint、随机种子和评测 episodes；
- 不把训练集上的 loss 下降直接当作 benchmark 成功率提升；
- 不把不同 embodiment 或不同 action space 的结果直接横向比较。

