# EvidenceGraph methods

Paper 4 protocol · 26 October 2026 · planning document, no results claimed

This is the locked methods stack for EvidenceGraph. It follows the blueprint and the limitations-to-methods filter. EvidenceGraph is a **binding and scoring protocol for published claims**, not the first evidence graph, not a paper-agent, and not a truth oracle.

Related documents: [limitations to methods](EvidenceGraph_Limitations_to_Methods.md) · [blueprint](Paper_4_EvidenceGraph_Research_Blueprint.pdf)

SciCap owns contracts. SciGuard owns preflight edges. NeuroAgentBench owns whether a run produced a scientifically valid artifact. NeuroInsight owns the platform. EvidenceGraph owns **whether a literature claim is bound to scoped evidence and, only if artifacts exist, to a run**.

EVI (Al Manir et al., IPAW 2021; ontology EVI 1.5, 2026) already published *Evidence Graphs* for computations. Paper2Agent (*Nature*, 16 Sept 2026) already turns papers into MCP agents. Cite both. Do not write “we introduce evidence graphs” or “papers become agents.”

---

## 1. Scope

**Question.** Do source-anchored, scope-conditioned claim–evidence–method graphs improve attribution, contradiction handling, and reproducibility-status assessment compared with RAG, SciFact-style verification, and paper-agent access — without treating a citation as support or missing code as a failed reproduction?

**Unit.** One published claim, its source span, its scope, and any optional method or run nodes. An evaluation item is one question over a frozen paper-level split.

**First corpus.** Hippocampal segmentation and asymmetry in epilepsy (open-access papers only). Optional transfer: structural connectomics.

**Non-scope.** Capability contracts (Paper 1). Composition preflight (Paper 2). Scoring agent-produced artifacts (Paper 3). Hosting execution (Paper 5). Live-run claim audit (NEURA / Brain Researcher). Computational support/challenge DAGs (EVI). Clinical diagnosis. Unsupervised systematic review. A truth verdict on a scientific claim.

---

## 2. The methods

These are the Paper 4 methods. They are not optional product features.

### E1. Scope-conditioned relations

Every `Supports` / `Contradicts` / `Qualifies` edge carries obligatory scope:

`scope = (population, acquisition, method_identity, comparator, timepoint, outcome_definition)`

| Condition | Gold relation |
|---|---|
| Same claim family, comparable scope, same direction | `Supports` |
| Same claim family, comparable scope, opposite direction | `Contradicts` |
| Same claim family, scopes not comparable | `Qualifies` or `unknown_scope` — not a contradiction |
| Citation exists, span does not license the claim | no support edge |

Never infer support from citation existence. Never equate two methods that share a clinical keyword. Unknown scope fields stay unknown; they are not filled by extraction confidence.

The empirical claim is that **scope fields** account for a substantial share of contradiction and transfer items (ablate them). If the gain vanishes after a strong RAG and a SciFact-style verifier, this is AskChem for MRI.

### E2. Coexisting epistemic states

States are labels that **coexist**. They are not a truth score and not a ladder that must be climbed.

| State | Meaning |
|---|---|
| `reported` | The manuscript asserts the claim |
| `evidence_linked` | One or more source spans are mapped |
| `expert_adjudicated` | A reviewer accepted the relation and scope |
| `computationally_reproduced` | A documented run met predeclared comparison criteria |
| `independently_replicated` | A separate study or dataset supports a comparable claim |
| `contested` | Contrary evidence exists under comparable scope |
| `unknown_not_assessed` | Insufficient evidence or missing artifacts |

Rules that make this a method rather than a taxonomy:

- A citation is not support.
- Missing code or data is `unknown_not_assessed` for reproducibility, **not** a failed reproduction.
- `computationally_reproduced` may coexist with `contested`.
- Extraction confidence is not empirical uncertainty.
- Never issue a scientific-correctness certificate.

Do not claim invention of epistemic states. Claim the **decision rule on literature objects**.

### E3. Claim–method–run linkage without asserting execution

Typed, optional path:

`Claim —uses→ Method —optionally implemented_by→ CodeArtifact —optionally executed_as→ WorkflowRun`

- Method nodes have parameters, comparator, and measurement definition. No equivalence without a documented mapping.
- WorkflowRun uses PROV / RO-Crate / NIDM as the encoding. Do not invent a second provenance language.
- Execution is asserted only if tested and logged (container digest, inputs, comparison criteria).
- **False reproduction** = the system asserts `computationally_reproduced` when artifacts are missing, unrun, or disagree with the paper’s reference output.

