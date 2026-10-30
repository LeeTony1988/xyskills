# 文档模型

本文件是 `init-ai-first-project` 的参考规则：初始化时用它决定每个文件该写什么、何时更新、何时归档。生成项目中的 feature 落地说明是 `docs/features/README.md`，工单落地规则是 `docs/issue-tracker.md`；本文件的 §2、§3 的 feature 行、§4 的 feature/工单命名、§7 与 §11 由它们承载。

## 1. 所有权矩阵

| 信息 | 唯一所有者 | 其他位置只放 |
|---|---|---|
| 项目身份、文件索引、常驻规则、边界 | `AGENTS.md` | — |
| 技术栈、目录、架构、命令、风格、测试、配置、约束、项目级成功标准 | `docs/spec.md` | `AGENTS.md` 指针 |
| 项目演进账本：基线、需求队列、依赖、状态、归档索引 | `docs/plan-map.md` | `status.md` 只放当前项 |
| 当前焦点、下一步、阻塞 | `docs/status.md` | — |
| 决策理由与后果 | `docs/adr/NNNN-*.md` | spec 的链接 |
| 单个 feature 的需求、方案、AC | `docs/features/F-NNN-slug/plan.md` | plan-map 一行摘要 |
| feature 目录结构、生命周期、门禁、DoD、bug/hotfix 规则 | `docs/features/README.md` | `AGENTS.md`、`docs/README.md` 一行指针 |
| 工单地图：工单列表、依赖、状态、覆盖 AC、提交 | `docs/features/F-NNN-slug/tickets.md` | `status.md` 的 next action |
| 单个工单的交付内容、阻塞、状态与 AC | `docs/features/F-NNN-slug/tickets/NN-<slug>.md` | tickets.md 一行索引 |
| 验收证据（按工单） | `docs/features/F-NNN-slug/acceptance.md` | plan-map 验收链接 |
| 工单存放位置、编号、状态与生成规则 | `docs/issue-tracker.md` | `AGENTS.md`、`docs/README.md` 一行指针 |
| 已归档 feature 全文 | `docs/archive/features/F-NNN-slug/` | plan-map 归档行 |

规则：写任何内容前先问“这件事的唯一所有者是谁”；如果答案是两个，先拆职责。工单状态以 `tickets/NN-<slug>.md` 的 `Status` 为准，`tickets.md` 只做索引并保持同步。工单模板与拆分方式不属本模型定义，由生成工单的流程或工具决定。

## 2. Feature 生命周期（落地于 `docs/features/README.md`）

| 阶段 | 进入条件 | 产出 | 退出条件（门禁） |
|---|---|---|---|
| `proposed` | 需求被记录 | `plan-map` 一行 | 人确认要做 |
| `planned` | plan 写好、AC 可测 | `plan.md` | 人批准 plan（AC 冻结），plan commit |
| `in-progress` | plan 已批准、工单拆分获人批准 | `tickets.md` 工单地图、`tickets/` 工单、代码、测试 | 所有工单 `verifying`，测试通过，每个产生改动的工单有 commit |
| `verifying` | 所有工单实现完成 | `acceptance.md` 按工单证据 | 每张工单有可复现证据与 commit，所有工单 `accepted` |
| `accepted` | 人签字 | 验收结论 | spec 已同步，最终文档 commit 已产生 |
| 归档 | spec/ADR 已更新 | 目录移入 archive（含工单） | plan-map 路径、状态与提交已更新 |

禁止跳级：没有 plan AC 不拆分；工单拆分未经人批准不写文件；阻塞未 `accepted` 不做；没有工单证据不标 `accepted`；spec 未同步不归档。

Bug 与 hotfix 也建 `F-NNN-slug` 目录并走同一生命周期；`plan.md` 顶部标注类型 `feature | bugfix | hotfix`。hotfix 可只拆一个工单，但不能跳过 AC、验收与 spec 同步。

## 3. 更新触发器

