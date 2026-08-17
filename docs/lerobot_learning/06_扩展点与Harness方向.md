# 06｜扩展点与 Harness 方向

## 1. LeRobot 可以扩展什么

### Dataset

可以新增数据集或转换外部数据：

~~~text
外部 HDF5 / RLDS / 视频
→ 转成 LeRobotDataset
→ 使用统一训练入口
~~~

相关位置：

~~~text
src/lerobot/datasets/
examples/port_datasets/
docs/source/porting_datasets_v3.mdx
~~~

### Processor

适合处理：

- observation key 重命名；
- state/action 转换；
- normalization；
- 时间窗口；
- task 文本；
- 环境和 policy 之间的适配。

相关位置：

~~~text
src/lerobot/processor/
docs/source/implement_your_own_processor.mdx
docs/source/adding_benchmarks.mdx
~~~

### Policy

新 policy 通常需要：

- 配置类；
- policy 实现；
- 注册 policy type；
- 输入输出 feature 定义；
- processor；
- checkpoint 加载逻辑；
- 单元测试和文档。

相关位置：

~~~text
src/lerobot/policies/<new_policy>/
src/lerobot/configs/policies.py
docs/source/bring_your_own_policies.mdx
~~~

### Benchmark / Environment

新增 benchmark 通常需要：

~~~text
src/lerobot/envs/<benchmark>.py
src/lerobot/envs/configs.py
src/lerobot/processor/env_processor.py（如需要）
pyproject.toml 依赖
docs/source/<benchmark>.mdx
docs/source/_toctree.yml
tests/
~~~

官方教程：

~~~text
docs/source/adding_benchmarks.mdx
~~~

### Harness

你的 VLA-as-tool 想法可以放在 LeRobot 外部：

~~~text
harness
├── policy adapter
├── observation adapter
├── action executor
├── benchmark runner
├── trace/logger
└── evaluator
~~~

第一版只做 Python wrapper：

~~~text
observation + task
→ policy.select_action
→ action chunk
→ env.step
→ trace
~~~

这样可以和官方 lerobot-eval 结果做对照，也不会一开始改动核心训练代码。

## 2. 推荐的扩展顺序

~~~text
外部 harness
→ processor 小改动
→ benchmark wrapper
→ 新 policy
→ 修改训练目标或模型结构
~~~

## 3. 改动前先回答

~~~text
我要改变输入、动作、推理频率、训练目标还是评测方式？
改动属于 dataset、processor、policy、env 还是 harness？
是否能在不改其他模块的情况下做 ablation？
是否能保留原始 baseline？
~~~

