# 05｜Benchmark 与模拟环境

详细表格见：

- [Benchmark、模拟器与训练数据集](../lerobot_repo_research/benchmark.md)

## 1. 当前主要 benchmark

~~~text
LIBERO / LIBERO-plus
Meta-World
RoboCasa365
RoboTwin 2.0
RoboMME
VLABench
RoboCerebra
IsaacLab Arena
~~~

## 2. 底层模拟器分组

~~~text
MuJoCo：LIBERO、LIBERO-plus、RoboCerebra、Meta-World、RoboCasa、VLABench
SAPIEN：RoboTwin、RoboMME（ManiSkill）
Isaac Sim：IsaacLab Arena
~~~

同一底层模拟器不代表相同 benchmark。机器人、相机、action space、任务和成功判定仍可能不同。

## 3. LIBERO-OOD 推荐主线

~~~text
训练：lerobot/libero
ID测试：标准 LIBERO
OOD测试：LIBERO-plus
~~~

这条主线能尽量固定 embodiment、state/action 和任务语义，把主要差异放在布局、相机、语言、光照、纹理和噪声。

如果训练使用 lerobot/libero_plus，再在相同扰动上测试，就不能称为纯 zero-shot OOD；需要严格 held-out split。

## 4. 评测协议

正式比较时固定：

- benchmark 版本；
- task 列表；
- 每个 task 的 episodes；
- 随机种子；
- reset 方式；
- control mode；
- n_action_steps；
- 模型和数据 revision。

不要只报告一个混合平均 success rate，要保留每个 suite/task 的结果。