| 事件 | 必须更新 |
|---|---|
| 新需求 | `plan-map` 加行并在演进日志记录；建 feature 目录与 `plan.md` |
| plan 批准 | `status.md` 的 Active / Next；提交 plan |
| 工单拆分批准 | `tickets.md` 工单地图与 `tickets/` 工单文件；提交 `docs(F-NNN): add tickets` |
| 每完成一个工单 | 工单文件状态、`tickets.md` 状态与 commit；阶段变化时 `status.md` |
| 实现完成 | `acceptance.md` 按工单填证据与 commit 范围；`status.md` 阶段 |
| 验收通过 | `spec.md`；`plan-map.md` 的当前基线并在演进日志记录；ADR（如有决策）；`AGENTS.md`（如路由或约束变了） |
| 归档 | feature 目录（含 `tickets/`）移动；`plan-map` 路径/状态/提交并在演进日志记录；`status.md` 复位；补齐最终文档 commit |
| 架构决策 | 新 ADR；spec 架构节链接；`plan.md` 引用 |

## 4. 命名

- Feature ID：`F-001` 起，三位递增；目录 `F-001-<kebab-slug>`；创建后 ID 与目录名不变。
- 工单 ID：`01` 起两位递增；文件 `NN-<kebab-slug>.md`，按依赖顺序编号（阻塞项在前）；创建后编号与文件名不变。
- ADR：`NNNN-<kebab-slug>.md`，四位递增；接受后不修改，只能新增 ADR 标记 `superseded by`。
- 文件名：`AGENTS.md` 大写；其余文档用小写 kebab，与项目现有约定一致。推荐 `spec.md`、`plan-map.md`、`status.md`。
- Feature 状态值：`proposed | planned | in-progress | verifying | accepted`；归档区不写状态，按完成日期排序。
- 工单状态值：`blocked | ready-for-agent | in-progress | verifying | accepted`。

## 5. 上下文预算

- `AGENTS.md`：目标 40–80 行，硬上限 150 行；超过 150 行必须拆分：事实进 spec，feature 流程进 `docs/features/README.md`，工单规则进 `docs/issue-tracker.md`。只放项目身份、文件索引、硬约束、边界、会话开始例程和指针。
- `docs/features/README.md`：feature 规则全文；只放流程、门禁与模板指针，不复制具体 feature 内容。
- `docs/issue-tracker.md`：只放工单存放位置、编号、状态与生成规则；不复制 feature 计划，也不定义工单模板。
- `status.md`：≤ 20 行；只放快照。
- `plan.md`：一个 feature 的完整方案；超过 300 行时拆出 `design.md` 并在 plan 中链接。
- `spec.md`：超过 500 行或模块超过 8 个时，拆成 `docs/spec/*.md`，`spec.md` 只做索引；`AGENTS.md` 的指针同步更新。
- `tickets.md`：只做工单地图（列表、依赖、状态、覆盖 AC、提交、链接）；建议 ≤ 100 行。
- `tickets/NN-*.md`：一个可独立验证的最小工作单元，控制在一个 fresh context window 内；不按文件罗列工单。
- `acceptance.md`：按工单记录证据与 commit；不复制工单正文。

## 6. ADR 触发条件

写 ADR，当决定满足任一：

- 难以回滚（数据模型、公共 API、协议、存储选型）
- 影响多个模块或团队
- 引入或移除关键依赖
- 有被否决的合理备选方案，需要留下理由
- 与现有 ADR 冲突

不写 ADR：命名、局部重构、可逆的实现细节。这些放在 `plan.md` 的“取舍”或代码注释。

## 7. 归档规则

- 归档是**移动**，不是复制；保留 `plan.md`、`tickets.md`、`acceptance.md` 与 `tickets/` 原样。
- 归档前必须：所有工单 `accepted`、acceptance 已签字、spec 已同步、ADR 已记录。
- 归档后 `plan-map.md` 的目录列指向 `docs/archive/features/F-NNN-slug/`，并记录完成日期、一句话结果与最终 commit。
- 归档前确认工作区干净，最终文档 commit 已产生。
- 归档目录不删除历史；需要推翻已归档决策时，新建 ADR 并在 `plan-map` 增加新 feature，不改旧记录。

## 8. plan-map 的演进特性与表结构

