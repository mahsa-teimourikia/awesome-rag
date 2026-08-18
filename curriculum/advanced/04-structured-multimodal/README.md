# Advanced 04 — Structured and Multimodal RAG: Deterministic Data, OCR, and Visual Evidence

**Level:** Advanced  
**Estimated time:** 2–3 hours  
**Notebook:** [`04_structured_multimodal.ipynb`](04_structured_multimodal.ipynb)  
**Prerequisite:** Agentic RAG, evidence provenance, evaluation

---

## Why this lesson exists

Not every RAG question should be answered from embedded prose.

Examples:

```text
"What is the total risk for Acme?"
```

requires deterministic aggregation.

```text
"What warning appears in this dashboard region?"
```

requires visual/OCR evidence.

```text
"What does the policy require?"
```

requires text retrieval.

A robust system routes each operation to the appropriate evidence boundary.

![Modality routing](assets/modality-routing.svg)

---

## Learning objectives

After this lesson you should be able to:

- separate deterministic computation from model interpretation;
- preserve row/cell provenance for structured facts;
- treat OCR as uncertain extracted evidence;
- retain page/region locators for visual citations;
- explain when OCR is sufficient and when a vision model adds value;
- avoid arbitrary code execution as a default data-query mechanism;
- separate visual observation from model inference;
- route queries by operation and modality; and
- evaluate numeric, OCR, visual, and text evidence differently.

---

# Deep dive — Structured and Multimodal RAG

## Why text-only RAG is insufficient

Enterprise knowledge rarely exists only as paragraphs. Important evidence lives in:

- relational databases;
- spreadsheets;
- tables embedded in PDFs;
- charts and diagrams;
- screenshots;
- scanned forms;
- images;
- audio/video transcripts and frames.

A text-only ingestion pipeline often flattens these modalities into strings and loses structure. Structured and Multimodal RAG instead asks: **what representation, retrieval method, and evidence contract are appropriate for this information type?**

## Operation-first routing

Modality is only part of the decision. The required operation matters too.

```text
"What is the policy limit?"       → text retrieval
"Total exposure for customer X?"  → deterministic structured query
"What number is in this cell?"    → table/OCR extraction
"What trend does this chart show?"→ visual interpretation
```

The system should route by both **information source** and **operation semantics**.

## Structured RAG

Structured RAG retrieves or computes over schema-bearing data rather than unstructured chunks.

Common patterns include:

### Typed API / semantic layer

Expose business operations such as:

```text
get_customer_exposure(customer_id)
get_policy_limits(policy_id)
```

This is often the safest option because business semantics and authorization are encoded outside the model.

### Constrained query specification

The model emits a typed intent:

```json
{
  "dataset": "claims",
  "filters": [{"field": "customer_id", "op": "eq", "value": "C-17"}],
  "aggregation": {"field": "amount", "op": "sum"}
}
```

Trusted code validates and executes it.

### Text-to-SQL

Useful for flexible analytics, but it introduces schema exposure, query correctness, resource, and authorization risks. Use read-only credentials, row-level security, allowlists, query validation, timeouts, and—where appropriate—human review.

## Deterministic computation boundary

LLMs are useful for interpreting user intent and explaining results. They should not replace deterministic arithmetic.

```text
natural-language request
        ↓
validated structured operation
        ↓
database / dataframe / calculation
        ↓
exact result + provenance
        ↓
LLM explanation
```

This separation improves reproducibility and makes numeric errors diagnosable.

## Table understanding

Tables are not ordinary text. Flattening a table can destroy:

- row/column relationships;
- headers;
- merged cells;
- units;
- hierarchical structure.

Possible representations include:

- row-wise documents;
- table-level summaries;
- schema + cell coordinates;
- HTML/Markdown serialization;
- table embeddings;
- multimodal page representations.

The right representation depends on whether questions target individual cells, row filtering, aggregation, or semantic interpretation.

## OCR pipelines

OCR converts visual text into machine-readable text and often provides geometry.

A robust OCR record can include:

```text
asset_id
page
region/bounding_box
text
confidence
reading_order
engine/version
```

OCR remains valuable because it supports searchable text, coordinates, deterministic extraction, and lower-cost indexing. Its weaknesses include recognition errors, reading-order errors, and loss of visual semantics.

## Native multimodal retrieval

