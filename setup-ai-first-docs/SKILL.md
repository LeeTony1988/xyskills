---
name: setup-ai-first-docs
description: 为 AI-first / AI-native 项目搭建或重整文档系统：AGENTS.md 路由、docs/README 文档地图、HLD/spec/roadmap 事实与演进层、features/status 功能地图，以及每个 feature 的 plan.md 与不入 Git 的 .scratch 规格和工单。Use when bootstrapping docs for a new repo, migrating scattered README/AGENTS.md/docs into this model, or adding the standard feature document skeleton. Not for writing product code or reviewing a finished design.
---

# 搭建 AI-first 文档系统

目标：搭建完成后，一个从未见过仓库的 agent 只从 `AGENTS.md` 出发，就能回答五个问题：项目是什么、系统现在是什么、当前做到哪、下一个功能怎么做、做完如何验收。

成功的样子：

- 所有**长期有效**的事实都有唯一所有者，并且都在代码和 Git 里。
- 所有**执行期**的规格与工单都在 `.scratch/`，可随时删除、重建，不污染仓库。
- 人与 agent 的交接面只有两个：`plan.md`（人批准）和 `tickets/`（agent 执行）。

## 文档模型

| 层 | 文件 | 回答什么 | 入库 |
|---|---|---|---|
| 路由 | `AGENTS.md` | 每次会话必须遵守什么、按什么顺序读哪些文件 | 是 |
| 文档规则 | `docs/README.md` | 文档地图、所有权、生命周期、更新触发器 | 是 |
| 系统事实 | `docs/spec.md` | 项目是什么、技术栈、结构、命令、代码风格、测试策略、边界、成功标准 | 是 |
| 系统结构 | `docs/HLD.md` | 系统由哪些模块组成、边界与关键机制 | 是 |
| 演进账本 | `docs/roadmap.md` | 时间、功能/文档索引、简介、状态 | 是 |
| 功能地图 | `docs/features/status.md` | 哪些在做、哪些已完成、哪些已归档 | 是 |
| 功能决策 | `docs/features/feature-<slug>/plan.md` | 这个功能为什么做、怎么做、接口与数据对象 | 是 |
| 执行规格 | `docs/features/feature-<slug>/.scratch/feature-<slug>-spec.md` | agent 执行时必须逐条满足什么 | **否** |
| 工单目录 | `docs/features/feature-<slug>/.scratch/tickets/` | 工单由用户自由规划，格式/命名不限；本 skill 只约束目录与三张独立收尾工单 | **否** |

四条不变量：

1. **单一事实源**：同一事实只在一个文件定义，其他位置只放指针（路径 + 章节 + 为什么读）。
2. **plan 是人的契约，scratch 是 agent 的工作台**：`plan.md` 记录经人确认的决策；`.scratch/` 是由 plan、spec、HLD 派生出的执行细节，不是决策地。
3. **scratch 可丢弃，结论必须回写**：任何需要长期保留的结论，在 feature 完成前必须回写到 `plan.md`、`docs/spec.md` 或 `docs/HLD.md`；只活在 `.scratch/` 的决策视为丢失。
4. **文档随 feature 走**：行为、结构、命令变化在同一个 feature 周期内同步到文档；代码提交与文档更新各自独立成单，不跨 feature 遗留。

放置规则、状态机、命名与上下文预算见 [`references/doc-model.md`](references/doc-model.md)；怎么写 plan / feature spec 见 [`references/ai-first-writing.md`](references/ai-first-writing.md)；feature 的完整生命周期与工单约束见 [`references/feature-workflow.md`](references/feature-workflow.md)。

## 工作流

### 1. 侦察仓库

先读环境，再问人：

- 顶层目录、`README*`、manifest（`package.json`、`pyproject.toml`、`go.mod`、`Cargo.toml`、`pom.xml` 等）与 lockfile。
- CI、`Makefile` / `justfile` / `Taskfile`、脚本目录。
- 现有文档：`AGENTS.md`、`CLAUDE.md`、`docs/`、`README`、issue/ticket 目录。
- `git rev-parse --is-inside-work-tree`；有 Git 时读 `git status --short`、`git log -5`、当前分支。

产出一张内部清单：项目名、语言与框架、构建/测试/lint/typecheck 命令的**来源文件**、模块边界、现有文档及其权威范围、缺失项。清单里每条结论都必须能指到具体文件。

**完成标准**：命令不是凭印象写的；所有未知项进入第 2 步的问题清单。

### 2. 一次性访谈

只问仓库回答不了、且会改变产出的问题。最多 6 个，一次问完：

1. 一句话：项目为谁解决什么问题？明确不做什么？
2. 架构边界：核心模块、外部系统、锁定的技术选型（用于 HLD）。
3. 当前有没有正在开发或刚完成的功能？有则给出 slug 和一句话简介（用于 status 首行，开工后再进 roadmap）。
4. 文档语言与 feature 命名偏好（默认中文；`feature-<kebab-slug>`）。
5. 谁验收 feature、谁能批准 `plan.md`（默认：项目维护者）。
6. `.scratch/` 策略确认：本地不入 Git、可随时删除、长期结论回写。默认开启；若团队要求入库，必须改 `.gitignore`、AGENTS 和 docs/README 三处，并说明理由。

