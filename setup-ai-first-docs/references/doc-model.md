# 文档模型

`setup-ai-first-docs` 的参考规则：决定一个事实该放在哪个文件、何时更新、何时归档。SKILL.md 负责流程，本文件负责放置与生命周期。

## 1. 所有权矩阵

| 信息 | 唯一所有者 | 其他位置只放 |
|---|---|---|
| 项目身份、会话开始顺序、文件索引、硬约束、边界 | `AGENTS.md` | — |
| 文档地图、所有权、生命周期、更新触发器、命名、写作规则 | `docs/README.md` | `AGENTS.md` 一行指针 |
| 项目级规格：项目是什么、技术栈、目录结构、具体命令、代码风格、测试策略、边界、成功标准、开放问题 | `docs/spec.md` | `AGENTS.md` 指向章节 |
| 系统结构：模块、职责、依赖方向、关键流程、数据架构、接口边界、非功能设计 | `docs/HLD.md` | `spec.md` 只链接，不复制 |
| 演进账本：已开工/已完成 feature 的时间、文件索引、简介、状态 | `docs/roadmap.md` | `status.md` 不复制历史 |
| 当前功能地图：状态、下一步、负责人 | `docs/features/status.md` | `roadmap.md` 记录时间线 |
| 单个 feature 的决策（图优先）：目标、范围、模块依赖、核心接口、关键机制、数据对象、验收标准、取舍 | `docs/features/feature-<slug>/plan.md` | `roadmap.md`、`status.md` 一行摘要 |
| 单个 feature 的执行规格：编号行为、接口细节、验收映射 | `.scratch/feature-<slug>-spec.md` | plan 不复制执行细节 |
| 单个工单：职责、验收、证据；格式由用户决定 | `.scratch/tickets/` | feature spec 只做验收指向 |
| 可复制的空模板 | `docs/templates/` | — |

规则：写任何内容前先问“这件事的唯一所有者是谁”。如果答案是两个，先拆职责，再写。

## 2. 单一事实源

- **项目定义与工程契约**（是什么、用什么、怎么建/跑/测、边界、如何算完成）→ `spec.md` 的 `Objective`、`Tech Stack`、`Project Structure`、`Commands`、`Code Style`、`Testing Strategy`、`Boundaries`、`Success Criteria`、`Open Questions`。
- **单功能行为**（一个功能具体做什么）→ `plan.md`；执行规格 → feature spec。
- **结构**（系统由什么组成、如何协作）→ `HLD.md` 的模块、流程、数据架构。
- **时间线**（何时开始、何时完成）→ `roadmap.md`。
- **当前状态**（现在在哪一步）→ `status.md`。
- **为什么这样做**（单个功能的取舍）→ `plan.md`。
- **怎么一步步做**（执行细节）→ `.scratch/`。

指针写法：`docs/spec.md > Boundaries`、`docs/HLD.md §4.1 登录流程`。指针要带章节和阅读理由，例如“改登录前读，确认 token 续期约束”，不要只写“见 spec”。

禁止的复制：

- plan 不复制 spec 的项目级约束，只引用章节。
- feature spec 不复制 plan 的决策，只引用并展开为可执行规格。
- status 不复制 plan 的内容，只放一行摘要和链接。
- AGENTS 不复制 spec/HLD 的正文。

## 3. Feature 生命周期

| 状态 | 进入条件 | 必须存在 | 退出门禁 |
|---|---|---|---|
| `planned` | 需求被记录、slug 确定 | `plan.md` 草稿；status 一行 | 人批准 plan（范围与验收标准冻结） |
| `in-progress` | plan 已批准、工单规划已确认 | `.scratch/<feature>-spec.md`；`tickets/` 至少三张独立工单（验收/代码提交/文档更新）；代码与测试；roadmap 一行 | 实现完成，三张独立工单完成，AC 通过 |
| `done` | 所有 AC 通过、证据齐全 | 验收证据；代码 commit；文档 commit；`spec.md` 的项目级变化已同步 / `HLD.md` 的结构变化已同步 | 归档评审通过 |
| `archived` | 功能已验收且不再改动 | 目录冻结；roadmap 与 status 均标 `archived` | — |

门禁：

