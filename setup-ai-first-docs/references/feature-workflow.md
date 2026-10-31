# Feature 工作流

本文件是 `setup-ai-first-docs` 的可选分支：搭建完文档系统后，如何创建并推进一个 feature。项目应把同样的规则写进自己的 `docs/README.md`，后续不依赖本 skill 也能执行。

## 1. 创建 feature

前置：需求已和用户讨论过，slug 已确定。

```bash
python <skill-dir>/scripts/scaffold_docs.py <project-root> --feature <slug>
```

产物：

```text
docs/features/feature-<slug>/
├── plan.md
└── .scratch/
    ├── feature-<slug>-spec.md   # 空模板，plan 批准后再填
    └── tickets/                 # 空目录，工单由用户自由规划
```

同时手工更新：

- `docs/features/status.md` 加一行：`| feature-<slug> | 一句话简介 | planned | [plan](feature-<slug>/plan.md) | 负责人 | 写 plan | YYYY-MM-DD |`
- **暂不加 roadmap**：plan 批准、进入实现时再加（`in-progress`）。

规则：

- 一个 feature 一个目录；目录名创建后不变。
- 没有真实需求不建目录；不要用示例功能占位。
- `plan.md` 先写，`.scratch/` 后填；顺序不能反。

## 2. 写 plan 并批准

`plan.md` 必须覆盖：背景与目标、范围、方案总览图、模块依赖图、核心接口（SDK/模块/符号级）、关键机制时序图或顺序分点、数据对象图与生命周期、失败模式、验收标准、取舍。默认图优先；完整接口/字段/错误码放 `.scratch`。写法见 [`ai-first-writing.md`](ai-first-writing.md) §3。

批准门禁：

- 人确认范围、验收标准、核心接口、数据对象设计。
- 记录批准日期与批准人；此后 AC 变更需要重新批准。
- plan 未批准：不填 feature spec、不规划工单、不改代码。
- plan 批准后：status 改 `in-progress`，在 `docs/roadmap.md` 加一行（`| YYYY-MM-DD | [feature-<slug>](features/feature-<slug>/plan.md) | 一句话简介 | in-progress |`）。

## 3. 写 feature spec

plan 批准后，用 `docs/templates/feature-spec.md` 填 `.scratch/feature-<slug>-spec.md`。

- 头部写来源：plan、`docs/spec.md` 章节、`docs/HLD.md` 章节。
- 项目级约束只放指针，不复制。
- 行为规格编号 `FR-001` 起，写 Given / When / Then、边界、错误。
- 每条 `AC-*` 必须能指向验收工单或验收说明。
- 不引入 plan 中没有的决策；发现缺口回 plan 补，再继续。

## 4. 规划工单

本 skill **不规定工单格式、命名、字段或状态值**；工单由用户自由规划创建，统一放在 `.scratch/tickets/`。

每个 feature 至少包含三张**独立**工单，不得合并：

| 工单 | 只负责 | 不包含 |
|---|---|---|
| 验收工单 | 按 `plan.md` 的 AC 执行验收，记录证据与结论 | 实现代码、提交代码、更新长期文档 |
| 代码提交工单 | 将本 feature 的代码改动提交到代码仓库，记录 commit | 文档更新 |
| 文档更新工单 | 同步 `spec.md` / `HLD.md` / `roadmap.md` / `status.md` / `plan.md`，并提交文档 | 代码改动 |

- 实现工单：数量、命名、格式、状态字段全部由用户决定；本 skill 不提供模板。
- 实现工单只改代码，不做最终提交；最终代码提交统一由代码提交工单完成。长期文档改动统一由文档更新工单完成。
- 推荐顺序：实现 → 验收 → 代码提交 → 文档更新；依赖可按项目调整，但三张收尾工单必须独立。
- 多代码仓库时，每个仓库一张代码提交工单。
- 工单可以合并实现内容，但不能把“验收 / 代码提交 / 文档更新”合并成一张。

## 5. 执行

- 按用户规划的工单执行；一次一张，不并行改多个工单。
- 实现工单完成后再进入收尾流程，按顺序执行验收、代码提交、文档更新三张工单。
- 验收工单记录：命令、输出、结论、日期；不修改实现代码。
- 代码提交工单记录：commit hash、提交范围、分支；不夹带文档改动。
- 文档更新工单记录：文档 commit hash、更新了哪些文档；不夹带代码改动。
- `.scratch/` 永远不提交；提交前用 `git status` 与 `git check-ignore` 确认。
- 实现中发现新决策：先回写 `plan.md` 并请用户确认；plan 变更影响 AC 时重新批准。
- 实现中发现文档错误：在文档更新工单中修正 `spec.md` / `HLD.md`，不要绕过。

阻塞处理：

- 缺信息：在对应工单或 `status.md` 的“下一步/阻塞”中写清缺什么、找谁；不要猜。
- 范围膨胀：新增实现工单，不改原工单的验收标准。

## 6. 验收与收尾

实现完成后：

1. **验收工单**：逐条运行 `plan.md` 的 AC，记录命令、输出、日期与结论。
2. **代码提交工单**：提交代码；确认提交范围只含代码与必要配置，不含文档改动；记录 commit hash。
3. **文档更新工单**：若 feature 改变了项目级目标、技术栈、目录结构、命令、代码风格、测试策略或边界，更新 `docs/spec.md` 对应章节；更新 `docs/HLD.md`（结构变化时）、`docs/roadmap.md`、`docs/features/status.md` 与必要时的 `plan.md`；提交文档并记录 commit hash。
4. 把 feature 中需要长期保留的决策从 `.scratch/` 回写到 plan/spec/HLD；确认删除 `.scratch/` 后仍能重建执行计划。
5. 确认三张工单都有结果后，status 与 roadmap 标 `done`。

验收通过后，`plan.md` 冻结；后续修改新建 feature，不原地改写历史结论。

## 7. 归档

默认**不移动目录**：把 `status` 与 roadmap 改为 `archived`，目录冻结，保留在原位。这样链接不失效，历史仍可查。

如果团队需要冷存储，可移到 `docs/features/archive/feature-<slug>/`，但必须同时更新：

- `roadmap.md` 的文档索引；
- `status.md` 的 plan 链接；
- 所有指向该目录的 committed 链接。

归档前门禁：验收、代码提交、文档更新三张工单完成，AC 证据齐全，`spec.md` / `HLD.md` 已同步，工作区干净。

## 8. 状态流转速查

| 从 | 到 | 触发 | 必须更新 |
|---|---|---|---|
| — | `planned` | 需求确认、目录创建 | plan 草稿、status |
| `planned` | `in-progress` | plan 批准 + 工单规划确认 | plan 批准记录、status、roadmap 加行 |
| `in-progress` | `done` | 实现完成 + 验收通过 + 代码提交 + 文档更新 | spec/HLD、status、roadmap、三张工单结果 |
| `done` | `archived` | 归档评审通过 | status、roadmap |

feature 状态没有 `blocked`；阻塞记在具体工单与 `status.md` 的“下一步/阻塞”列。
