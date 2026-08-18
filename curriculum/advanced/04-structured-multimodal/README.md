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

## Key takeaway

**Multimodal RAG is not "send everything to a vision model." Route calculations, extracted observations, visual interpretation, and narrative retrieval through different evidence contracts.**
