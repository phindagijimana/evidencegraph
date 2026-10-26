# Limitations that can become methods

EvidenceGraph / Paper 4 · 26 October 2026

Same filter as SciCap, SciGuard, and NeuroAgentBench: a limitation is a method only if it yields a representation, decision rule, or evaluation protocol that still stands after SciFact, PaperQA2, ScholarQA, Paper2Agent, EVI, EVIRAG, AskChem, PaperTrail, ORKG, NIDM/PROV/RO-Crate, and NEURA/Brain Researcher are granted. The locked Paper 4 protocol is [`EvidenceGraph_Methods.md`](EvidenceGraph_Methods.md).

**Filter**

| Keep as a method | Discard as a feature gap |
|---|---|
| Scope-conditioned support / contradict / qualify | “First evidence graph” |
| Coexisting epistemic states; missing code is Unknown | “Neuroimaging is missing from SciFact” |
| Claim → method → optional run, without asserting reproduction | A KG plus a website |
| Primary number = scoped claim–source–span | Rubric score on a fluent cited answer |
| Task families existing benches cannot score | LLM-as-judge attribution; a systematic-review bot |

SciCap owns **contracts**. SciGuard owns **preflight edges**. NeuroAgentBench owns **how agent runs are scored**. NeuroInsight owns **the platform**. EvidenceGraph owns **how literature claims are bound to evidence, methods, and (when they exist) runs**. Do not republish M1–M4, G1–G5, or B1–B7 as Paper 4 methods.

The name is already taken. Al Manir, Niestroy, Levinson, and Clark (IPAW 2021; ontology still maintained, EVI 1.5, April 2026) published *Evidence Graphs* as a PROV extension for support/challenge over **computations**. Cite EVI. Do not write “we introduce evidence graphs.”

---

## 1. What the closest systems cannot do

| System | Limitation | Why it is not already EvidenceGraph |
|---|---|---|
| SciFact / SciFact-Open (2020, 2022) | SUPPORT / REFUTE / NEI against abstracts; rationale sentences. SciFact-Open already notes that evidence can support only a special case of a claim. | Closest evaluation convention. Residual: full-text methods, obligatory scope, reproducibility status, not a truth verdict. |
| SciClaim (EMNLP 2021) | Fine-grained claim knowledge graphs (entities, relations, attributes) from papers. | They extract experimental associations. Residual: method identity, executable artifacts, epistemic coexistence. |
| Evidence Inference | Intervention–comparator–outcome extraction from clinical trials. | Steal the ICO habit. Not neuroimaging method/provenance relations. |
| Scite | Citation contexts: supporting / contrasting / mentioning. | Citation polarity ≠ claim support once population or protocol differ. |
| ORKG / SciQA | Crowdsourced scholarly contribution graphs; SPARQL QA. | Structured comparisons exist. Residual: span-anchored evidence, run status, scoped contradiction. |
| Nanopublications / W3C PROV-O | Assertion + provenance primitives. | Reuse the encoding. Do not invent a competing assertion format. |
| NIDM / RO-Crate / Workflow Run RO-Crate | Neuroimaging and workflow provenance of **a run**. | Import as the run object. Residual: linking a *literature claim* to that object without asserting the run happened. |
| EVI Evidence Graphs (Al Manir et al., 2021; EVI 1.5, 2026) | Defeasible support/challenge over computational DAGs. Graphs are emitted when a computation runs. | Highest name collision. Different object: their graph is the run; yours is the literature claim. |
| PaperQA2 / LitQA2 (2024) | Agentic literature search; citation-backed answers; they already **find contradictions** in biology papers. | Strongest RAG/agent baseline. Residual: classify scope-mismatch vs genuine conflict; do not score answer fluency. |
| ScholarQA / OpenScholar / ScholarQABench (2025) | Multi-paper synthesis; citation F1; even a **Scholar-Neuro** slice. | They already do neuroscience literature QA. Residual: scoped attribution and reproducibility status, not rubric accuracy. |
| Paper2Agent (Miao et al., *Nature*, 16 Sept 2026) | A paper becomes an MCP agent; tools execute; multi-paper MCP connection is supported. | Highest 2026 blocker for “papers as agents.” Residual: cross-paper claim provenance and method-scope, not “can I run this paper.” |
| AskChem (2026) | 2.4M DOI- and quote-grounded chemistry claims; typed edges `supports` / `contradicts` / `extends` / `derives_from`. Expert-checked edge precision. | They already built a claim–evidence graph as infrastructure. Domain port is not a method. Residual: executable-run states and obligatory imaging scope. |
| EVIRAG (EMNLP 2026) | Names **epistemic collapse**: RAG compresses disagreement into one fluent answer. Claim-level disagreement graphs; ContradictionRecall; ViewpointCoverage. | They already made disagreement a first-class RAG objective. Residual: disagreement conditioned on **method/population comparability**, plus Unknown reproducibility. |
| PaperTrail (CHI 2026) | UI maps LLM-answer claims to source evidence: supported, unsupported, omitted. | They own claim–evidence *interface* provenance for Q&A. Residual: a typed literature graph, not an HCI overlay on one answer. |
| GraphRAG-on-SciFact (2025) | Claim–document–entity graph; still fails when evidence lives in methods/results, not the abstract. | Confirms the residual: methods text and protocol identity, not more hops. |
| NEURA / Brain Researcher (2026) | Claim cards and proof-carrying audit of **your** neuroimaging run. Six-level auditor; reproducibility ladder. | Different object: live analysis vs published literature. Cite; do not clone the run auditor. |

