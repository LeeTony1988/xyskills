---
name: init-ai-first-project
description: 初始化 AI-first 项目文档体系：生成 AGENTS.md、docs/spec.md、plan_map.md、status.md、ADR 与 feature 生命周期目录，并把需求演进规则写入项目。Use when bootstrapping AI-first docs for a new or existing repository, creating AGENTS.md or a project spec, or adopting a feature-folder workflow.
---

# 初始化 AI-first 项目文档

目标：初始化结束后，一个从未见过该仓库的 agent 只从 `AGENTS.md` 出发（含它指向的文件）就能找到：项目是什么、当前事实在哪、现在做到哪、下一步做什么、如何验证。

## 文档模型

三层，各只有一个职责：

| 层 | 文件 | 回答 | 更新方式 |
|---|---|---|---|
| 常驻路由 | `AGENTS.md` | 每次会话必须遵守什么、去哪读 | 少改；路由或约束变化时改 |
| 当前事实 | `docs/spec.md` | 系统现在是什么 | 持续校准 |
| 演进账本 | `docs/plan_map.md` + `docs/features/` | 要做什么、做到哪、证据是什么、路线如何演进 | 持续更新、追加、归档 |

两条不变量：

- **单一事实源**：同一事实只在一个文件里定义，其他文件只放指针。
- **文档随代码走**：代码变更与对应文档变更在同一个 commit / PR 中完成。

所有权、状态机、命名与归档规则的完整定义见 [`references/doc-model.md`](references/doc-model.md)。

## 步骤

### 1. 普查仓库

先读环境，不要先问人：

- 顶层目录、`README*`、manifest（`package.json`、`pyproject.toml`、`go.mod`、`Cargo.toml`、`pom.xml` 等）与 lockfile
- CI 配置、`Makefile` / `justfile` / `Taskfile`、脚本目录
- 现有文档：`AGENTS.md`、`CLAUDE.md`、`docs/`、`.scratch/`、ADR
- `git log -10`、当前分支、commit 风格

产出一张内部清单：语言与框架、包管理器、构建/测试/类型检查/发布命令的**来源文件**、现有文档及其权威范围、缺失项。

**完成标准**：清单中每条结论都能指到具体文件；命令不是凭印象写的。

### 2. 一次性访谈

只问仓库回答不了、且会改变产出的问题。最多 8 个，一次问完：

1. 一句话：项目为谁解决什么问题/功能实现是什么？明确不做什么？
2. 技术栈有哪些锁定项（版本、禁止引入的依赖、必须支持的平台）？
3. 版本工作流：分支模型、commit 规范、每个 feature 的提交节点、合并前必须通过哪些检查？
4. `Always / Ask First / Never` 三类边界各写 2–3 条，用项目自己的例子。
5. 谁有权验收 feature、把状态改为 `accepted`？
6. 文档语言与命名偏好（默认跟随现有文档）。
7. 现有 `AGENTS.md` / spec 是保留合并，还是重写？重写前必须列出保留项。
8. 有没有必须写进 spec 的合规、性能或安全约束？

问题 3 没有明确约定时，默认：一个 feature 一个分支（`feat/F-NNN-slug`），commit 引用 `F-NNN`（默认 Conventional Commits，如 `feat(F-001): ...`），合并前 build / test / lint / typecheck 全部通过；项目已有 CI 时以 CI 为准。

用户不关心的问题给默认值，并记入 `docs/spec.md` 的 Open Questions，不要留空。

**完成标准**：每个问题有答案或明确的默认值；没有“待定”但没有负责人的条目。

### 3. 生成文档

按此顺序写：先写事实，再写索引，最后写路由。

1. `docs/spec.md` — 用 `assets/templates/spec.md.template`，从普查结果填充；每条命令带完整参数、cwd 和前置条件；把“最后校准”写成今天与 `git rev-parse --short HEAD`（未提交写 `working tree`）。
2. `docs/plan_map.md` — 用 `assets/templates/plan_map.md.template`，写清演进说明、当前基线、演进队列、排序与阻塞、已归档和演进日志；“当前基线”从 spec 的模块/能力生成，“演进队列”先留空，“最后更新”和演进日志第一条写本次初始化（未提交时提交列写 `working tree`）。
3. `docs/status.md` — 用 `assets/templates/status.md.template`，写 `Active: Idle`，下一步指向 plan_map。
4. `docs/README.md` — 用 `assets/templates/docs-README.md.template`，写所有权、演进文档、生命周期、Git 提交规则、命名。
5. `docs/templates/` — 复制 `feature-plan.md.template`、`feature-task.md.template`、`feature-acceptance.md.template`、`adr.md.template`，重命名为 `plan.md`、`task.md`、`acceptance.md`、`adr.md`。项目从此拥有自己的模板，后续会话不再依赖本 skill。
6. `docs/adr/README.md` — 用 `assets/templates/adr-README.md.template`，写 ADR 索引与触发条件；没有真实决策时不编造 ADR。
7. `docs/features/`、`docs/archive/features/` — 建目录，用 `.gitkeep` 保留。
8. `AGENTS.md` — 用 `assets/templates/AGENTS.md.template`，最后写，因为它的每个指针都必须指向已存在的文件。