Multimodal RAG can index and retrieve images/pages directly using multimodal representations. Instead of converting every page to text first:

```text
page image → multimodal embedding → retrieve page/region → multimodal model
```

This can preserve layout, charts, handwriting, visual annotations, and spatial relationships that OCR-only pipelines lose.

The trade-off is greater compute cost and more difficult evaluation/provenance.

## Cross-modal retrieval

Multimodal systems may support:

```text
text query → image/page
image query → text
image query → image
text query → text + image
```

Cross-modal alignment is a central challenge: the embedding space must make the query and the relevant evidence comparable even when they use different modalities.

## Late fusion vs unified retrieval

Two broad architectures are common.

### Separate retrievers + fusion

```text
text retriever ─┐
table retriever ├→ fusion/rerank → context
image retriever ┘
```

Advantages: specialized indexes, easier diagnostics, independent tuning.

### Unified multimodal representation

```text
all modalities → shared representation → one retrieval layer
```

Advantages: simpler cross-modal search. Risks: modality-specific signals can be lost and evaluation becomes less transparent.

For enterprise systems, separate retrieval paths with explicit fusion are often easier to govern.

## Visual evidence granularity

Retrieving an entire 50-page PDF because one chart is relevant wastes context. Useful retrieval units include:

- page;
- figure;
- chart;
- table;
- image region;
- slide;
- video segment/frame.

Store locators so the answer can identify where the evidence came from.

## Observation, computation, and inference

These evidence types must remain distinct.

```text
Observed:  OCR reads "$5M" in region R3.
Computed:  SUM(rows 12–18) = $5M.
Inferred:  The chart appears to show accelerating growth.
```

They have different error modes. A model inference should not be presented with the certainty of a database calculation.

## Multimodal context construction

Context assembly must account for modality budgets. A final prompt may contain:

- extracted text;
- structured result objects;
- table snippets;
- selected images/pages;
- source metadata.

Avoid duplicating the same evidence as OCR text, page image, and generated summary unless there is a reason. Duplication consumes context and can overweight one source.

## Security

Structured and multimodal systems expand the attack surface:

- SQL/data authorization;
- hidden text in images;
- prompt injection inside documents/screenshots;
- EXIF/metadata leakage;
- sensitive OCR content;
- cross-tenant vector indexes;
- generated code execution.

Authorization must apply before evidence is exposed to the model. A multimodal model seeing a restricted page is already a data-access event.

## Evaluation

Use modality-specific metrics.

**Structured**
- query/operation correctness;
- row selection;
- arithmetic accuracy;
- units/currency handling;
- authorization.

**OCR/table extraction**
- character/word error;
- field accuracy;
- cell/header association;
- locator accuracy.

**Visual**
- evidence retrieval recall;
- chart/diagram interpretation accuracy;
- region grounding;
- unsupported visual inference.

**End-to-end**
- claim support across modalities;
- citation/locator completeness;
- contradiction handling;
- latency/cost.

## Architecture selection

Use OCR-first when the task is predominantly textual extraction. Use native multimodal retrieval when visual layout and non-textual information are essential. Use structured execution when the task is a database operation or calculation. Many real systems combine all three.

The design goal is not maximum modality support. It is to preserve the strongest available evidence representation for each task.

---

# Notebook companion

The sections below connect the theory above to the executable notebook, identify deliberate simplifications, and highlight production gaps.

# 1. What the notebook actually implements

The folder contains:

```text
README.md
04_structured_multimodal.ipynb
```

There is no `lab.py` and no enterprise notebook at the path referenced by the old README.

The notebook demonstrates:

1. deterministic Python aggregation over `TableRow`;
2. OCR regions with confidence and bounding boxes;
3. `create_pandas_dataframe_agent`;
4. a mocked multimodal message.

---

# 2. Deterministic computation first

The strongest part of the notebook is:

```python
total = sum(...)
```

with exact cited rows.

For numeric questions:

```text
authorized rows
    ↓
validate schema / units
    ↓
deterministic filter & calculation
    ↓
result + row provenance
    ↓
optional natural-language explanation
```

Do not ask an LLM to independently calculate a material financial result when code/SQL can calculate it exactly.

---

# 3. Important correction: Pandas code agents are not the default "safe math" architecture

The notebook says:

> use `create_pandas_dataframe_agent` for safe math

but then enables:

```python
allow_dangerous_code=True
```

This agent can execute generated Python.

That is not a safe default production boundary.

For production, prefer:

- predefined aggregation functions;
- validated query specifications;
- parameterized SQL;
- semantic-layer APIs;
- allowlisted dataframe operations.

Use code execution only in a genuinely isolated sandbox with strict resource, network, filesystem, and credential controls.

![Structured data boundary](assets/structured-data-boundary.svg)

---

# 4. OCR is useful, not obsolete

The notebook frames the choice too strongly as:

```text
legacy OCR bad → pass raw images to VLM
```

The better decision is operation-dependent.

OCR is often preferable when you need:

- text extraction;
- searchable text;
- stable coordinates;
- deterministic field pipelines;
- lower cost.

Vision-language models add value when interpretation depends on:

- layout;
- chart structure;
- spatial relationships;
- visual annotations;
- non-textual elements.

A robust multimodal pipeline may use both.

---

# 5. OCR provenance

An OCR result should carry:

```text
asset_id
page
bounding_box
text
confidence
engine/version
source checksum
```

A number without a location is difficult to verify.

Low-confidence extraction should trigger:

```text
review
re-extraction
alternate parser
abstention
```

—not a fabricated value.

---

# 6. Observation vs inference

Distinguish:

### Observation

```text
OCR region contains "$5M"
```

### Inference

```text
This likely represents Q3 revenue.
```

### Deterministic result

```text
SUM(authorized rows) = $140,000
```

![Evidence types](assets/evidence-types.svg)

The answer should not blur these categories.

---

# 7. Structured data security

For SQL/dataframe access:

- enforce tenant scope outside model-generated text;
- prefer database row-level security or trusted views;
- bind parameters;
- allowlist operations;
- limit rows/time;
- audit query/result IDs.

A model-generated `WHERE tenant = ...` clause is not a security boundary.

---

# 8. Visual claims need visual locators

For images/PDFs, retain:

```text
asset ID
page/frame
bounding box or region ID
source version
```

If a multimodal model creates an interpretation, label it as model-derived rather than pretending it is a measured database fact.

---

# 9. Evaluation by modality

| Evidence type | Primary checks |
|---|---|
| Structured rows | row selection, arithmetic, units, authorization |
| OCR | transcription accuracy, confidence calibration, region locator |
| Image/chart | interpretation accuracy, locator, numeric caution |
| Text | retrieval quality, claim support, citations |
| Combined | no double-counting, provenance completeness |

---

# 10. Exercises

1. Add EUR and USD rows and block aggregation without an explicit conversion policy.
2. Add a low-confidence OCR amount and route it to review.
3. Replace the dataframe agent with a typed aggregation function.
4. Define a `QuerySpec` for allowed filters and aggregations.
5. Add an image-derived claim and require a region locator.
6. Label each final claim as `computed`, `observed`, or `inferred`.
7. Add two tenants with the same account name and prove row isolation.

---

# 11. Checkpoint

1. Why should deterministic calculations happen outside the LLM?
2. Why is `allow_dangerous_code=True` not a production safety guarantee?
3. When is OCR preferable to a VLM?
4. What must an OCR citation contain?
5. What is the difference between observation and inference?
6. Where should row-level authorization be enforced?
7. How should numeric visual estimates be treated?
8. Why are modality-specific evaluation metrics necessary?

---

## What comes next

### [Advanced 05 — Adaptive RAG](../05-adaptive-rag/README.md)

Route requests to the cheapest reliable retrieval/data path instead of sending every question through one pipeline.

---

## References

- Pydantic — [Models](https://docs.pydantic.dev/latest/concepts/models/)
- PostgreSQL — [Row Security Policies](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- LangChain experimental Pandas agent — use only with explicit code-execution risk controls
- NIST — [AI RMF](https://www.nist.gov/itl/ai-risk-management-framework)

---
- Abootorabi et al. — [Ask in Any Modality: A Comprehensive Survey on Multimodal RAG](https://arxiv.org/abs/2502.08826)
- Gao et al. — [Scaling Beyond Context: Multimodal RAG for Document Understanding](https://arxiv.org/abs/2510.15253)

## Key takeaway

**Multimodal RAG is not "send everything to a vision model." Route calculations, extracted observations, visual interpretation, and narrative retrieval through different evidence contracts.**