**One-sentence answers you will need.**

- EVI asks whether a **computation** is supported or challenged. EvidenceGraph asks whether a **published claim** is bound to scoped evidence and, only if artifacts exist, to a run.
- Paper2Agent asks whether a **paper can be executed**. EvidenceGraph asks whether a **claim can be attributed** across papers without inventing support or reproduction.
- PaperQA2 / ScholarQA ask whether an **answer is cited**. EvidenceGraph asks whether the **span and scope** actually license the claim.
- EVIRAG asks whether **disagreement is preserved** in the answer. EvidenceGraph asks whether two results **are comparable** before they are called a contradiction.
- SciFact asks whether an abstract **supports or refutes** a claim. EvidenceGraph does not issue a truth verdict.

---

## 2. Methods worth keeping (Paper 4)

### E1. Scope-conditioned relations (not NLI polarity)

**Limitation.** SciFact, Scite, PaperQA2, and AskChem treat support or contradiction as a property of a claim plus a passage (or a citation). SciFact-Open already saw special-case support. Hippocampal-asymmetry papers routinely “contradict” each other until segmentation protocol, atlas, pathology comparator, or surgical versus community cohort are bound.

**Method.** Every `Supports` / `Contradicts` / `Qualifies` edge carries obligatory scope:

`scope = (population, acquisition, method_identity, comparator, timepoint, outcome_definition)`

Decision rule:

| Condition | Gold relation |
|---|---|
| Same claim family, comparable scope, same direction | `Supports` |
| Same claim family, comparable scope, opposite direction | `Contradicts` |
| Same claim family, scopes not comparable | `Qualifies` (or `Unknown-scope`) — not a contradiction |
| Citation exists, span does not license the claim | no support edge |

Never infer support from citation existence. Never equate two methods that share a clinical keyword.

**Test.** Ablate scope fields (blueprint E6). The gain that remains after a strong RAG and SciFact-style verifier is the method. If the gain vanishes, you built AskChem for MRI.

### E2. Coexisting epistemic states; missing code is Unknown

**Limitation.** SciFact collapses a claim to SUPPORT / REFUTE / NEI. Paper2Agent and many paper-chat tools treat a GitHub link as reuse. EVI and Brain Researcher have states, but for a computation you ran. Literature tools still collapse “code mentioned” into “reproduced.”

**Method.** States are labels that **coexist**, not a truth score and not a ladder you must climb:

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
- `computationally_reproduced` may coexist with `contested` (external validity still open).
- Extraction confidence is not empirical uncertainty.
- Do not emit a scientific-correctness certificate.

Do not claim you invented epistemic states. Brain Researcher already has six claim-card states; EVI already has defeasible assertions. Claim the **decision rule on literature objects**: states coexist, and absence of artifacts is Unknown.

### E3. Claim–method–run linkage without asserting execution

