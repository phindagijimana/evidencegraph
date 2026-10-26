# EvidenceGraph literature map

**Paper 4 — binding and scoring protocol for published claims**  
Scoping review and novelty matrix · 26 October 2026 · search cutoff aligned with the locked methods memo

**Status.** Planning map for claim-setting. Not a PRISMA systematic review. Not a finding that EvidenceGraph works. No confirmatory numbers. Bibliographic metadata must be re-checked and locked before any manuscript submission. Do not treat this file as gold extraction.

**Bottom line.** EVI already published *Evidence Graphs* (Al Manir, Niestroy, Levinson, and Clark, IPAW 2021; ontology EVI 1.5, 2026) for support and challenge over **computations**. AskChem already ships a large claim–evidence graph. Paper2Agent already turns papers into MCP agents. SciFact, PaperQA2, ScholarQA, EVIRAG, PaperTrail, ORKG, and NEURA/Brain Researcher already occupy verification, cited QA, disagreement-preserving RAG, HCI overlays, contribution graphs, and live-run audit. The residual that still looks testable is **scope-conditioned relations**, **coexisting epistemic states on literature objects**, and **scoped attribution** `(claim, source, span, scope)` — not a new graph product and not a paper-agent.

---

## Five literature updates

1. **EVI already owns the name.** Al Manir et al. (IPAW 2021; EVI 1.5, 2026) published Evidence Graphs as a PROV extension for defeasible support/challenge over computational DAGs. A literature-claim binder cannot be described as introducing evidence graphs. Residual: bind a *published claim* to scoped evidence and, only if artifacts exist, to a run.

2. **Paper2Agent already occupies “papers become agents.”** Miao et al. (*Nature*, 16 September 2026) convert papers and code into MCP tools. Residual: cross-paper claim attribution and method-scope, not executable paper access.

3. **Support/refute polarity is already a product.** SciFact / SciFact-Open (SUPPORT / REFUTE / NEI) and AskChem (`supports` / `contradicts` / `extends` / `derives_from`) score passage or citation polarity. Hippocampal-sclerosis papers often look contradictory until atlas, cohort, and comparator are bound. Residual: obligatory scope so incomparable protocols are `Qualifies`, not `Contradicts`.

4. **Cited literature QA already includes neuroscience.** PaperQA2 / LitQA2 and ScholarQA / OpenScholar / ScholarQABench (including a Scholar-Neuro slice) score fluent, cited answers. Residual: the primary number is correct `(claim, source, span, scope)` under expert gold, not citation F1 or rubric fluency.

5. **Disagreement, provenance, and live-run audit already exist.** EVIRAG names epistemic collapse; PaperTrail overlays claim–evidence on one LLM answer; ORKG stores contributions; NIDM / PROV / RO-Crate encode runs; NEURA / Brain Researcher audit a live neuroimaging analysis. Residual: states **coexist** on literature objects; missing code is `unknown_not_assessed`, not a failed reproduction; `Claim → Method → optional CodeArtifact → optional WorkflowRun` does not assert execution.

---

## 1. Search protocol

### 1.1 Sources and clusters

Web search over publisher sites, arXiv, ACL Anthology, PubMed/PMC, and official specifications, using the Paper 4 Boolean clusters plus snowball from the locked methods and limitations memos.

| Cluster | Query family | Meant to catch |
|---|---|---|
| A | scientific claim verification / fact checking / SciFact / evidence inference | SciFact, SciFact-Open, SciClaim, Evidence Inference |
| B | literature QA / RAG / contradiction / citation-backed answer | PaperQA2, ScholarQA, GraphRAG-on-SciFact, EVIRAG |
| C | evidence graph / claim graph / nanopublication / ORKG | EVI, AskChem, ORKG, SciClaim |
| D | paper agent / MCP / executable paper | Paper2Agent |
| E | PROV / NIDM / RO-Crate / workflow run crate | run encodings |
| F | neuroimaging claim audit / reproducibility ladder | NEURA, Brain Researcher |
| Extra | Scite citation polarity; PaperTrail HCI overlay | citation ≠ support; gap vs a typed graph |

### 1.2 What this map is not

