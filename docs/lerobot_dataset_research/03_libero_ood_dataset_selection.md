# LIBERO-OOD 后训练数据集选择

## 先定义你说的 OOD

“LIBERO-OOD”至少可能指两种实验，训练集选择不能混在一起：

1. **Vanilla LIBERO → LIBERO-plus 零样本 OOD**：只用标准 LIBERO demonstrations 后训练，然后直接在 LIBERO-plus 的相机、布局、光照、纹理、语言、初始状态和传感器噪声扰动上评测。此时不能用 `lerobot/libero_plus` 训练，否则不再是零样本 OOD。
2. **面向 OOD 的适应/鲁棒后训练**：允许使用 LIBERO-plus demonstrations 后训练，再在保留的 perturbation、task 或 seed 上评测。此时必须明确拆分，避免训练和测试变体泄漏。

如果暂时没有固定协议，建议先做第 1 种，它更容易解释，也能与标准 LIBERO 成功率同时报告。

## 推荐候选

### A. 首选：标准 LIBERO 全四套

#### `lerobot/libero`

Hub：<https://huggingface.co/datasets/lerobot/libero>

当前 LeRobot 文档的首选训练集：

- LeRobot v3.0；
- 1,693 episodes、273,465 frames、40 tasks；
- 10 FPS；
- `observation.state`: `[8]`；
- `action`: `[7]`；
- 两路图像：读取后 `[3, 256, 256]`；
- MP4 存储，下载约 1.9 GB。

适用：在 Spatial/Object/Goal/Long 全部 demonstrations 上后训练，再做标准 LIBERO 或 LIBERO-plus OOD 评测。

这是最适合先看形状、跑通加载和建立 baseline 的选择。

#### `HuggingFaceVLA/libero`

Hub：<https://huggingface.co/datasets/HuggingFaceVLA/libero>

它与上面的 demonstrations 和 schema 相同，但相机图像以 PNG 存在 Parquet 中：

- LeRobot v3.0；
- 1,693 episodes、273,465 frames、40 tasks；
- 10 FPS；
- 图像 `[256, 256, 3]`、state `[8]`、action `[7]`；
- 下载约 69.9 GB。

适用：不能安装视频解码依赖，或必须研究无视频重编码图像时。通常不建议把它作为第一份下载，因为它比 `lerobot/libero` 大约 37 倍。

### B. 真正的扰动数据：LIBERO-plus

#### `lerobot/libero_plus`

Hub：<https://huggingface.co/datasets/lerobot/libero_plus>

当前 Hub 元数据显示：

- LeRobot v3.0；
- 14,347 episodes、2,238,036 frames、40 tasks；
- 20 FPS；
- `observation.state`: `[8]`；
- `action`: `[7]`；
- `observation.images.front` 和 `observation.images.wrist`: `[256, 256, 3]`。

它覆盖 objects layout、camera viewpoint、robot initial state、language、lighting、background texture 和 sensor noise 等扰动。

适用：OOD adaptation、鲁棒后训练或 held-out perturbation 实验。若用它训练，就应按 perturbation/task/seed 明确划分训练和测试，不能再称为对整个 LIBERO-plus 的零样本 OOD。

注意它与 `lerobot/libero` 不只数据量不同：FPS 为 20 vs 10，相机 key 也不同。混合训练前需要对齐 key、采样频率、action horizon 和 normalization。

### C. 分 suite / no-op 清理版本

IPEC-COMMUNITY collection：<https://huggingface.co/collections/IPEC-COMMUNITY/libero-benchmark-dataset>

- `IPEC-COMMUNITY/libero_spatial_no_noops_1.0.0_lerobot`
- `IPEC-COMMUNITY/libero_object_no_noops_1.0.0_lerobot`
- `IPEC-COMMUNITY/libero_goal_no_noops_1.0.0_lerobot`
- `IPEC-COMMUNITY/libero_10_no_noops_1.0.0_lerobot`
- `IPEC-COMMUNITY/libero_90_no_noops_lerobot`

适用：只后训练一个 suite、复现 GR00T 的 suite-wise recipe，或研究 LIBERO-90 → held-out suite 的迁移。

风险：至少抽查到的 Spatial 仓库 `codebase_version` 是 `v2.1`，而当前 checkout 的 `LeRobotDataset` 以 v3.0 为主。下载前逐个查看 `meta/info.json`，必要时使用 v3.0 镜像或先转换。不能仅凭仓库名包含 `lerobot` 就假定能被当前代码直接加载。

## 推荐的第一轮实验矩阵

| 实验 | 后训练数据 | 测试 | 能回答的问题 |
|---|---|---|---|
| ID baseline | `lerobot/libero` | vanilla LIBERO 四套 | 当前模型是否学会任务 |
| zero-shot OOD | `lerobot/libero` | LIBERO-plus 全扰动 | 标准后训练后的自然鲁棒性 |
| OOD adaptation | `lerobot/libero` + LIBERO-plus train split | LIBERO-plus held-out split | 扰动数据后训练是否提升泛化 |
| transfer | LIBERO-90 no-noops | Spatial/Object/Goal/Long | 跨任务/知识迁移能力 |

不要把 standard LIBERO 四套训练数据与同一套 standard test 成功率叫作 OOD；这更接近 demonstration-conditioned benchmark evaluation。OOD 必须说明到底 hold out 了 task、视觉扰动、语言表达、布局还是其他因素。

## 先在 Hub 看形状

浏览器直接打开各数据集的 `meta/info.json`，重点比较：

```text
codebase_version
fps
total_episodes / total_frames / total_tasks
features.*.dtype
features.*.shape
features 中的相机 key
```

也可从 `repos/lerobot` 执行：

```bash
for DATASET_ID in \
  lerobot/libero \
  HuggingFaceVLA/libero \
  lerobot/libero_plus
do
  echo "===== ${DATASET_ID} ====="
  curl -sL "https://huggingface.co/datasets/${DATASET_ID}/resolve/main/meta/info.json" \
    | jq '{codebase_version, fps, robot_type, total_episodes, total_frames, total_tasks,
           features: (.features | with_entries(.value |= {dtype, shape, names}))}'
done
```

接着只加载元数据：

```bash
uv run python - <<'PY'
from lerobot.datasets import LeRobotDatasetMetadata

for repo_id in ["lerobot/libero", "HuggingFaceVLA/libero", "lerobot/libero_plus"]:
    meta = LeRobotDatasetMetadata(repo_id)
    print("\n", repo_id)
    print("version:", meta.info["codebase_version"])
    print("fps:", meta.fps)
    print("episodes / frames:", meta.total_episodes, meta.total_frames)
    print("camera_keys:", meta.camera_keys)
    for key, feature in meta.features.items():
        print(key, feature.get("dtype"), feature.get("shape"))
PY
```

## 当前建议

第一步用 `lerobot/libero` 后训练并建立 vanilla LIBERO baseline；第二步不再训练，直接评测 LIBERO-plus，得到 zero-shot OOD 结果。确认失效维度后，再决定是否从 `lerobot/libero_plus` 构造严格的 held-out split 做 OOD adaptation。
