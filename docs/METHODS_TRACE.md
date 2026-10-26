# Methods trace — EvidenceGraph (Paper 4)

Planning document. No results claimed. No confirmatory numbers. Extraction is not gold.

This file cites the public substrate against locked methods **E1–E5** in [`EvidenceGraph_Methods.md`](EvidenceGraph_Methods.md). It does not replace that memo. There is no E6.

EVI (Al Manir, Niestroy, Levinson, and Clark, IPAW 2021; ontology EVI 1.5, 2026) already published Evidence Graphs as a PROV extension for support and challenge over computational DAGs. This folder is a binding and scoring protocol for published claims. It does not introduce evidence graphs.

---

## Citation stance

| System | What it already owns | Residual this folder tests |
|---|---|---|
| EVI (Al Manir et al., IPAW 2021; EVI 1.5, 2026) | The name *Evidence Graphs*; defeasible support/challenge over computations | Bind a published claim to scoped evidence; assert a run only if artifacts exist |
| SciFact / SciFact-Open (Wadden et al. 2020, 2022) | SUPPORT / REFUTE / NEI polarity from claim vs passage | Obligatory imaging scope so incomparable protocols are `Qualifies`, not `Contradicts` |
| AskChem (2026) | DOI- and quote-grounded `supports` / `contradicts` / `extends` / `derives_from` | Same polarity job without population / atlas / protocol fields |
| PaperQA2 / LitQA2 (2024); ScholarQA / OpenScholar / ScholarQABench (2025) | Cited answers; citation F1 and rubric fluency | Primary number is correct `(claim, source, span, scope)` under expert gold |
| Paper2Agent (Miao et al., *Nature*, 16 September 2026) | Papers as MCP agents on an executable subset | Attribution across papers without asserting execution |

Public code in this wave: `baselines/polarity.py` (B4, no scope), `baselines/bm25.py` (B0 on fixture spans only), `ingest/resolve.py` (local license fields, network off), and `ingest/europepmc.py` (URL builder; live call gated by `EG_LIVE_INGEST=1`). Locked scoring stays in `evaluation/score.py` and `evidencegraph/relations.py`. Additional corpus rows are fixtures (`fixture: true`, `not_a_published_doi: true`), not a 20-paper crawl.

---

## E1–E5 vs public tool

| Method | Public tool reused | Literature residual | Test |
|---|---|---|---|
| E1 | SciFact polarity (`baselines/polarity.py`) | `Qualifies` when cohort / atlas / protocol are incomparable | I003 |
| E2 | — | missing code = `unknown_not_assessed` | I004 |
| E3 | PROV / RO-Crate optional (`prov:` on JSON-LD export) | `Claim → Method → optional CodeArtifact → optional WorkflowRun` without asserting execution | I004 / I005 |
| E4 | ScholarQA / PaperQA2 (cited-answer habit, not reimplemented) | primary = `(claim, source, span, scope)` | I001 / I002 |
| E5 | EVI name occupancy | construction: `expert_entered`; `extraction_is_gold` false | all items |

---

## Per-method residual

### E1 — scope-conditioned relations

SciFact and AskChem already decide support or contradiction from claim and passage (or a typed citation edge). `baselines/polarity.py` reuses that habit: token overlap plus keyword polarity; **no scope**. On I003 (surgical + FreeSurfer vs community + ASHS) polarity is allowed to emit `Contradicts` or `Supports`. EvidenceGraph must emit `Qualifies`, not `Contradicts`, because population, acquisition, method identity, and comparator are not comparable.

### E2 — coexisting epistemic states

SciFact collapses to SUPPORT / REFUTE / NEI. A GitHub mention is not reuse. I004 keeps `unknown_not_assessed` when code is mentioned and no run is logged. That label is not a failed reproduction.

### E3 — claim–method–run without asserted execution

Paper2Agent binds tools that execute. EVI emits a graph when a computation runs. NIDM / PROV / RO-Crate encode a run. I004 and I005 store an optional method node and `workflow_run: unavailable`. Execution is not asserted. I005 scores `false_reproduction` when a system writes `computationally_reproduced` without artifacts. The JSON-LD dump may carry a PROV context; it does not invent a second provenance language.

### E4 — scoped attribution

ScholarQA and PaperQA2 score whether an answer is cited. I001 (finding span, matching scope) is `Supports` with attribution correct. I002 (same paper, background span) is unsupported / `none`. A citation is not support. No LLM judge is the primary arbiter.

### E5 — construction

EVI already occupies the product name. All five items are `origin: expert_entered` with `extraction_is_gold: false`. Machine extraction is not gold and is not present in v0. Paper-level holdout is the construction rule; these fixtures are the pilot slice, not a reported sample.

---

## What this file does not claim

- No E6.
- No sentence that this project introduces evidence graphs.
- No Paper2Agent clone and no MCP-of-papers.
- No React UI and no restricted full text.
- No fabricated accuracy, DOI, or evaluation number.