**Limitation.** Paper2Agent binds a paper to MCP tools. NIDM and Workflow Run RO-Crate bind a run to artifacts. EVI emits an evidence graph when the computation happens. None of them bind a **published claim** to a method identity and an *optional* run receipt while remaining silent when the run does not exist.

**Method.** Typed, optional path:

`Claim —uses→ Method —optionally implemented_by→ CodeArtifact —optionally executed_as→ WorkflowRun`

- Method nodes have parameters, comparator, and measurement definition. No equivalence without a documented mapping.
- WorkflowRun uses PROV / RO-Crate / NIDM as the encoding. Do not invent a second provenance language.
- Execution is asserted only if tested and logged (container digest, inputs, comparison criteria).
- Primary error to count: **false reproduction** — the system says the result was reproduced when artifacts are missing, unrun, or disagree.

**Test.** Blueprint E5 on the executable subset (planning: 10–20 papers). Paper2Agent is the comparator *where it can be deployed*, on that subset only. Do not imply a full replication of Paper2Agent.

### E4. Primary endpoint is scoped attribution, not answer quality

**Limitation.** ScholarQABench scores rubric accuracy and citation F1 (including Scholar-Neuro). PaperQA2 scores LitQA2 and Wikipedia-style summaries. PaperTrail scores whether an HCI overlay changes trust. A fluent, cited answer can still mis-scope the population or treat a methods sentence as a finding.

**Method.** Pre-register one primary number:

> Fraction of answered items whose central claim has the correct **(claim, source, span, scope)** under expert gold.

Also report, never as substitutes:

- Unsupported-statement rate (citation exists, span does not license)
- Appropriate abstention (scored separately from unsupported)
- Span localization F1 against an unchanged source version
- False-reproduction rate on the executable subset

No LLM judge as sole arbiter of attribution. Blinded experts; report agreement. Paper-level clustered intervals, not question-level only.

This is the Paper 4 analogue of NeuroAgentBench’s “score the artifact, not the claim” — here, score the **binding**, not the prose.

### E5. Construction and task families existing benches cannot score

**Limitation.** SciFact cannot score method-scope contradiction. LitQA2 / ScholarQABench cannot score reproducibility status. Paper2Agent cannot score cross-paper attribution. EVIRAG scores disagreement preservation, not comparability.

**Method.** Freeze a handbook and a paper-level holdout (no paragraph leakage). Two annotators plus adjudicator; report agreement by edge type. Task families:

| Family | Gold | What it measures |
|---|---|---|
| Attribution | correct claim–source–span–scope | E4 |
| Apparent contradiction | `Contradicts` vs `Qualifies` given scope | E1 |
| Method transfer | apply / abstain when protocol or cohort differs | E1, E2 |
| Reproducibility status | available / run / unknown — never “failed” for missing code | E2, E3 |
| Unsupported synthesis | no support edge | E4 |

Fair baselines on the **same** permitted corpus and budget: BM25, vector RAG, hybrid RAG, KG-RAG without method/run nodes, SciFact-style verifier, Paper2Agent-style access on the executable subset. Ablate spans, scope nodes, method links, run provenance, and expert-reviewed edges (blueprint E6).

The construction protocol is part of the method. A resource paper can carry it even if the AI-results paper is separate.

---

## 3. Methods that belong next door

| Method | Owner |
|---|---|
| Late binding, invoke ALLOW / REJECT / ABSTAIN | SciCap (Paper 1) |
| Edge-level PASS / FAIL / UNKNOWN preflight | SciGuard (Paper 2) |
| Layered artifact oracle, false success, abstention gold | NeuroAgentBench (Paper 3) |
| Local/HPC workbench, plugin SDK, run receipts | NeuroInsight (Paper 5) |
| Support/challenge over computational DAGs | EVI; cite, import PROV relations if useful |
| Paper → MCP agent | Paper2Agent; cite as comparator |
| Claim audit of a live neuroimaging run | NEURA / Brain Researcher; cite |
| Disagreement-preserving RAG | EVIRAG; steal the failure name, not the paper |
| Claim–evidence overlay on one LLM answer | PaperTrail; HCI comparator, not the graph method |
| PROV / NIDM / RO-Crate encodings | Standards; emit them |

