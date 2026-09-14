# 05 — Capstone: Enterprise Knowledge Assistant

**Level:** Beginner  
**Estimated time:** 120–180 minutes  
**Scenario:** Enterprise Knowledge Assistant for Northstar Technologies  
**Notebook:** [`05_enterprise_rag_capstone.ipynb`](05_enterprise_rag_capstone.ipynb)  
**Prerequisite:** [04 — Citations and Abstention](../04-citations-abstention/README.md)

---

## Why this Capstone exists

The previous courses in the Beginner track broke the Retrieval-Augmented Generation (RAG) architecture down into isolated components:
1. Grounding LLM generations in external evidence.
2. Inspecting retrieval independently from generation.
3. Controlling retrieval units through chunking.
4. Validating citations and forcing abstention.

However, enterprise RAG is not simply calling `chain.invoke()`. A robust system requires:
* An **ingestion pipeline** that respects document structure.
* A **real vector store** that persists embeddings.
* An **explicit orchestration layer** that exposes retrieval, grounding, generation, and validation as observable steps.
* A **quantitative evaluation** framework that isolates retrieval failures from generation failures.

This capstone integrates all these principles into a single, cohesive proof-of-concept.

---

## The Scenario

You are building an internal **Enterprise Knowledge Assistant** for a fictional company called **Northstar Technologies**.

The assistant must answer questions across multiple departments (HR, Engineering, Finance, Security, and Support). To make this realistic, we have provided a synthetic knowledge base (`data/knowledge_base/`) containing documents with real-world enterprise complexities:

1. **Version-Sensitive Data**: The corpus contains both the 2024 and 2026 Parental Leave policies. The model must rely on metadata (like `Effective Date` or `Status`) to answer correctly, rather than synthesizing the two.
2. **Conflicting Evidence**: Standard and Enterprise SLAs have different communication rules. If a user asks a vague question ("How often do P1 customers get updates?"), the system must recognize the conflict and abstain, rather than hallucinating an average.
3. **Multi-Source Synthesis**: Some incidents require the system to pull the `payments_incident_runbook.md` (Engineering) and cross-reference it with the `enterprise_sla.md` (Support).
4. **Missing Information**: The system must gracefully handle unanswerable queries (e.g., "Who is the CEO?") when the corpus genuinely does not contain the answer.

---

## The Architecture

Unlike simple prototypes that wrap ingestion, retrieval, and generation into a single opaque `chain.invoke()` call, this capstone forces you to build an **Explicit Orchestration Pipeline**:

```text
User Query
    ↓
retrieve_candidates(query, top_k)
    ↓
build_evidence_context(candidates)
    ↓
generate_decision(query, context)  ← Pydantic structured output
    ↓
validate_decision(decision, evidence_map)
    ↓
render_response()
```

By decoupling these steps, you can independently test whether a failure is due to a retrieval miss (the documents weren't found) or a generation failure (the model hallucinated or failed to abstain).

---

## Evaluation & Observability

Enterprise RAG requires empirical evaluation. We have included a **Golden Dataset** (`data/evaluation/golden_dataset.json`) featuring 30+ QA pairs spanning various categories: `single_source`, `multi_source`, `unanswerable`, `version_sensitive`, and `conflicting_evidence`.

You will learn how to measure:
* **Retrieval Recall@K**: Did the right document make it into the context window?
* **Citation Validity**: Did the model invent a citation ID that wasn't in the evidence map?
* **Answerability Accuracy**: Did the model successfully abstain when expected?

---

## Learning objectives

After completing this capstone, you should be able to:

1. **Ingest structured documents:** Implement structure-aware Markdown chunking.
2. **Orchestrate explicit RAG:** Expose every step of the pipeline rather than hiding it in an opaque chain.
3. **Use real tooling:** Integrate real embeddings (`langchain-huggingface`) and a local vector store (`Chroma`).
4. **Implement robust generation:** Use Pydantic structured outputs and a real LLM (`OpenAI`) for generation and citation mapping.
5. **Evaluate empirically:** Use a golden dataset to evaluate retrieval (`Recall@K`) separately from generation.

---

## Project Structure

This capstone models a proper software engineering project, rather than throwing all code into a single notebook:

* `data/knowledge_base/`: The synthetic Markdown documents for Northstar Technologies.
* `data/evaluation/`: The golden dataset containing QA pairs to evaluate the pipeline.
* `scripts/`: Demonstration scripts showing how synthetic data can be programmatically generated.
* `src/`: The core application modules (`config.py`, `ingestion.py`, `chunking.py`, `retrieval.py`, `generation.py`, `validation.py`, `evaluation.py`).
* `05_enterprise_rag_capstone.ipynb`: The main orchestration notebook that pulls the pipeline together.

## Getting Started

1. Copy `.env.example` to `.env` and insert your OpenAI API key.
2. Install the requirements: `pip install -r requirements.txt`.
3. Open `05_enterprise_rag_capstone.ipynb` and step through the architecture.