用户不关心的问题给默认值，并记入 `docs/spec.md` 的 Open Questions，不要留空。

**完成标准**：每个问题有答案或明确的默认值；没有“待定”但没有负责人的条目。

### 3. 确认方案（门禁）

写文件前，先用一屏展示并等待确认：

- 将要生成的目录树（见第 4 步的模板清单）。
- 所有权矩阵：每个事实放在哪个文件。
- 状态词汇：`planned | in-progress | done | archived`（roadmap 只使用后三个）。
- `.scratch/` 的忽略规则，以及“只活在 scratch 的决策视为丢失”。
- 改造仓库时，额外展示每个现有文档的处置：**保留 / 合并 / 移动 / 暂不动**。

**完成标准**：用户确认目录树、`.scratch` 策略和迁移处置；有分歧先改方案，不进入生成。

### 4. 生成骨架

先运行脚手架（`<skill-dir>` 指本技能目录）：

```bash
python <skill-dir>/scripts/scaffold_docs.py <project-root> --project-name "<项目名>"
```

脚本只创建缺失文件，不覆盖已有文件；会创建目录、复制 `docs/templates/`、向 `.gitignore` 追加 `docs/features/*/.scratch/`。随后按“先事实、再索引、最后路由”的顺序填写：

1. **`docs/spec.md`**：按模板写项目级规格，九个部分必须齐全：`Objective`（项目是什么、用户故事/验收标准）、`Tech Stack`、`Project Structure`（源代码/测试/文档目录）、`Commands`、`Code Style`、`Testing Strategy`、`Boundaries`、`Success Criteria`、`Open Questions`。`Commands` 必须覆盖环境准备、目录创建、依赖安装、构建、运行、测试、Lint、类型检查、发布；每条都是带完整参数、cwd 与前置条件的可执行命令，并标注 `Verified` / `Unverified`。不写实现方案和历史。
2. **`docs/HLD.md`**：模块划分与职责、依赖方向、关键流程（编号步骤，标出模块与接口）、数据架构（对象、所有者、存储、一致性）、外部接口边界、非功能设计。每条关键流程至少覆盖一条端到端路径。
3. **`docs/roadmap.md`**：每个**已开工或已完成**的功能一行（`in-progress | done | archived`），固定四列 `时间 | 文件索引 | 简介 | 状态`。`planned` 只登记在 status，plan 批准后再进 roadmap。时间用 ISO 日期，文件索引指向 `features/feature-<slug>/plan.md`。没有真实功能就留空表，不编造。
4. **`docs/features/status.md`**：覆盖所有 feature 目录与状态（含 `planned`）；roadmap 中出现的功能必须在此表且状态一致；没有活动 feature 时写 `Idle`。`plan` 列链接到 `plan.md`。
5. **`docs/README.md`**：文档地图（每个文件/目录的职责、读者、更新时机）、四层模型、唯一事实源规则、feature 生命周期与工单约束、`.scratch` 规则、更新触发器、命名、写作规则、新 feature checklist。
6. **`AGENTS.md`**：最后写。只放项目身份、会话开始顺序、文件索引、硬约束、`Always / Ask First / Never`。目标 40–100 行，硬上限 120 行；每个具体路径必须真实存在。
7. **`docs/templates/`**：确认 8 个模板齐全：`AGENTS.md`、`docs-README.md`、`HLD.md`、`spec.md`、`roadmap.md`、`features-status.md`、`plan.md`、`feature-spec.md`。模板里的 `{{...}}` 占位符保留，供后续复制时替换。

已有文件处理：

- **先读再动**：列出“保留 / 合并 / 移动”，经用户确认后才写。
- 已有 `docs/spec.md`：项目级目标、技术栈、结构、命令、风格、测试、边界保留并补齐九节；架构内容迁到 HLD，历史/计划内容迁到 roadmap，单功能行为迁到对应 feature 的 `plan.md`。
- 已有 `AGENTS.md`：保留项目特定规则，合并而不是替换；把事实性内容下沉到 spec/HLD，把流程性内容放到 `docs/README.md`。
- 已有 `docs/features/`：先映射现有状态到四值词汇，不擅自重命名 feature 目录；工单格式保持用户原样。
- 已有 roadmap 含 `planned` 行：把 `planned` 行迁到 `status.md`，roadmap 只保留已开工/已完成功能。
- 不删除用户内容；冲突时以现有约定为准，把差异列入 Open Questions。

空仓库：`Tech Stack`、目录、命令写 `TBD` 并进入 Open Questions；不编造命令、模块或功能。