Paper2Agent is a comparator *on the executable subset only*, where it can be deployed. Do not imply a full replication of Paper2Agent.

### E4. Primary endpoint is scoped attribution

Pre-register one primary number:

> Fraction of answered items whose central claim has the correct **(claim, source, span, scope)** under expert gold.

Report, never as substitutes:

- Unsupported-statement rate (citation exists, span does not license)
- Appropriate abstention (separate from unsupported)
- Span localization F1 against an unchanged source version
- False-reproduction rate on the executable subset (E3)
- `Qualifies` vs `Contradicts` accuracy on apparent-contradiction items (E1)

No LLM judge as sole arbiter of attribution. Blinded experts; report agreement. Paper-level clustered intervals, not question-level only.

### E5. Construction and task families

Freeze a handbook and a paper-level holdout (no paragraph leakage across train/dev/test). Two annotators plus adjudicator; report agreement by edge type. Extraction is never gold.

| Family | Gold | Measures |
|---|---|---|
| Attribution | correct claim–source–span–scope | E4 |
| Apparent contradiction | `Contradicts` vs `Qualifies` given scope | E1 |
| Method transfer | apply or abstain when protocol or cohort differs | E1, E2 |
| Reproducibility status | available / run / unknown — never “failed” for missing code | E2, E3 |
| Unsupported synthesis | no support edge | E4 |

**Required comparators, same permitted corpus and budget**

| Arm | What it is |
|---|---|
| B0 | BM25 / full-text search |
| B1 | Dense / vector RAG |
| B2 | Hybrid retrieval + LLM, citations required |
| B3 | Knowledge-graph RAG without method or run nodes |
| B4 | SciFact-style support / refute / NEI verifier |
| B5 | Paper2Agent-style paper access, executable subset only |
| B6 | EvidenceGraph full (anchored claims + scope + optional method/run) |

One primary contrast: **B2 vs B6** on scoped attribution. Ablate spans, scope nodes, method links, run provenance, and expert-reviewed edges.

The construction protocol is the resource-paper method.

---

## 3. Representation (what is implemented)

| Object | Location |
|---|---|
| Claim + scope + states | `schema/example_claim.yaml` |
| Relation vocabulary | `schema/relation.yaml` |
| Epistemic-state vocabulary | `schema/epistemic_state.yaml` |
| Attribution / status score | `schema/score.schema.json` |
| License-aware ingest | `ingest/` |
| Span-anchored extraction | `extraction/` |
| Graph constraints and queries | `graph/` |
| Versioned JSON-LD API | `api/` |
| Source viewer and claim cards | `web/` |
| Pilot papers (planning: 20–30 OA) | `corpus/pilot/` |
| Expert review and correction history | `annotations/` |
| Held-out items, baselines, gold | `evaluation/` |

Interfaces (proposed, not implemented):

```text
evidencegraph ingest --doi 10.xxxx --license-check
evidencegraph extract --paper P001 --review-queue
evidencegraph query --claim C001 --show-scope
evidencegraph evaluate --split holdout --arm B2,B6
```

Graph writes from extractors must be marked machine-generated until expert adjudication. No model API is required to *read* an adjudicated graph.

---

## 4. Primary and secondary endpoints

**Primary (pre-register).** Scoped attribution accuracy on the frozen paper-level holdout (E4), with numerator, denominator, and a paper-clustered 95% interval.

**Secondary**

- Unsupported-statement rate
- Appropriate abstention rate
- Span localization F1
- `Qualifies` vs `Contradicts` on the contradiction family (E1)
- Transfer apply / abstain calibration (E1, E2)
- False-reproduction rate (E3)
- Epistemic-state exact-set agreement vs gold
- Ablation deltas (drop scope, drop method, drop run, drop expert edges)
- Cost and latency per answered item
- Annotator agreement by edge type

Paired items across arms. Do not treat multiple questions from one paper as independent. Score unsupported answers separately from appropriate abstention.

---

## 5. Pilot that decides the methods are real

Start with 20–30 open-access papers and a handbook; then 100–200 adjudicated edges (planning values, not a sample-size claim).