- Not an exhaustive ACM / IEEE / PubMed screen with recorded inclusion counts.
- Not a claim that 2026 preprints will remain the version of record.
- Not extracted gold. Extraction is never gold (E5).
- Peer-review status of 2026 systems named in the methods memo must be rechecked at submission.
- No DOIs are invented here. Where a DOI is not locked in a methods memo or a public standard URL, the work is cited by name and venue only.

### 1.3 Threat levels

| Level | Meaning for EvidenceGraph |
|---|---|
| **Blocker** | Already implements the object this folder would otherwise call novel. Do not claim that object. |
| **High** | Same job, different encoding. Must be a baseline or a hard differentiator. |
| **Must-cite baseline** | Fair experimental comparator. |
| **Adjacent** | Method or evaluation lesson. |
| **Reuse** | Emit or import this standard; do not replace it. |

---

## 2. Required systems

### 2.1 SciFact / SciFact-Open (2020, 2022) — must-cite evaluation convention

SciFact verifies claims against abstracts with SUPPORT / REFUTE / NEI and rationale sentences. SciFact-Open already notes that evidence can support only a special case of a claim.

**Not already EvidenceGraph.** Abstract-level polarity is not obligatory imaging scope, not a reproducibility state, and not a truth verdict this folder will issue. Steal the evaluation habit (support / refute / not enough information as **baseline B4**). Do not adopt SUPPORT/REFUTE as this graph’s relation set. The locked set is `Supports` / `Contradicts` / `Qualifies` / `unknown_scope` / `none`.

### 2.2 ScholarQA / PaperQA2 (2024–2025) — strongest RAG/QA baselines

PaperQA2 / LitQA2: agentic literature search with citation-backed answers; already used to surface contradictions in biology papers. ScholarQA / OpenScholar / ScholarQABench: multi-paper synthesis, citation F1, and a Scholar-Neuro slice.

**Not already EvidenceGraph.** They ask whether an **answer is cited**. This folder asks whether the **span and scope** license the claim. A fluent cited answer can still treat a methods sentence as a finding or transfer a surgical-HS result to a community 1.5 T protocol. PaperQA2 is the honest contradiction-finding baseline; ScholarQA is the honest cited-QA baseline (B2). Do not score answer fluency as the primary number.

### 2.3 Paper2Agent (Miao et al., *Nature*, 16 September 2026) — blocker for paper-agents

A paper becomes an MCP agent; tools execute; multi-paper MCP connection is supported.

**Not already EvidenceGraph.** Paper2Agent asks whether a **paper can be executed**. This folder asks whether a **claim can be attributed** across papers without inventing support or reproduction. Paper2Agent is comparator **B5 on the executable subset only**. Do not imply a full replication, and do not write “papers become agents.”

### 2.4 EVI Evidence Graphs (Al Manir et al., IPAW 2021; EVI 1.5, 2026) — blocker for the name

Defeasible support/challenge over computational DAGs. Graphs are emitted when a computation runs. Ontology still maintained.

**Highest name collision.** EVI asks whether a **computation** is supported or challenged. This folder asks whether a **published claim** is bound to scoped evidence and, only if artifacts exist, to a run. Cite EVI. Import PROV relations if useful. Do not write that this project introduces evidence graphs.

### 2.5 AskChem (2026) — blocker for “we built a claim–evidence graph”

DOI- and quote-grounded chemistry claims; typed edges `supports` / `contradicts` / `extends` / `derives_from`; expert-checked edge precision. A domain port of AskChem to epilepsy MRI is not a method.

**Residual.** Obligatory imaging scope (population, acquisition, method identity, comparator, timepoint, outcome definition) and executable-run states. If scoped attribution vanishes after AskChem-style edges plus a strong RAG, this is AskChem for MRI.

### 2.6 EVIRAG (EMNLP 2026) — blocker for “we preserve disagreement”

Names **epistemic collapse**: RAG compresses disagreement into one fluent answer. Claim-level disagreement graphs; ContradictionRecall; ViewpointCoverage.