- 没有批准 plan，不填 feature spec（骨架可先存在）、不规划工单、不改代码。
- 工单规划未经人确认，不开始实现；每个 feature 至少三张独立工单：验收、代码提交、文档更新。
- 实现工单只改代码、不做最终提交；最终代码提交与文档更新分别由独立工单完成。
- 验收标准未全部通过，不标 `done`；三张收尾工单未完成，不标 `done`。
- `spec.md` / `HLD.md` 未同步，不归档。
- 不允许跳级；`planned` 不能直接到 `done`。

Bug 与 hotfix 也使用 `feature-<slug>` 目录，在 `plan.md` 顶部标 `类型: bugfix | hotfix`；实现工单可以只有一张，但验收、代码提交、文档更新三张独立工单不能省略。

## 4. 更新触发器

| 事件 | 必须更新 |
|---|---|
| 提出新功能 | `status.md` 加一行（`planned`）；建 `plan.md`；此时不进 roadmap |
| plan 批准 | `plan.md` 记录批准日期；`status.md` 进入 `in-progress`；`roadmap.md` 加行（`in-progress`） |
| 工单进展 | 按用户规划更新；验收、代码提交、文档更新三张独立工单完成时更新 `status.md` |
| 实现完成 | 工单证据；验收命令输出；`status.md` 备注 |
| 验收通过 | `spec.md`（项目级目标/成功标准；功能行为回写 `plan.md`）；`HLD.md`（结构变化时）；`roadmap.md` 与 `status.md` 标 `done` |
| 归档 | `status.md` 与 `roadmap.md` 标 `archived`；feature 目录冻结 |
| 架构决策变化 | `HLD.md` 的“技术选型与约束”或“变更记录”；相关 plan 链接 |
| 项目级目标/范围变化 | `spec.md` 的 `Objective` / `Success Criteria`；功能行为变化回写 `plan.md` |
| 命令/环境变化 | `spec.md` 的 `Commands`，重新验证并更新 `Verified` 状态 |
| 文档规则变化 | `docs/README.md`；必要时 `AGENTS.md` 的指针 |

每次更新同时刷新文件顶部的“最后校准/最后更新”日期；历史记录只追加，不改写。

## 5. `.scratch/` 规则

`.scratch/` 是 AI-native 的本地工作区，默认被 `.gitignore` 排除：

```gitignore
docs/features/*/.scratch/
```

内容：

```text
docs/features/feature-<slug>/.scratch/
├── feature-<slug>-spec.md   # 从 plan + spec + HLD 派生的执行规格
├── tickets/                 # 工单（格式由用户决定；至少三张独立收尾工单）
└── notes/                   # 可选：临时调查、日志、草稿
```

规则：

- **可丢弃**：删除 `.scratch/` 后，仅凭 `plan.md` + `spec.md` + `HLD.md` 应能重建执行计划。不能重建，说明 plan 缺信息。
- **非决策地**：feature spec 和工单里发现的新决策，先回写 `plan.md` 并获得确认；不得只留在 scratch。
- **不提交**：任何 `.scratch/` 文件都不进 Git；提交前用 `git status` 与 `git check-ignore` 双重确认。
- **不互链**：committed 文档（AGENTS、README、plan、roadmap、status）不写指向 `.scratch/` 内部文件的 Markdown 链接；只描述“本地工作区”这一事实。
- **不放密钥**：即使是本地文件，也不写 token、密码、真实用户数据。
- **团队共享走 plan/PR**：需要他人看到的结论，提升到 `plan.md` 或代码评审说明，不靠 scratch 传递。

## 6. 命名

| 对象 | 规则 | 示例 |
|---|---|---|
| Feature 目录 | `feature-<kebab-slug>`；slug 2–5 个英文词 | `feature-user-login` |
| Feature spec | 与目录同名 + `-spec.md` | `.scratch/feature-user-login-spec.md` |
| 工单 | 格式、命名、数量由用户决定；至少三张独立工单（验收 / 代码提交 / 文档更新） | `.scratch/tickets/` |
| 模板 | 与目标文件同名，放 `docs/templates/` | `docs/templates/plan.md` |
| 日期 | ISO `YYYY-MM-DD` | `2026-05-01` |
| 功能状态 | `planned \| in-progress \| done \| archived` | `in-progress` |
| Roadmap 状态 | `in-progress \| done \| archived`（`planned` 只留在 status） | `in-progress` |

