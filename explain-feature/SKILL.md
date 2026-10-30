---
name: explain-feature
description: 'Explain how a feature works end to end: read the docs and the relevant code, map the architecture and module dependencies, walk the complete flow, explain 3–6 key steps with code anchors, add a concrete example, and cover edge cases and common misunderstandings; by default write docs/<feature>.md. Use when the user asks "how does X work", "walk me through X", "帮我理解/梳理这个功能", "从入口到……", "画一下架构/模块关系", or wants a whole-process document rather than a code review.'
---

# Explain a feature

Before explaining a feature to the user, read the docs and the code. Docs explain design intent and terminology but are not evidence; facts come from the code.

The goal is not to restate the code but to leave the reader with a mental model they can remember and reuse: understand the main path first, then go deeper only where needed. Do not write a complete reference manual. Work in three layers:

> shape (architecture + main flow) → mechanism (3–6 key steps + code anchors) → application (example + counterexample + edge cases and misunderstandings)

Introduce abstract concepts as "diagram → one-sentence explanation → example"; add a counterexample for easily confused concepts. If two abstract concepts in a row have neither a diagram nor an example, stop and add one.

Guarantee the architecture diagram and the main flow diagram first. Add ownership, state, and sequence diagrams only when they are needed; do not draw them for completeness.

## 0. Decide the deliverable first

- **Default to a document**: write it to `docs/<feature>.md`. Use ASCII kebab-case for the file name, for example `docs/task-scheduler.md`, not `docs/新功能说明.md`.
- If the user explicitly wants only a verbal explanation, a compressed version in chat is fine; **when the user asks for a document, never answer only in chat**.
- If `docs/<feature>.md` already exists: read the old document first and edit it in place. Do not create a `-v2`, and do not append a second explanation to the end.

## 1. Frame the question

- State the feature in one sentence: **"<trigger> causes <feature> to pass through <key path> and produce <observable result>."**
- Write the scope in one line: which path this document explains, and what it deliberately leaves out.
- Use a table to define easily confused words: which layer this document means, and what it does not mean.

  | Word | What it means here | What it does not mean |
  | --- | --- | --- |
  | task | ... | ... |

## 2. Draw the architecture diagram

The architecture diagram answers **where the feature lives and who depends on whom**.

- Draw one Mermaid `flowchart` (with `subgraph` for layers) or a component diagram, kept to 6–12 modules; for a single-module feature, a small context diagram is enough.
- Group by real boundaries: user/UI, host/API, extension/registry, runtime/scheduler, storage, external services. Collapse a subsystem into one box when its internals are not the subject.
- For each module, write one line for its responsibility and the interfaces it exposes or consumes. Label edges with the real contract (`POST /api/...`, `conversation.submit()`), not "calls".
- Use `-->` for synchronous calls and `-.->` for persistence/asynchronous handoff; mark which module owns the conversation, task, document, or source of truth.
- Add a module table:

  | Module | Responsibility | Exposes / depends on | Owns |
  | --- | --- | --- | --- |
  | ... | ... | ... | ... |

- Explain why each important boundary exists (replaceability / durability / ownership / isolation), and add one short paragraph: the entry point, the source of truth, the host/runtime boundary, and which modules are replaceable.

## 3. Draw the ownership/holding diagram (when needed)

Draw it only when ownership or lifecycle is the hard part of understanding the feature; otherwise mark the owner in the architecture diagram.

- Draw a Mermaid `flowchart` or component diagram, kept to 6–12 core modules.
- Mark create / hold or reference / manage / use (without holding) / destroy / release.
- For a managing module, note its management structure (`queue`, `array`, `map`, `hash map`, and so on).

## 4. Draw the state transition diagram and state storage table (when stateful)

Draw it only when the feature has a clear state machine; when states are simple, one state table is enough.

- Draw a Mermaid `stateDiagram-v2`; label each edge with "event / triggerer".
- Use notes to mark the allowed operations and constraints for each state, and to make illegal transitions explicit (for example, `Disposed -> Running` should raise an error).
- Follow the state diagram immediately with a state storage table: where each state or piece of data lives, and why.

## 5. Draw the complete flow

The flow diagram answers **what happens in what order**.

- Overlay the flow on the architecture: each step names the module responsible for it.
- Draw one Mermaid `flowchart` from the trigger to the user-visible result.
- Include the main path and its hinge points: entry and validation, decision or state-change points, and terminal states.
- Make labels concrete down to file, function, record, or document names; do not write "process", "service", or "flow".
- Put the diagram before the prose and walk through the arrows in prose; do not rewrite the diagram as a bullet list.

## 6. Draw a sequence diagram (for cross-module handoffs)

Draw it only when a cross-module synchronous or asynchronous handoff is the hard part; if a flow diagram explains it, skip it.

- Use the module names from the architecture diagram as participants, not file names; label every message with the real interface or function name.
- Use `->>` for synchronous calls and `-->>` for asynchronous calls or returns; use `activate`/`deactivate` to mark who is handling the message.
- For an asynchronous handoff, use `Note over` to mark "does not wait for the result here; the result returns from X"; mark timeouts and retries on the diagram when they exist.
- Draw only the key round trips (5–10 messages, 2–5 participants), one path per diagram; add a paragraph below the diagram for the key constraints.

## 7. Break down the key steps

Break the main path into **3–6 steps**, each answering one decision point. Use the **question-and-answer note** format:

```text
**Why is the xxx feature designed this way?**

- explanation 1
- explanation 2
```