**Residual.** Disagreement conditioned on **method/population comparability**, plus Unknown reproducibility. Steal the failure name (epistemic collapse). Do not republish EVIRAG’s disagreement-preservation paper.

### 2.7 PaperTrail (CHI 2026) — HCI comparator, not the graph method

UI maps LLM-answer claims to source evidence: supported, unsupported, omitted.

**Residual.** A typed literature graph with scope and optional method/run nodes, not an overlay on one model answer. Source-span viewer later is enough; a React explorer is out of v0.

### 2.8 ORKG / SciQA — must-cite contribution graphs

Crowdsourced scholarly contribution graphs and SPARQL QA.

**Residual.** Span-anchored evidence, run status, and scoped contradiction. Structured comparisons exist. Do not rebuild ORKG.

### 2.9 NIDM / PROV / RO-Crate — reuse as the run encoding

W3C PROV-O and nanopublications: assertion + provenance primitives. NIDM and Workflow Run RO-Crate: neuroimaging and workflow provenance of **a run**.

**Reuse.** Emit these encodings on `WorkflowRun`. Do not invent a second provenance language. Residual: linking a *literature claim* to that object **without asserting the run happened**.

### 2.10 NEURA / Brain Researcher (2026) — live-run auditor, different object

Claim cards and proof-carrying audit of **your** neuroimaging run. Six-level auditor; reproducibility ladder.

**Different object.** Live analysis versus published literature. Cite; do not clone the run auditor. Brain Researcher already has claim-card states. This folder claims the **decision rule on literature objects**: states coexist, and absence of artifacts is Unknown.

---

## 3. Adjacent systems (do not over-claim against them)

| System | Lesson | Residual |
|---|---|---|
| SciClaim (EMNLP 2021) | Fine-grained claim KGs from papers | Method identity, executable artifacts, epistemic coexistence |
| Evidence Inference | ICO from clinical trials | Steal ICO habit; not imaging method/provenance |
| Scite | Citation supporting / contrasting / mentioning | Citation polarity ≠ claim support once protocol differs |
| GraphRAG-on-SciFact (2025) | Claim–document–entity graph still fails when evidence is in methods | Methods text and protocol identity, not more hops |
| Nanopublications | Assertion + provenance | Reuse encoding |

---

## 4. Residual (what can still be a method)

After granting every system above, three rules remain. They are the locked methods E1, E2+E3, and E4 — not a new ecosystem.

| Residual | Locked method | What existing systems do instead |
|---|---|---|
| Scope-conditioned relations | E1 | SciFact / AskChem / Scite / PaperQA2 treat support or contradiction as claim+passage (or citation). Incomparable atlas or surgical vs community cohort must be `Qualifies`, not `Contradicts`. Insufficient scope fields stay `unknown_scope`. |
| Coexisting epistemic states; missing code is Unknown | E2 | SciFact collapses to SUPPORT/REFUTE/NEI. Paper-chat tools treat a GitHub link as reuse. Missing code or data is `unknown_not_assessed`, **not** a failed reproduction. |
| Claim → method → optional run, no asserted execution | E3 | Paper2Agent binds tools; NIDM/RO-Crate bind runs; EVI emits a graph when the computation happens. False reproduction = asserting `computationally_reproduced` without artifacts. |
| Primary number = scoped attribution | E4 | ScholarQABench and PaperQA2 score citations and rubrics. Gold is correct `(claim, source, span, scope)`. No LLM-judge primary. |
| Task families existing benches cannot score | E5 | Attribution, apparent contradiction, transfer abstain, reproducibility status, unsupported synthesis. Extraction is never gold. Paper-level holdout. |

**Construction protocol.** Two annotators plus adjudicator; report agreement by edge type; freeze a handbook. Machine-extracted edges (none in v0) stay marked machine-generated until expert adjudication.

---

## 5. What would not be novel (do not write these sentences)

- “We introduce evidence graphs.”
- “We introduce the first evidence graph for science / MRI / epilepsy.”
- “Papers become agents.”
- “A stronger RAG than PaperQA2.”
- “SciFact for epilepsy MRI.”
- “We preserve disagreement in RAG answers.” (EVIRAG)
- “We overlay claims on an LLM answer.” (PaperTrail)
- “We audit live neuroimaging runs.” (NEURA / Brain Researcher)
- “We replace PROV, NIDM, or RO-Crate.”
- “Extraction is gold.”