ID 与目录名创建后不变；需要改 slug 时新建目录并在 roadmap 记录迁移，不原地重命名历史。若项目沿用 `feature-xxxA` 形式，把 `<slug>` 视为该 ID，目录与 spec 保持同名即可。

## 7. 上下文预算

超出预算时按模块或功能拆分，并在原文件保留索引；不要把所有内容塞进一个文件。

| 文件 | 目标 | 硬上限 | 超限处理 |
|---|---|---|---|
| `AGENTS.md` | 40–100 行 | 120 行 | 事实下沉 spec/HLD，流程下沉 docs/README |
| `docs/README.md` | ≤ 200 行 | 300 行 | 拆 `docs/README/` 子文档并保留索引 |
| `docs/spec.md` | ≤ 400 行 | 500 行 | 拆 `docs/spec/`，`spec.md` 做索引 |
| `docs/HLD.md` | ≤ 300 行 | 400 行 | 按模块拆 `docs/hld/`，保留总览与索引 |
| `docs/roadmap.md` | ≤ 200 行 | 300 行 | 按年份分表 |
| `docs/features/status.md` | ≤ 50 行 | 80 行 | 只保留活动功能；归档功能移入“已归档”索引表 |
| `plan.md` | ≤ 300 行 | 400 行 | 图优先；超过 7 个节点/10 条消息拆图或改文字；完整接口/字段移 `.scratch` |
| feature spec | ≤ 200 行 | 300 行 | 按能力分节或拆文件 |

工单不设行数预算；格式与粒度由用户决定，但每个 feature 至少三张独立工单。

## 8. 迁移已有仓库

1. **盘点**：列出每个现有文档、它当前回答的问题、最后更新时间、是否仍准确。
2. **分类**：项目定义与工程契约（目标、技术栈、结构、命令、风格、测试、边界）→ spec；单功能方案/行为 → plan；结构细节 → HLD；时间线 → roadmap；流程规则 → docs/README；执行细节 → scratch（可不迁移，留在原处并标注历史）。
3. **给方案**：逐文件写“保留 / 合并 / 移动 / 暂不动”，等用户确认；不直接删除。
4. **保权威**：同一事实有多份时，选最新且最准确的一份作为所有者，其余改为指针；冲突写 Open Questions。
5. **保历史**：旧路线图、已完成计划只追加到 roadmap 或在旧文件顶部标 `Superseded by ...`，不改写历史结论。
6. **保命名**：现有 feature 编号、工单格式、状态值能映射就映射；不能映射时保留原值并加说明，不强行统一。

## 9. 反模式

- `AGENTS.md` 变成百科：每次会话都加载的长文档会稀释真正重要的规则。
- `spec.md` 写路线图、历史决策或 feature 实现步骤：它只描述项目级事实与工程契约。
- `HLD.md` 按文件罗列代码：它描述模块边界与机制，不描述目录树。
- `plan.md` 写“使用某 SDK 实现”：没有模块、符号、输入输出，等于没设计。
- 把验收、代码提交、文档更新合并成一张工单：三张必须独立。
- 状态出现在三个地方且各自维护：只允许 roadmap（时间线）与 status（看板）两处，且必须一致。
- 把 `.scratch/` 当协作文档：他人克隆后不存在，结论必然丢失。
- 模板占位符未替换就交付：agent 会把 `[ ]` 当成真实需求。
- 文档没有所有者与更新触发器：下一个人不知道何时该改，最终变成沉积层。

## 10. 验收清单

机检（`scripts/verify_docs.py`）：

- 必需文件与 8 个模板齐全。
- `AGENTS.md` 行数达标，且包含五个核心指针。
- spec / HLD / README / plan / feature spec 的必需章节存在。
- roadmap 四列、日期格式、状态值合法（仅 `in-progress | done | archived`），链接可解析。
- status 覆盖所有 feature 目录；roadmap 中出现的功能状态必须与 status 一致（`planned` 可只在 status）。
- 每个 feature 至少三张独立工单（验收 / 代码提交 / 文档更新）；脚本仅在工单文件少于 3 个时提示。
- 无未替换的 `{{...}}`（模板目录除外）。
- `.scratch/` 未被 Git 跟踪，`.gitignore` 规则存在。

人工检查：事实准确性、日期真实性、接口粒度、数据对象生命周期、以及“删掉 scratch 能否重建计划”。