模板是中文骨架；项目以英文为主时，按相同结构翻译标题与说明，保持文件名、状态值、章节编号不变。模板中的 HTML 注释是生成提示，写入项目时删除。

空仓库：`Tech Stack`、`Project Structure`、`Commands` 写 `TBD` 并列入 Open Questions；不编造命令或目录。

已有文件处理：

- 先读，列出“保留 / 合并 / 移动”三项，给用户确认后再写。
- 已有 `docs/spec.md` 时按模板列缺口，只补缺失或过时内容，不重写已准确的部分。
- 已有 `AGENTS.md` 时保留项目特定规则，合并而不是替换。
- 不删除用户内容；冲突时以现有约定为准，把差异列入 Open Questions。
- 已有 `AGENTS.md` 超过 150 行时，先提议拆分：事实进 spec，规则留在 AGENTS。

**完成标准**：模板中的占位符全部替换或进入 Open Questions；`AGENTS.md` 中每个具体路径都真实存在（`F-NNN-slug` 这类模式路径除外）；`docs/templates/` 齐全。

### 4. 验证命令

逐条执行 `docs/spec.md` 的 Commands 表：

- 非破坏性命令（version、help、build、test、lint、typecheck）必须实际运行并记录退出码。
- 发布、部署、删除数据等有副作用的命令**不要执行**；从 CI 配置或脚本中抄录完整命令，标注 `Unverified: <原因>`。
- 失败的命令：先修文档中的路径/参数；修不好就修项目，或标注 `Unverified` 并说明。
- 每条命令记录：`Verified: YYYY-MM-DD, <OS>, exit 0` 或 `Unverified: <原因>`。
- 验证结束后，把最后一条通过的验证写入 `docs/status.md` 的 `Last verification`，把当前 commit 写入 `Last commit`。
- 运行 `git status --short`，确认只包含预期的文档文件；不要替用户提交未确认的变更。

**完成标准**：Commands 表每一行都有验证状态；没有一条命令是猜的。

### 5. 自检

逐项检查，全部通过才交付：

- [ ] `AGENTS.md` ≤ 150 行；没有复制 spec 的章节。
- [ ] `AGENTS.md` 的每个具体路径都存在（`F-NNN-slug` 模式除外）；阅读顺序不超过 5 步。
- [ ] `docs/spec.md` 的 12 个章节都存在；不适用写 `N/A` 并说明，不留空占位符。
- [ ] Commands 表覆盖：环境准备、安装、开发、构建、测试、lint、类型检查、发布、Git 状态检查；不适用写 `N/A`。
- [ ] `plan_map.md` 的 ID 唯一、状态合法、目录可解析；当前基线覆盖 `spec.md` §4.1 的每个模块。
- [ ] `plan_map.md` 包含演进说明、演进日志、最后更新；基线/队列/归档结构完整，无空占位符。
- [ ] `plan_map.md` 的归档表包含提交列；演进日志每条有提交（初始化未提交时写 `working tree`）。
- [ ] `docs/features/` 中每个 `F-NNN` 目录都有 `plan.md` 和 `task.md`；`docs/archive/features/` 中每个都有 `acceptance.md`。
- [ ] `plan.md` 有 Git 提交计划；`task.md` 每个产生改动的 `T-*` 有提交字段；`acceptance.md` 有 commit 记录。
- [ ] `AGENTS.md` 和 `docs/README.md` 有 Git 提交约束：每个功能改动必须有 commit，commit 引用 `F-NNN`。
- [ ] `status.md` 的 Active 与 plan_map 一致；没有活动 feature 时为 `Idle`。
- [ ] `docs/templates/` 四个模板存在。
- [ ] 边界是项目特定规则，不是通用口号。
- [ ] `git status` 只包含本次初始化相关文件。

### 6. 交接

向用户报告：

- 新建/修改的文件清单
- 命令验证结果表（通过 / 未验证及原因）
- Git 状态：文件是否已提交、commit hash（未提交则列出待提交文件）
- Open Questions（最多 5 条，带负责人）
- 下一步：审阅 spec → 用 `docs/templates/plan.md` 建第一个 feature

**完成标准**：用户能说出“下一个功能从哪里开始、如何验收”，并确认 spec 可作为当前事实源。

## 边界

- 初始化阶段只产出文档；业务功能留给第一个 feature。
- 只创建有真实内容的 ADR、feature 和计划。
- `docs/spec.md` 只写当前事实；历史计划放 `plan_map.md` 与 feature 目录。
- `AGENTS.md` 保持路由角色；长命令和目录树放 `docs/spec.md`。
- 初始化文档也遵守 Git 规则：先展示 `git status` 与 `git diff`，经用户确认后作为一个独立 commit。
