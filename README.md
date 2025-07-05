# LambdaLib – Self-Evolving Meta-language λ Library

## 1 Vision
LambdaLib is **not** just another functional toolkit. It is a _substrate for meaning_: an execution environment in which every element is itself a _λ-entity_ capable of describing, transforming, and recreating its own behaviour. Code, data, rules, and even the runtime’s scheduling policy are all expressed as the same primitive — **`λ`**.

*One primitive ➜ fractal expressiveness ➜ emergent logic.*

### Why do this?
| Conventional stack | λ-approach |
|--------------------|------------|
| Code ↔ Data split | Unified semantic graph (everything is `λ`) |
| Fixed control flow | Graph rewrites that can re-wire themselves at run-time |
| Tool-driven evolution (humans edit source) | _Intrinsic_ evolution: λ-graphs carry the rules needed to extend themselves |

The goal is to build systems that **adapt** and **explain** their own reasoning, instead of passively executing handwritten algorithms.

---

## 2 Conceptual Primer

| Term | Intuition | Formal sketch |
|------|-----------|---------------|
| `λ` (LambdaNode) | "Atom of meaning" — holds state _and_ the rules that transform it | `λ = (label, data, links, ops)` |
| Operation (`Λ`) | Transform describing _how_ to rewrite one or more `λ` | Itself a `λ` with `ops=[pattern → rewrite]` |
| Graph | The runtime world: nodes + edges | `G = {λᵢ}` |
| Engine | Minimal host that iterates "apply ops" | Selects active ops, applies until quiescent |

> **Meta-rule:** _Everything that happens is the result of some `λ` rewriting other `λ`s._

---

## 3 Package Layout
```
lambda_lib/
├── core/        # λ primitives & the bare engine
├── ops/         # Seed library of basic operations (eval, norm, mirror, …)
├── graph/       # Utility rewrites: mapping, filtering, visualising graphs
├── runtime/     # Higher-level executors, scheduling strategies
└── examples/    # Pure-λ demos (will grow as the library learns)
```
Each directory already contains **contracts** (`#@module:` blocks) describing intent and invariants. Implementation starts empty so the system can grow organically.

---

## 4 Execution Model
1. **Seed graph** — you provide an initial set of nodes: _data_, _operations_, and _meta-operations_ (ops that rewrite other ops).
2. **Engine tick** — the `LambdaEngine` selects applicable operations (pattern-matching over nodes).
3. **Rewrite** — patterns produce new or modified `λ` nodes, which may include **new rules**.
4. **Convergence or divergence** — the process continues until a stability criterion is met (or forever, for open-ended systems).

Because rules live inside the graph, _the graph can change the way it changes_.

---

## 5 Self-Organisation & Learning
LambdaLib delegates "learning" to **structural evolution**:

* **Gradient-like rewrites** — Ops can compute local utility (e.g., classification error) and spawn improved variants of themselves.
* **Mirror & phase** — Nodes can create oppositional or context-shifted copies, exploring alternative hypotheses.
* **Experience fold (⨂)** — Aggregates patterns that repeatedly succeed into higher-order abstractions.

Nothing here hard-codes SGD, back-prop, or Bayesian updates. Those can emerge as _particular rewrite strategies_ carried by nodes.

---

## 6 Worked Example: Online Classification

> _Task:_ maintain a classifier that labels streaming sensor data into `NORMAL` / `ALERT`.

### 6.1 Seed graph
```
(DataStream) --feeds--> (FeatureMaker λ) --feeds--> (Classifier λ) --writes--> (Statistics λ)
                    ^                                         |
                    |_____________feedback <__________________|
```
* `FeatureMaker` starts with a trivial identity transform.
* `Classifier` holds a naive threshold rule.
* `Statistics` stores rolling accuracy.

### 6.2 Self-improvement cycle (simplified)
1. `Statistics` detects accuracy < 80 %  → triggers `tune` op.
2. `tune` spawns mutant `Classifier′` nodes with varied thresholds.
3. Competing classifiers vote; `mirror` op removes consistently under-performing variants.
4. `convolve` op folds best variant back into *canonical* `Classifier`.

The library provides only the **patterns** (`tune`, `vote`, `convolve`, `mirror`) — their existence in the graph lets the system refactor itself.

---

## 7 Other Use-case Sketches
| Domain | How λ helps |
|--------|------------|
| **Market simulation** | Prices, agents, and even the market rules are nodes; policies evolve via `gradient` rewrites reacting to profit signals. |
| **Generative art** | Shapes & colour rules self-modify using `phase` shifts to explore style space. |
| **Multi-agent planning** | Agents export intent nodes; `convolve` merges compatible intents into coalition plans. |
| **Explainable reasoning** | Because every rewrite is itself data, you can replay and audit the decision lineage. |

---

## 8 Getting Started (when code arrives)
```bash
pip install lambda-lib  # TODO once published
python -m lambda_lib.examples.simple_eval
```
*Until implementation lands, explore the contracts to understand the planned behaviour.*

---

## 9 Roadmap
1. **Minimal engine** executing first-order pattern rules.
2. **Pattern DSL** embedded in docstrings for readable rewrite specs.
3. **Graph visualiser** (SVG & interactive).
4. **Persistence layer** so λ worlds can be snapshotted and traded.
5. **Go runtime** sharing the same graph files for polyglot execution.

Contributions welcome — propose new ops as contract-only PRs and watch the system learn to implement itself!

---

© 2025 LambdaLib authors. MIT License.
