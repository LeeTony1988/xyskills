---
name: codebase-understanding
description: Understand a codebase like a professional code auditor. Build a global map, descend global → local → detailed, verify every claim against a file census. Use when onboarding to an unfamiliar repo, explaining a repo's architecture, auditing code never read before, or designing code-comprehension tooling.
---

# Codebase understanding

Distilled from ICPC '26, *"Understanding Codebase like a Professional!"* (arXiv:2504.04553): interviews with 8 professional code auditors plus a 15-developer study of the resulting CodeMap prototype. Auditors onboard a new codebase weekly or daily, under deadlines as tight as 48 hours, where one missed component is irreversible loss — their comprehension flow is the one worth copying.

Two load-bearing words:

- **map** — a levelled structure (modules, edges, reading order) you build first and keep consulting, not a pile of notes.
- **census** — the repo's fixed, checkable facts, above all its file list. The map is a hypothesis; the census is what falsifies it.

## The ladder

Understanding travels global → local → detailed, one level per pass, and each level seeks different information:

| Level | Sought |
|---|---|
| Global | project background, modules, business flow, dependencies |
| Local | a module's key files, components, and the variables that carry its function |
| Detailed | concrete lines and execution paths — correctness and data flow |

Each pass refines one mental model and validates the previous level's claims, which is what turns an overview into something you can act on. Skipping a level is what makes the result come out as a list of categories.

## Steps

### 1. Take the census

Pull the repo's fixed facts from the environment before asking anything of a model: tracked file list, file counts per directory and language, lines of code, manifests, build files, README.

**Done when:** you hold one number every later map must account for.

### 2. Draw the global map

Partition the repo into **business modules** — by what the code does, not by directory layout — one line of purpose each, plus named **edges** in plain language: "A supplies data to B", "C calls B on the failure path". Mark the entry point and write the reading order: what to look at first, second, third.

**Done when:** every census file sits in exactly one module, the business flow reads end to end, and no module is an orphan — each has an inbound and an outbound edge you can name.

### 3. Refine the map against the census

First maps err in a fixed way: dropped files, invented components. Re-derive each round on top of the previous round's output, diff against the census, repair the gaps. Rounds keep paying until they flatten — roughly 3 for a small single-language repo, 4+ for a large one, and multi-language or very large repos gain slowly enough that one pass is not a serious attempt.

**Done when:** two consecutive rounds add no real file and retire no phantom one.

### 4. Descend into the module the task touches

Scope all further reading and querying to that module. Whole-repo context loses focus, and setting the scope is the work that makes the answer land. Name its files, its key functions, the variables that carry its behaviour, and its hand-offs to neighbours.

**Done when:** you can say what enters the module, what leaves it, and which file each sits in.

### 5. Verify on real lines

Open the source and walk the execution path behind every edge you claimed — the way auditors kept switching back to their editor to check the map. A purpose read off a file or directory name is a guess; the code is the evidence.

**Done when:** every claim you would repeat carries a `file:line`, and the census still balances.

### 6. Hand the map over

When the result goes to a human, give them the ladder rather than prose: the global map, the reading order, then zoom on request, keeping text to claims the map already supports. Size the structure to the reader: the full multi-layer graph drowns someone who has never read a repo end to end, so open with the global map alone and offer depth.

**Done when:** the reader can go from your answer to a specific file and confirm you.

## The scaffold

Auditors' largest reported cost was inventing the prompt, so ask the fixed questions instead of improvising — in the codebase's own vocabulary, since answers align to the terms they are asked with:

- **Global** — What business problem does this solve? What are the components and their relationships? How does a request move end to end? Where is the entry point, and what is the reading order?
- **Local** — What does this module do? Which files implement it? Who calls it, and what does it hand off?
- **Detailed** — What is this variable or function for, and how does it change the data along this path?

Write each level's map where the next reader will find it — `docs/architecture.md` or the repo's existing note convention — as a claim the census can falsify, not a description of the code. One levelled artefact retires the study's most-cited waste: re-prompting for hierarchy from scratch.

## Symptom → habit

| You notice | Reach for |
|---|---|
| An explanation of a function that never says how it connects | the edge (step 2) |
| A long answer whose correct parts you cannot pick out | map first, prose second (step 6) |
| A one-shot whole-repo summary that comes out thin and generic | scope, then refine (steps 3–4) |
| Purposes inferred from file names | `file:line` (step 5) |
| Modules in the map no file backs up | census diff (step 3) |
| A repo whose files you cannot enumerate | partition the census, cover each part, and re-scope each query to it: capacity, not intelligence, is what bites at that size |

## Designing tooling for this

Building or evaluating a code-comprehension system — a pi extension, a viewer, an onboarding assistant: read [`references/design-opportunities.md`](references/design-opportunities.md) for the paper's four design opportunities, CodeMap's features, and the measured effects that justify each.