`docs/plan-map.md` 是项目演进账本，不是一次性路线图。它随项目状态持续更新，并保留可追溯的历史。

### 8.1 四层演进

| 层 | 内容 | 更新时机 | 规则 |
|---|---|---|---|
| 当前基线 | 已交付的能力/模块 + spec 章节 | 每次验收通过 | 追加新能力；被取代的能力标注 `superseded by F-NNN` |
| 演进队列 | 待做/在做 feature + 状态/依赖/验收 | 新需求、计划批准、状态变化、依赖调整 | 行可修改；ID 不变；状态值合法 |
| 排序与阻塞 | 下一项、优先级、阻塞原因 | 优先级或依赖变化 | 每次重排写原因 |
| 已归档 | 已完成 feature + 日期/结果/提交 | 归档时 | 只追加，不改写 |

### 8.2 演进日志

`plan-map` 末尾维护一个轻量日志，只记路线图级变化（新增、重排、拆分/合并、取代、归档），不记工单级进度：

`| 日期 | 变更 | 说明 | 提交 |`

每次更新 `plan-map` 时刷新顶部 `最后更新`。

### 8.3 表结构

演进中表格列固定为：

`| ID | 名称 | 状态 | 依赖 | 影响 spec | 文档目录 | 验收 |`

- 名称与 `status.md` 使用完全相同的字符串。
- 影响 spec 用 `§4.1, §5` 形式，便于定位。
- 验收列在 `verifying` 前为 `-`，之后指向 `acceptance.md`。

归档表格列：`| ID | 名称 | 完成日期 | 结果 | 文档目录 | 提交 |`。

## 9. status.md 结构

固定字段：`Updated`、`Active`、`Next`、`Blockers`、`Last verification`、`Last commit`。Active 必须是 `plan-map` 中的 ID + 名称 + 阶段（如 `F-001 用户登录 — in-progress`）；无活动 feature 时写 `Idle`。

## 10. 文档语言

跟随项目现有文档；没有先例时用用户的工作语言。术语首次出现时在 `spec.md` 的 Glossary 定义；后续文档使用同一术语，不造同义词。

## 11. Git 提交约束

- 每个 feature 一个分支，默认 `feat/F-NNN-slug`；项目已有约定以项目为准。
- 每个可独立验证的改动至少一个 commit；没有 commit 的工单不能标 `accepted`。
- 默认 commit 格式：`<type>(F-NNN): <summary>`，例如 `feat(F-001): add login endpoint`；项目已有规范以项目为准。
- 代码提交前必须通过 `spec.md` §5 Commands 中的 build/test/lint/typecheck（或项目定义的等价门禁）。
- 纯文档提交只跑文档校验（路径、链接、占位符、状态值），不跑全量测试；代码与文档混合的提交按代码提交处理。
- 代码与相关文档在同一个 commit/PR；验收前必须有一个包含 spec/plan-map/status 更新的文档 commit。
- `tickets.md` 记录每个产生改动的工单的 commit hash；`acceptance.md` 按工单记录验收 commit 或 commit range；`plan-map` 演进日志记录对应 commit，归档行记录最终 commit。
- 交接前 `git status` 必须干净；禁止把多个 feature 混在一个 commit。
- 初始化 commit 产生后，把文档中的 `working tree` 回填为实际 sha；commit 尚未推送时 amend，已推送时改用后续文档 commit。
- 仓库没有 git 时不执行提交：spec、plan-map、status 的 commit 字段写 `no-git`，交接时建议用户 `git init` 并等待确认。

状态变化与 commit 的对应：

| 状态变化 | 必须产生的 commit |
|---|---|
| 需求进入 `proposed` | `docs(F-NNN): propose feature` |
| `proposed` → `planned` | `docs(F-NNN): add plan` |
| `planned` → `in-progress` | `docs(F-NNN): add tickets` |
| `in-progress` → `verifying` | `docs(F-NNN): add acceptance evidence` |
| `verifying` → `accepted` | `docs(F-NNN): sync spec and plan-map` |
| `accepted` → 归档 | `docs(F-NNN): archive feature` |