---

## 6. Required experimental baselines (same permitted corpus)

| Arm | What it is | Isolates |
|---|---|---|
| B0 | BM25 / full-text search | Lexical retrieval |
| B1 | Dense / vector RAG | Embedding retrieval |
| B2 | Hybrid retrieval + LLM, citations required | Strongest cited QA (PaperQA2 / ScholarQA class) |
| B3 | Knowledge-graph RAG without method or run nodes | Graph without E3 |
| B4 | SciFact-style support / refute / NEI verifier | Polarity without scope |
| B5 | Paper2Agent-style paper access, executable subset only | Execution access vs attribution |
| B6 | Full binder: anchored claims + scope + optional method/run | Incremental methods |

Primary contrast later: **B2 vs B6** on scoped attribution. Ablate spans, scope nodes, method links, run provenance, and expert-reviewed edges. v0 does not run these arms. v0 only loads and scores five hand-authored gold items.

---

## 7. Seed bibliography (names and venues only unless already a public standard)

Do not treat the following as a locked reference list. Export into a citation manager and lock author/volume/page/DOI before submission. No DOIs are minted here.

### Claim verification and graphs

1. Wadden et al. (2020). SciFact. EMNLP.
2. Wadden et al. (2022). SciFact-Open.
3. SciClaim (EMNLP 2021). Fine-grained claim knowledge graphs.
4. Evidence Inference (clinical ICO extraction).
5. Al Manir, Niestroy, Levinson, and Clark (2021). Evidence Graphs. IPAW. Ontology EVI 1.5 (2026).
6. AskChem (2026). DOI- and quote-grounded chemistry claim graph.
7. ORKG / SciQA. Open Research Knowledge Graph.

### Literature QA, disagreement, HCI

8. PaperQA2 / LitQA2 (2024).
9. ScholarQA / OpenScholar / ScholarQABench (2025), including Scholar-Neuro.
10. EVIRAG (EMNLP 2026). Epistemic collapse; ContradictionRecall; ViewpointCoverage.
11. PaperTrail (CHI 2026). Claim–evidence overlay on one LLM answer.
12. GraphRAG-on-SciFact (2025).
13. Scite. Citation supporting / contrasting / mentioning.

### Agents, encodings, live-run audit

14. Miao et al. (2026). Paper2Agent. *Nature*, 16 September 2026.
15. W3C PROV-O. https://www.w3.org/TR/prov-o/
16. RO-Crate. https://www.researchobject.org/ro-crate/specification
17. NIDM. Neuroimaging Data Model; import as the run object.
18. Workflow Run RO-Crate. Run provenance encoding.
19. NEURA / Brain Researcher (2026). Live neuroimaging claim audit.
20. Nanopublications. Assertion + provenance primitives.

---

## 8. Open questions before the novelty claim is frozen

1. Does AskChem already store enough method/population structure that an imaging port is only a domain annotation? Read the edge schema before claiming E1.
2. Does EVI 1.5 already allow a literature-claim node, or only computational artifacts? If the former, import rather than parallel.
3. Can SciFact-Open’s “special case of a claim” be scored as `Qualifies` without new labels? If yes, E1 must still show obligatory *imaging* scope fields do work that generic hedges do not.
4. How much of Scholar-Neuro already requires methods-section evidence? If most gold is already span-localized, E4’s increment is scope, not spans.
5. Is there an OA hippocampal-asymmetry / HS corpus large enough for a paper-level holdout without restricted full text? v0 uses hand-authored fixtures only.

---

**Decision for the research program.** Build a **binding and scoring protocol**, not a graph brand. If B6 does not beat B2/B4 on scoped attribution, and ablations do not show scope and method nodes doing the work, publish a curated OA resource (*Scientific Data* / GigaScience) or thin software (SoftwareX / JOSS). Do not design a Nature paper. EVI already occupies the name; Paper2Agent already occupies paper-agents; EVIRAG already occupies disagreement preservation.
