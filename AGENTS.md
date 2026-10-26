# Agent instructions — EvidenceGraph (Paper 4)

Read [`docs/EvidenceGraph_Methods.md`](docs/EvidenceGraph_Methods.md) before writing code. This folder is a **binding and scoring protocol for published claims**, not the first evidence graph and not a paper-agent.

Program build plan: [`../docs/BUILD_PLAN.md`](../docs/BUILD_PLAN.md). **Does not depend on S0 imaging fixtures.** Do not block on SciCap/SciGuard/NeuroInsight.

## Mission

Store source-anchored claims with obligatory scope, coexisting epistemic states, and optional method/run links. Score `(claim, source, span, scope)`. A citation is not support. Missing code is `unknown_not_assessed`, not a failed reproduction.

## Do not build

- “We introduce evidence graphs” (EVI, Al Manir et al. 2021; AskChem 2026).
- A Paper2Agent clone or MCP-of-papers.
- A stronger RAG as the product.
- A truth oracle or systematic-review bot.
- Restricted full text in the repo.
- Treating LLM extraction as gold.
- A live-run claim auditor (NEURA / Brain Researcher).

## Locked methods you must implement

| ID | Rule |
|---|---|
| E1 | `Supports` / `Contradicts` / `Qualifies` / `unknown_scope` / `none`. Incomparable scope → Qualifies, not Contradicts. |
| E2 | Epistemic states **coexist**. Missing artifacts → `unknown_not_assessed`. |
| E3 | `Claim → Method → optional CodeArtifact → optional WorkflowRun`. Assert execution only if tested. Count false reproduction. |
| E4 | Primary score = correct (claim, source, span, scope). No LLM-judge primary. |
| E5 | Paper-level holdout. Extraction ≠ gold. |

## Reuse (do not replace)

- [`schema/relation.yaml`](schema/relation.yaml)
- [`schema/epistemic_state.yaml`](schema/epistemic_state.yaml)
- [`schema/example_claim.yaml`](schema/example_claim.yaml)
- [`schema/score.schema.json`](schema/score.schema.json)

PROV / RO-Crate for optional runs. Europe PMC / Crossref for ingest. SciFact conventions for SUPPORT/REFUTE **baselines**, not as this graph’s relation set.

## Target tree

```text
schema/          # already present
ingest/resolve.py          # DOI/PMCID → metadata + license; refuse if not OA
extraction/     # later; v0 is hand-entered YAML
graph/store.py  # JSON/YAML store is enough; Neo4j not required
graph/query.py
evaluation/score.py
evaluation/items/          # gold items, paper-level split
corpus/pilot/manifest.yaml # DOI, license, retrieval date — no full text if disallowed
annotations/handbook.md
tests/test_relations.py
tests/test_score.py
pyproject.toml             # console_scripts: evidencegraph
```

## CLI

```text
evidencegraph ingest --doi 10.xxxx --license-check
evidencegraph load schema/example_claim.yaml
evidencegraph query --claim C001 --show-scope
evidencegraph evaluate --item evaluation/items/I001.yaml --pred predictions/I001.yaml
```

`ingest` must exit non-zero if the license is not redistributable. Never write restricted full text.

## Claim record

Follow [`schema/example_claim.yaml`](schema/example_claim.yaml). Required in v0:

- `claim_id`, `asserted_by`, `statement`
- `scope`: population, acquisition, method_identity, comparator, timepoint, outcome_definition (unknown allowed)
- `evidence_span.source` + offsets or paragraph id
- `relation`: `Supports` | `Contradicts` | `Qualifies` | `unknown_scope` | `none`
- `epistemic_states`: list, may contain several
- `workflow_run`: `unavailable` unless a logged run exists

## Relation decision (E1)

| Condition | relation |
|---|---|
| Same claim family, comparable scope, same direction | `Supports` |
| Same claim family, comparable scope, opposite direction | `Contradicts` |
| Same claim family, scopes not comparable | `Qualifies` |
| Scope fields insufficient | `unknown_scope` |
| Citation/paper exists, span does not license | `none` |

Do not infer support from citation existence. Do not equate methods that only share a clinical keyword.

## First vertical slice (must pass)

| Item | Gold |
|---|---|
| Finding sentence, matching cohort and protocol | attribution correct; `Supports` |
| Correct paper, span is background | `unsupported` / relation `none` |
| Two HS papers, different atlas or surgical vs community | `Qualifies`, not `Contradicts` |
| Code mentioned, no run | states include `unknown_not_assessed`; not `computationally_reproduced` |
| System asserts reproduced with no artifacts | `false_reproduction` true |

Hand-author these as YAML under `evaluation/items/`. No need for 20 papers in v0.

## Score

Implement [`schema/score.schema.json`](schema/score.schema.json). `attribution_correct` is true only if claim, source, span, **and** scope match gold. LLM-as-judge is forbidden as the sole arbiter.

## Tests

- `test_relations.py`: Qualifies vs Contradicts on a scope mismatch.
- `test_states.py`: missing code ≠ computationally_reproduced.
- `test_ingest_license.py`: mocked non-OA DOI is refused.
- Unset model API keys. Graph read path has no model.

## Boundaries

- Do not import SciCap/SciGuard/NAB as this paper’s method.
- Optional later: a NeuroInsight `workflow_run` id on a claim. That is a pointer, not novelty.

## Done when

- Five gold items load and score offline.
- License check refuses a mocked restricted DOI.
- API/export distinguishes machine-extracted (none in v0) from expert-entered.

Stop. Do not build a React explorer or a RAG stack until methods §5 is re-read. A JSON-LD dump is enough.