**完成标准**：生成文档中没有未替换的 `{{...}}`（`docs/templates/` 除外）；`AGENTS.md` 中每个具体路径都存在；`docs/README.md` 能解释每个文件何时更新；`.gitignore` 包含 scratch 规则。

### 5. 首个 feature（可选）

只有用户确认存在当前功能时才做；没有就保持 `status.md` 为 `Idle`，不要造一个示例功能。

1. 运行 `python <skill-dir>/scripts/scaffold_docs.py <project-root> --feature <slug>` 创建 `plan.md`、`.scratch/feature-<slug>-spec.md`、`.scratch/tickets/`。
2. 填 `plan.md`：先写 30 秒摘要，再画方案总览图、模块依赖图；关键机制用 `sequenceDiagram`（或顺序分点文字），数据对象用 `erDiagram` + 生命周期 bullet。核心接口只保留最多 6 行小表（能力 | 模块/接口 | 调用方 | 关键约束/错误），必须写到 SDK/模块/符号级；完整参数、字段、错误码放 `.scratch`。图只保留核心模块，超过 7 个节点或 10 条消息时拆图或改文字，不能画成“毛线球”。
3. 人批准 plan 后，再写 `.scratch/feature-<slug>-spec.md`；冲突时停下来问，不自行选择。
4. 在 `.scratch/tickets/` 中由用户自由规划工单；格式、命名、数量由用户决定。至少包含三张独立工单：**验收**、**代码提交**、**文档更新**，三张不得合并。实现工单只改代码、不做最终提交；最终代码提交由代码提交工单完成，长期文档由文档更新工单提交。推荐顺序：实现 → 验收 → 代码提交 → 文档更新；多代码仓库时每个仓库一张代码提交工单。
5. 详细门禁与状态流转见 [`references/feature-workflow.md`](references/feature-workflow.md)。

**完成标准**：`plan.md` 的验收标准可测；核心图能让人在 5 分钟内复述主路径与模块依赖；feature spec 的每条规格能映射到验收工单；三张独立工单（验收/代码提交/文档更新）已规划。

### 6. 校验

先跑脚本：

```bash
python <skill-dir>/scripts/verify_docs.py <project-root>
```

脚本机检：必需文件与模板齐全、AGENTS 行数与指针、必需章节、roadmap 四列与状态值、status 与 feature 目录一致、plan 关键章节、feature spec 存在、工单目录存在、Markdown 相对链接可解析、未替换占位符、`.scratch` 是否被 Git 跟踪。

再人工确认：

- [ ] `AGENTS.md` 只做路由，没有复制 spec/HLD 的章节；每个指针都指向真实文件。
- [ ] `docs/spec.md` 九个部分齐全，`Commands` 每行都是完整可执行命令而不是工具名；没有路线图、历史或 feature 实现步骤。
- [ ] `docs/HLD.md` 的模块边界、依赖方向和一条关键流程能让新人复述系统结构。
- [ ] `docs/roadmap.md` 每行四列，日期真实，状态与 `features/status.md` 一致；没有 `planned` 行。
- [ ] 每个 feature 的 `plan.md` 写到了具体 SDK/模块/接口与数据对象生命周期，而不是“待实现”。
- [ ] `.scratch/` 中没有只存在于本地、却应当长期保留的决策。
- [ ] 每个 feature 至少有三张独立工单：验收、代码提交、文档更新；没有合并成一张。
- [ ] 没有编造的命令、模块、功能或日期。

**完成标准**：脚本退出码 0；人工项全部通过，或未通过项已列入交接说明。

### 7. 提交与交接

- 展示 `git status --short` 与 `git diff`；确认暂存区不包含任何 `.scratch/` 文件。
- 用 `git check-ignore -v docs/features/<feature>/.scratch/<feature>-spec.md` 证明忽略规则生效。
- 经用户确认后提交，建议信息：`docs: bootstrap AI-first documentation system`。
- 无 Git：不执行提交，说明 `.scratch` 仍由 `.gitignore` 排除，并建议 `git init`（等用户确认）。
- 交接时报告：新建/修改的文件、文档地图一句话、Open Questions（最多 5 条）、下一个动作（批准 plan → 规划工单 → 按用户规划执行）。

**完成标准**：`git status` 只剩预期文件；用户能说出“下一个功能从哪个文件开始、如何验收”。

## 边界

- 只产出文档系统，不写业务代码；不替用户决定产品需求。
- 不创建没有真实内容的 feature、roadmap 行或 ADR 式决策。
- `AGENTS.md` 保持路由角色：长事实进 spec/HLD，流程规则进 `docs/README.md`。
- `.scratch/` 永远不作为长期事实的唯一所在地；committed 文档不链接到 `.scratch/` 内部文件（链接会在他人克隆后失效）。
- 不删除、不改写用户已有文档；迁移先给方案并等确认。
- 文档中的命令必须实际运行过或标注 `Unverified: <原因>`；发布、部署、删除类命令不执行。
