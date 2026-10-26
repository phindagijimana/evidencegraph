# EvidenceGraph annotation handbook (v0)

Locked with E1–E5. Extraction is never gold. Two annotators plus an adjudicator own relation **and** scope. This file is the construction protocol for the five pilot items; it is not a result.

## 1. Units

One item is one question over a frozen paper-level split. The scored object is `(claim, source, span, scope)`. A citation is not support.

## 2. Hypothesis versus finding

| Span role | Use |
|---|---|
| `finding` | Results sentence that asserts the measured outcome under a stated cohort and protocol. May license `Supports` / `Contradicts` / `Qualifies`. |
| `hypothesis` | Proposed, not measured. Does not license a finding. |
| `background` | Anatomy, prior work, or motivation. Correct paper + background span = relation `none` (unsupported). |
| `citation_only` | Reference exists; no licensing span. Relation `none`. |

Do not promote a methods sentence or a related-work citation to a finding.

## 3. Scope fields (obligatory)

Every edge carries:

`population`, `acquisition`, `method_identity`, `comparator`, `timepoint`, `outcome_definition`

Unknown stays unknown. Do not fill a blank from extraction confidence.

## 4. Relation rule (E1)

| Condition | Relation |
|---|---|
| Same claim family, comparable scope, same direction | `Supports` |
| Same claim family, comparable scope, opposite direction | `Contradicts` |
| Same claim family, scopes not comparable | `Qualifies` — not a contradiction |
| Scope fields insufficient to decide | `unknown_scope` |
| Paper or citation exists, span does not license | `none` |

**Qualifies, not Contradicts**, when any deciding field differs: surgical versus community cohort; different atlas or segmentation protocol; different comparator (pathology-defined HS versus imaging-defined HS); different acquisition (for example 3 T research versus 1.5 T community) without a documented mapping.

**Contradicts** only when those deciding fields are known and comparable and the effect direction is opposite.

Never equate two methods that only share a clinical keyword (both say “hippocampus” or “HS”).

## 5. Epistemic states (E2)

States **coexist**. They are not a ladder and not a truth score.

| State | Meaning |
|---|---|
| `reported` | The manuscript asserts the claim |
| `evidence_linked` | One or more source spans are mapped |
| `expert_adjudicated` | A reviewer accepted the relation and scope |
| `computationally_reproduced` | A documented run met predeclared comparison criteria |
| `independently_replicated` | A separate study or dataset supports a comparable claim |
| `contested` | Contrary evidence exists under comparable scope |
| `unknown_not_assessed` | Insufficient evidence or missing artifacts |

Rules:

- Missing code or data ⇒ `unknown_not_assessed` for reproducibility. It is **not** a failed reproduction.
- Do not assign `computationally_reproduced` unless a logged run exists (container digest, inputs, comparison criteria).
- Asserting `computationally_reproduced` without artifacts is `false_reproduction`.
- Extraction confidence is not empirical uncertainty.
- Never issue a scientific-correctness certificate.

## 6. Claim–method–run (E3)

`Claim —uses→ Method —optionally implemented_by→ CodeArtifact —optionally executed_as→ WorkflowRun`

`workflow_run` is `unavailable` unless a logged run exists. PROV / RO-Crate / NIDM encode the run. Do not invent a second provenance language.

## 7. Origin (E5)

| Origin | Gold? |
|---|---|
| `expert_entered` | Eligible for gold after adjudication |
| `machine_extracted` | Never gold. Mark machine-generated until review. |

v0 has no extractor. All five items are `expert_entered` with `extraction_is_gold: false`.

## 8. Pilot item families

| Item | Family | Gold |
|---|---|---|
| I001 | attribution | Finding span, matching cohort and protocol; `Supports` |
| I002 | unsupported_synthesis | Correct paper, background span; `none` |
| I003 | apparent_contradiction | Surgical + FreeSurfer vs community + ASHS; `Qualifies` |
| I004 | reproducibility_status | Code mentioned, no run; `unknown_not_assessed` |
| I005 | reproducibility_status | System asserts reproduced with no artifacts; `false_reproduction` |

## 9. What not to do

- Do not treat LLM extraction as gold.
- Do not store restricted full text.
- Do not infer support from citation existence.
- Do not score missing code as failed reproduction.