- Attach a snippet only where code evidence is needed, at most one per step: 3–15 lines, marked **simplified**, with interfaces kept intact.
- Explain the snippet's intent, logic, and use case; for a complex step, add a concrete example or data.
- Write code locations as `path:line`; open the source and verify before writing — never guess line numbers or symbol names.
- When the reader says "I still don't understand", do not repeat yourself. Use a smaller example, add a counterexample or an analogy, and edit that section directly.

## 8. Write the document

Default to `docs/<feature>.md`. When the user explicitly asks for a document, you must create or update the file; do not give the explanation only in chat.

Use this structure (7 sections by default; delete whatever you can):

```text
# <Feature>: end to end

> Definition: <trigger> causes <feature> to go through <key path> and produce <observable result>
> Scope: ...
> Terms: see the glossary below

| Word | What it means here | What it does not mean |
| --- | --- | --- |
| ... | ... | ... |

## 1. Architecture and ownership
[architecture diagram + module table; add the entry point, source of truth, host/runtime boundary, replaceable modules, and the reason for each key boundary; append an ownership diagram when ownership or lifecycle is a hard point]

## 2. State and storage (when stateful)
[stateDiagram-v2 + state storage table]

## 3. Complete flow
[main flow diagram; append a sequence diagram when cross-module sequencing is a hard point]

## 4. Key steps and code (3–6)
[Q&A notes; only steps that need code get a 3–15 line snippet, at most one per step; mark it "simplified" and include path:line]

## 5. Concrete example and counterexample
[one concrete example or data set walking the normal path; one counterexample for a confusing concept]

## 6. Edge cases and common misunderstandings
[only relevant edge cases; misunderstandings short and concrete]

## 7. Code index
[path:line → purpose]
```

Rules for the document:

- Write in the user's language; keep identifiers, paths, and protocol names exact.
- By default include only one main path, one architecture diagram, one main flow diagram, 3–6 key steps, and one concrete example; add ownership, state, and sequence diagrams only when needed; write branches and edge cases only when relevant — do not aim to cover every case.
- Keep one topic per section; move unrelated details out or delete them.
- Put diagrams before the prose they explain; when a diagram says it clearly, do not repeat it in paragraphs; when code says it clearly, do not explain it line by line.
- Keep key steps and their code together, in "step → snippet → explanation" order; do not collect the code into a separate "core code" section.
- Keep the state diagram and the state storage table in the same section.
- Link existing docs for deep details; edit an old document in place rather than appending a second explanation at the end.
- Before finishing, verify paths, line numbers, and behavioural conclusions.

## 9. Finish

Close with a 3–5 line recap of the architecture, ownership/state (if any), and the complete flow's shape. Name the part most likely to be confused, and point to the concrete example that resolves it.

Offer only one next deep-dive suggestion; do not list a catalogue of follow-ups.

## Checklist

Before delivery, check only the non-negotiables; mark `N/A` where not applicable.

**Scope and structure**

- [ ] one-sentence definition + one-line scope + glossary
- [ ] 7-section skeleton adapted; code index complete; optional diagrams and tables deleted when not applicable, not padded in
- [ ] written to `docs/<feature>.md` when the user asked for a document; old document updated in place

**Diagrams and flow**

- [ ] architecture diagram has 6–12 modules, edges are real contracts, source of truth is marked
- [ ] main flow diagram runs from the trigger to the user-visible result, with each step mapped to its module
- [ ] ownership/state/sequence diagrams appear only when they explain a hard point; state diagram and state storage table share one section
- [ ] diagrams come before the explanation, Mermaid parses, and module names are consistent

**Key steps and examples**

- [ ] 3–6 key steps in Q&A notes, each with one question and one decision point
- [ ] code only beside the step that needs it: at most one snippet per step, 3–15 lines, marked "simplified", with `path:line`
- [ ] one concrete example plus a counterexample for an easily confused concept
- [ ] edge cases limited to relevant items

**Delivery**

- [ ] conclusions come from the source; paths and line numbers verified
- [ ] 3–5 line recap: architecture/flow shape + one deep-dive suggestion

## Anti-patterns

- Starting with a directory tree, a whole function, or a large block of source; giving details before architecture.
- Drawing only a flow diagram with no architecture diagram: the reader sees motion but not where anything lives.
- Drawing one box per file, with edge labels like "calls" or "handles" instead of real contracts.
- Mixing architecture, ownership, state, flow, and sequence into one diagram; or drawing every diagram regardless of whether it explains a hard point.
- An ownership diagram that is just the dependency graph redrawn; a state diagram without events/triggerers or illegal transitions; a sequence diagram with participants split by file and no distinction between sync and async.
- Explaining only "what" and never "why".
- Writing the document as a list of code and diagrams: stuffing in every branch, diagram, and code block so the reader cannot grasp the main line.
- Writing the key steps as a line-by-line source walkthrough or a four-column field table instead of 3–6 Q&A notes.
- Splitting key steps and code into two sections, or dumping whole code blocks into the document; snippets not marked "simplified" and without `path:line`.
- An example that is only abstract description, or that shows only the normal path and skips relevant edge cases.
- Giving definitions only, with no counterexample or correction of common misunderstandings.
- Guessing line numbers, or describing code you have not read.
- Answering only in chat when the user asked for a document; creating a `-v2` or appending a second explanation when an old document exists.
- Ending with a list of "next you could look at…" instead of one deep-dive suggestion.