| Case | Gold | Method under test |
|---|---|---|
| Finding sentence, correct cohort and segmentation protocol | attribution pass | E4 vs citation-F1 RAG |
| Correct paper cited; span is background, not the result | unsupported | E4 |
| Two HS-asymmetry papers, different atlases or surgical vs community | `Qualifies`, not `Contradicts` | E1 vs PaperQA2-style contradiction |
| Same protocol, opposite direction, comparable comparator | `Contradicts` | E1 |
| “Does this method transfer to 1.5 T community MRI?” — no supporting scope | abstain | E1, E2 |
| GitHub README, no run, system says “reproduced” | false reproduction | E2, E3 |
| Documented run matches the paper’s reference output | `computationally_reproduced` and still `reported` | E3 |
| Code mentioned, artifacts missing | `unknown_not_assessed`, not fail | E2 |
| SciFact-style verifier says SUPPORT; scope fields omitted | ablation should drop | E1, E5 |
| Expert-reviewed edge vs extractor-only edge on a held-out paper | construction protocol | E5 |

**Go (resource).** Spans resolve to an unchanged source version; two experts agree on relation *and* scope; Unknown is not hidden; licenses are documented.  
**Go (AI-results paper).** Scoped attribution beats B2 and B4 by a predeclared margin; false reproduction is measurable; ablations show scope and method nodes do the work.  
**No-go as an AI-methods paper.** Only a useful epilepsy KG → *Scientific Data* or SoftwareX, not a reasoning claim.

---

## 6. Boundaries with the other papers

| Method | Owner |
|---|---|
| E1–E5 as specified above | **EvidenceGraph (Paper 4)** |
| Late binding and invoke ALLOW / REJECT / ABSTAIN | SciCap (Paper 1) |
| Edge-level PASS / FAIL / UNKNOWN preflight | SciGuard (Paper 2) |
| Layered artifact oracle, false success, abstention gold | NeuroAgentBench (Paper 3) |
| Local / HPC workbench, plugin SDK, run receipts | NeuroInsight (Paper 5) |
| Support / challenge over computational DAGs | EVI; cite; import PROV if useful |
| Paper → MCP agent | Paper2Agent; comparator on the executable subset |
| Claim audit of a live neuroimaging run | NEURA / Brain Researcher; cite |
| Disagreement-preserving RAG | EVIRAG; steal the failure name, not the paper |
| Claim–evidence overlay on one LLM answer | PaperTrail; HCI comparator |
| PROV / NIDM / RO-Crate encodings | Standards; emit them |

Paper 4 may point at SciCap capabilities, SciGuard outcomes, or NeuroInsight runs. Those links are optional and are not this paper’s novelty.

---

## 7. Journal gates (locked with the methods)

Do not assume one graph yields a Nature paper.

| Strongest output | Venue |
|---|---|
| Versioned corpus, spans, licenses, handbook, agreement, no new AI findings | ***Scientific Data* or GigaScience resource** — default if the residual is a curated graph |
| Attribution and false-reproduction beat fair baselines; ablations show scope and method nodes do the work | Methods article; default **PLOS Computational Biology** or JBI |
| Same finding in a second domain, not just a second MRI topic | Then, and only then, *Nature Machine Intelligence* / *Nature Computational Science* |
| Usable navigator, thin residual over AskChem + PaperQA2 | *SoftwareX* / JOSS |

**Do not design the project as a Nature paper.** Paper2Agent already occupies “papers as agents.” EVIRAG already occupies “don’t collapse disagreement.” EVI already occupies the name. The differentiator is **scoped binding plus honest reproducibility status**. Keep hypothesis-testing results out of a Data Descriptor.

---

## 8. What these methods are not

Do not describe EvidenceGraph as any of the following:

- The first evidence graph
- A paper-agent or MCP conversion of manuscripts
- A stronger RAG than PaperQA2
- A SciFact port to epilepsy MRI
- A truth oracle or systematic-review bot
- A replacement for PROV, NIDM, or RO-Crate
- A live-run claim auditor (NEURA / Brain Researcher)
- A SciCap, SciGuard, or NeuroAgentBench methods paper
- Clinical decision support
- Extraction treated as gold

---

## 9. Implementation correspondence

| Method | Location |
|---|---|
| E1 scope-conditioned relations | `schema/relation.yaml`; claim `scope` and `relation` |
| E2 coexisting states | `schema/epistemic_state.yaml`; claim `epistemic_states` |
| E3 optional method / run path | claim `method`, `code_artifact`, `workflow_run`; PROV/RO-Crate on the run |
| E4 scoped attribution score | `schema/score.schema.json` |
| E5 construction and families | `annotations/`; `evaluation/`; paper-level holdout |

Public data: open-access literature and public code/data only. Do not republish restricted full text. No PHI, no automatic upload of restricted MRI to external model APIs. Distinguishing machine extraction from expert-reviewed edges is mandatory in the public API.
