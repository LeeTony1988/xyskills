# Design opportunities for an LLM-powered codebase understanding system

The paper's Stage 2 (design opportunities) and Stage 3 (CodeMap prototype), with the evidence behind each. Consult this when the task is to build or evaluate tooling for codebase comprehension; the operating workflow lives in [`../SKILL.md`](../SKILL.md).

Framing the paper calls **human–AI co-understanding**: the model is not an answer generator but a collaborator that extracts, reformulates, and contextualises information so machine-level representations become human-readable structures, while the human steers exploration by interpreting and inquiring.

## The four design opportunities

Derived from the auditors' three complaints about conversational LLMs: repetitive manual prompting for hierarchy, the manual effort of decomposing a project into promptable segments, and answers too general to align with the current reasoning focus — *"I can ask the model to explain a function, but it never tells me how this connects to the rest of the codebase."*

**DO1 — Extract at the level the user is on.** Serve the three-level chain automatically instead of making the user mine for it: global (project background, structure), local (key files, component details), detailed (clarification of a named item). Value: removes manual information-gathering so attention stays on comprehension.

**DO2 — Decompose for the user.** Splitting a codebase into functional components is the expertise the study's novices lacked and the effort the experts resented. A tool should perform the split and let the user re-scope by picking a component. Value: it also *creates the context window* — the thing users could not articulate when pasting a whole repo into a chat.

**DO3 — Represent across levels.** Structural relationships (inter-module dependencies, data ownership) are where comprehension is won and lost, and prose is the wrong carrier for them. Value: multiple abstraction layers, visibly linked, each node carrying both a graphic and a natural-language relation.

**DO4 — Scaffold the querying.** Users lose their thread formulating queries, and query-writing itself needs domain expertise. A tool should pre-answer the common questions at each level and keep transitions between levels one click, so the user's own evolving reasoning can rejoin the structured flow. Value: the least expert user gets the most expert flow.

## CodeMap's two key features

**Feature 1 — per-layer extraction and representation.**

- Global map, business component view: modules, components, links between them.
- Global map, function-call view: classes as nodes with inheritance edges.
- Local map: relationships among variables and functions within a file.
- Natural-language enhancement: every link phrased as a relation ("Component A provides or manages data for Component B"), plus a step-by-step architectural reading guide that orients the user through the global map.

**Feature 2 — switching layers by interaction.**

- Click-level changes: global ↔ local ↔ detailed, and back up to global without losing it. Chat is linear and makes higher-level context hard to return to; the map makes re-ascent cheap.
- In-context query: a question asked at any layer is auto-composed with that layer's context (module name, files, selected area), so the user explores deeper without restating where they are.

## Generation and accuracy mechanism

- **Prompt structure**: task description + explicit output constraints + few-shot example, emitting DOT for the graph and JSON for the overview (summary, entry point, execution instructions, step-by-step reading guide). Format-strict output is what makes the map machine-renderable.
- **Generality**: prompts are neither project-specific nor language-specific — few-shot placeholders (`Module1 → Module2`) with no language-bound detail, so the same prompts served Solidity, Python, and Java.
- **Iterative refinement**: each round rebuilds on the previous round's output, since single-pass generation misses components and files and hallucinates others.
- **Proxy ground truth**: functional decomposition has no agreed answer, so use a fixed fact — the repo's file count — and score the map on wrongly included vs. missing files. Accuracy = (TP + TN) / (TP + TN + FP + FN), with TN inapplicable because no file should be excluded from the map.
- **Observed convergence**: accuracy climbed with each round, stabilising by round 4 for Python and round 3 for Solidity, still climbing for the tested Java projects. Small repos, especially Solidity, converged fast; large ones (Python-668, Solidity-73, Java-100) gained slowly, so rounds needed scale with repo size.
- **Capability ceiling**: with a 1M-token model (GPT-4.1) and richer chunking, five refinement rounds reached 99% on Python-130 but only 27% on Python-668. Map quality tracks context and retrieval capacity; the right fix at scale is partitioning the repo and covering each partition, not a cleverer single prompt.
- **Evaluation cost to expect**: 9 Python, 8 Solidity, 3 Java projects at 5 rounds × 10 runs exceeded 1000 API calls — real numbers for planning a replication.

## Measured effects (the justification for the interface)

Setup: 9 experienced developers (4–10 years, daily ChatGPT users) against ChatGPT and the commercial static-analysis visualiser Understand, in 25-minute tasks with think-aloud, quizzes, and NASA-TLX; 6 novices did free 10-minute exploration of CodeMap vs. ChatGPT. 18.48 hours of video, 25 hours of annotation.

- Perceived: 9/9 found CodeMap useful, intuitive, and easy to use, vs. 7/9, 2/9, 8/9 for ChatGPT and 4/9, 3/9, 0/9 for Understand.
- Behaviour shift, vs. Understand: 75% less time reading code in the editor (2.08 vs. 8.18 min), 90% more time viewing maps (8.55 vs. 4.50 min). The shift appeared with CodeMap and not with the static tool.
- Behaviour shift, vs. ChatGPT: reading and interpreting LLM text fell from 5.48 min to 1.15 min, a 79% reduction, with attention moving onto the map.
- Why the shift happens: decomposition plus semantic relation descriptions build module-level understanding, and the selected component doubles as a context the user could never describe well to a chat ("we usually just upload the entire repo… it definitely loses focus").
- Why the static tool failed: interface misaligned with the natural reading flow, information at the wrong cognitive level, no key points or textual explanation, overwhelming volume, call relations at too fine a granularity — users abandoned it for the editor. It suited work *after* a mental model already existed.
- Why chat underperforms: it demands the user already know what to ask, in the repo's own terms; without that, output lists categories without interpreting them, or reasons from file names rather than content. It builds understanding gradually for experts and leaves novices asking "what is starlette?" with no entry point.
- Where a map pays off most: large and complex projects — *"the reason you'd create diagrams is when a project is really big, when it's too hard to describe clearly using only language"* — and beyond the second layer users will not draw it themselves.
- For novices: the levelled flow cut non-purposeful exploration, gave a starting point and a blueprint that kept key functions from being missed, and pre-empted the standard questions ("what is the business problem, how do components relate, how does the flow work") so depth came from clicking, not prompt-writing. Diagrammatic form matched how they already learned.
- Counter-example worth designing against: one novice with no full-codebase reading experience found the displayed volume overwhelming and preferred chat's linear explanation — structure offered all at once is a learning curve, so reveal a level at a time.

## Limits of the evidence

- Performance depends on retrieval quality and the underlying model's reasoning, context length, and hallucination rate; mitigated only by refinement rounds and a stronger model.
- 8 interviewees, 15 study participants; observational study aimed at validating the design opportunities, not benchmarking a product.
- Baselines were ChatGPT and Understand only; AI-native IDEs (Cursor, Trae) were untested — they mainly assist context selection and lack hierarchical, level-switching views.
- Interviews date from 2024 with ChatGPT as the tool of reference; the authors hold that the strategies, not the tools, generalise.

Source: arXiv:2504.04553v3 · DOI 10.1145/3794763.3794822 · code and prompts at https://gaojie058.github.io/code-map/