Paper 4 may *point at* SciCap capabilities, SciGuard outcomes, or NeuroInsight runs. Those links are optional and are not this paper’s novelty.

---

## 4. Feature gaps that look like methods but are not

- “SciFact has no epilepsy MRI.” Domain port.
- “We have more claims than SciFact” / “we built a website.”
- “First evidence graph.” False. EVI 2021; AskChem 2026; SciClaim 2021.
- “Better RAG than PaperQA2.” Then you are an IR paper, and ScholarQABench already has a neuroscience slice.
- “Papers become agents.” Paper2Agent, *Nature* 2026.
- “LLM-as-judge for attribution.” That is ScholarQA’s secondary scorer, not a method to copy.
- A systematic-review bot, or a truth oracle.
- Replacing PROV, NIDM, or RO-Crate.
- Auto-extracting the graph and treating extraction as gold.
- Recycling NeuroAgentBench tasks as literature questions.

---

## 5. Recommended methods stack

1. **Representation (E1 + E3):** source-anchored claims; scope-bearing edges; optional method and run nodes encoded in PROV / RO-Crate / NIDM.
2. **Decision rule (E2):** coexisting epistemic states; citation ≠ support; missing artifacts = Unknown; no truth certificate.
3. **Evaluation (E4 + E5):** scoped attribution as the primary number; contradiction / transfer / reproducibility-status families; fair RAG, SciFact-style, and Paper2Agent-subset baselines; component ablation.

**Venue split (do not conflate).**

| Strongest output | Venue |
|---|---|
| Versioned corpus, spans, licenses, handbook, agreement | *Scientific Data* or GigaScience resource — **no hypothesis results** |
| Attribution and false-reproduction beat fair baselines; ablations show scope and method nodes do the work | Methods article; default **PLOS Computational Biology** or JBI |
| Same finding in a second domain, not just a second MRI topic | Then, and only then, *Nature Machine Intelligence* / *Nature Computational Science* |
| Usable navigator, thin residual over AskChem + PaperQA2 | *SoftwareX* / JOSS |

Default: build the **curated graph and the evaluation**. Do not design a Nature paper. Paper2Agent already occupies “papers as agents” in 2026; EVIRAG already occupies “don’t collapse disagreement”; EVI already occupies the name. Your differentiator is **scoped binding plus honest reproducibility status**.

---

## 6. Pilot that decides these are real methods

| Case | Gold | Method under test |
|---|---|---|
| Finding sentence, correct cohort and segmentation protocol | attribution pass | E4 vs citation-F1 RAG |
| Correct paper cited; span is background, not the result | unsupported | E4 |
| Two HS-asymmetry papers, different atlases / surgical vs community | `Qualifies`, not `Contradicts` | E1 vs PaperQA2-style contradiction |
| Same protocol, opposite direction, comparable N and comparator | `Contradicts` | E1 |
| “Does this method transfer to 1.5 T community MRI?” — no supporting scope | abstain | E1, E2 |
| GitHub README, no run, agent says “reproduced” | false reproduction | E2, E3 |
| Documented run matches the paper’s reference output | `computationally_reproduced` + still `reported` | E3 |
| Code mentioned, artifacts missing | `unknown_not_assessed`, not fail | E2 |
| SciFact-style verifier says SUPPORT; scope fields omitted | ablation should drop | E1, E6 |
| Expert-reviewed edge vs extractor-only edge on held-out paper | construction protocol | E5 |

**Go.** Scoped attribution beats hybrid RAG and a SciFact-style verifier by a predeclared margin; false reproduction is measurable; Unknown is not scored as fail; two experts can agree on relation *and* scope.  
**No-go as an AI-methods paper.** Only a useful epilepsy KG. Then *Scientific Data* or SoftwareX, not a reasoning claim.

---

## 7. Decision

Turn **scope-conditioned relations**, **coexisting epistemic states**, **claim–method–run links that do not assert execution**, and **scoped attribution as the primary score** into the Paper 4 methods. Leave contracts to SciCap, preflight to SciGuard, run scoring to NeuroAgentBench, live-run claim audit to NEURA/Brain Researcher, computational evidence DAGs to EVI, and paper-agents to Paper2Agent.

That is the limitation set this field will grant EvidenceGraph. The graph is not the contribution. The binding rules and the score are.
