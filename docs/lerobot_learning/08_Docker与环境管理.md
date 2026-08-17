# 08｜Docker 与环境管理

## 1. Docker 是什么角色

Docker 不是 LeRobot 必须使用的训练接口，而是隔离依赖环境的一种方式。

它可以固定：

~~~text
Ubuntu / CUDA / Python
PyTorch
MuJoCo / SAPIEN / Isaac Sim
LeRobot
benchmark 依赖
~~~

## 2. 仓库里有什么

~~~text
docker/Dockerfile.user
docker/Dockerfile.internal
docker/Dockerfile.benchmark.libero
docker/Dockerfile.benchmark.libero_plus
docker/Dockerfile.benchmark.metaworld
docker/Dockerfile.benchmark.robocasa
docker/Dockerfile.benchmark.robotwin
docker/Dockerfile.benchmark.robomme
docker/Dockerfile.benchmark.vlabench
~~~

先阅读目标 benchmark 对应的 Dockerfile，不要把所有 benchmark 依赖混在一个 Conda 环境。

## 3. 什么时候值得使用 Docker

适合：

- benchmark 依赖互相冲突；
- 需要固定 CUDA/PyTorch 版本；
- 论文需要别人复现实验；
- 运行 Isaac Sim、SAPIEN 等重量级环境；
- 想把训练和评测环境隔离。

初学时可以先使用仓库推荐的 uv 环境跑通 LIBERO，再决定是否切 Docker。

## 4. 论文中的环境记录

无论使用 Conda、uv 还是 Docker，都记录：

~~~text
系统版本
GPU和驱动
CUDA
Python
LeRobot commit
benchmark commit
依赖锁文件
数据 revision
~~~

Docker 镜像最好固定 tag 或 digest，不要论文中只写 latest。

