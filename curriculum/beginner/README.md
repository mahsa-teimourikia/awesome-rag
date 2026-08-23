# Beginner RAG Curriculum

**Track goal:** Build a correct mental model of Retrieval-Augmented Generation before adding orchestration, agents, or production complexity.

The beginner track is intentionally small. It teaches the complete evidence loop first, then makes retrieval inspectable, then improves how evidence is prepared, and finally teaches the system when to cite and when not to answer.

```text
01 RAG Foundations
        ↓
02 First Local RAG
        ↓
03 Chunking Decisions
        ↓
04 Citations & Abstention
```

## Who this track is for

This track is designed for software engineers, data scientists, ML engineers, architects, and technical professionals who understand basic Python but want a rigorous foundation for building enterprise RAG systems.

You do **not** need prior experience with vector databases, LangChain, agents, or advanced retrieval frameworks.

## What you will be able to do

By the end of the track, you should be able to:

- explain the retrieval → context → generation loop;
- distinguish retrieval failure from generation failure;
- build and inspect a small local RAG pipeline;
- understand embeddings, similarity, top-k retrieval, and context construction;
- reason about chunk size, overlap, boundaries, and metadata;
- preserve source provenance through the pipeline;
- produce citations that map claims back to evidence;
- abstain when authorized evidence is insufficient;
- evaluate intermediate artifacts instead of judging only fluent answers; and
- identify which failures justify moving to more advanced retrieval techniques.

---

# Course sequence

| Course | Core question | Practical focus | Why it comes here |
|---|---|---|---|
| **01 — RAG Foundations** | What actually happens inside RAG? | Retrieval → evidence → generation; failure decomposition | Establishes the system mental model |
| **02 — First Local RAG** | Can I build and inspect the loop myself? | Small local corpus, embeddings/retrieval, inspectable results | Makes the architecture concrete |
| **03 — Chunking Decisions** | How does document preparation change retrieval quality? | Chunk boundaries, overlap, metadata, retrieval experiments | Introduces the first major design trade-off |
| **04 — Citations & Abstention** | How does the system know what it can support? | Provenance, claim support, citation validation, abstention | Adds evidence discipline before more complex retrieval |
| **05 — Enterprise RAG Capstone** | How do these pieces fit into a real application? | Build an end-to-end Enterprise RAG system using a real vector store, embeddings, LLM, and dataset | Consolidates all concepts into a unified pipeline |

---

# 01 — RAG Foundations

Start with the architecture rather than a framework.

You should understand:

```text
user question
    ↓
retrieval
    ↓
candidate evidence
    ↓
context construction
    ↓
generation
    ↓
supported answer
```

The important lesson is that RAG is not simply "LLM + vector database." It is an evidence system with multiple independently measurable stages.

**Key concepts**

- retrieval vs generation;
- lexical vs semantic matching at a high level;
- evidence provenance;
- retrieval failure modes;
- grounding;
- evaluation boundaries.

**Exit criterion:** you can explain where a bad RAG answer came from without saying only "the model hallucinated."

---

# 02 — First Local RAG

Build the smallest pipeline whose intermediate artifacts you can inspect.

The objective is not framework sophistication. It is observability.

Inspect:

```text
query
retrieved items
scores
source metadata
constructed context
final answer
```

**Key concepts**

- document representation;
- embedding-based similarity;
- top-k;
- deterministic local examples;
- source IDs;
- debugging retrieval separately from generation.

**Exit criterion:** you can trace an answer back through its retrieved evidence.

---

# 03 — Chunking Decisions

Chunking changes what the retriever is capable of finding.

Study the trade-offs between:

- small vs large chunks;
- overlap vs duplication;
- fixed-size vs structure-aware boundaries;
- context completeness vs retrieval precision;
- chunk metadata;
- document structure.

Do not search for one universal "best chunk size." Evaluate chunking against the actual question distribution and document structure.

**Exit criterion:** you can design a chunking experiment and explain which retrieval metric should decide between alternatives.

---

# 04 — Citations & Abstention

A production-oriented RAG system needs an explicit answerability boundary.

```text
retrieve
   ↓
is sufficient authorized evidence available?
   ├─ yes → answer + citations
   └─ no  → abstain / clarify
```

Citations should be based on source provenance carried through retrieval, not reconstructed from model memory.

**Key concepts**

- source provenance;
- claim-to-evidence support;
- citation correctness;
- answerability;
- abstention;
- unsupported claims.

**Exit criterion:** the system can refuse unsupported questions and explain which evidence supports material claims.

---

# Engineering habits introduced in this track

Even beginner examples should establish habits that continue through the curriculum:

1. **Inspect intermediate artifacts.**
2. **Preserve provenance from ingestion onward.**
3. **Separate retrieval evaluation from answer evaluation.**
4. **Use deterministic computation where possible.**
5. **Treat abstention as a valid outcome.**
6. **Add complexity only after measuring a failure that simpler architecture cannot solve.**

---

# What not to add yet

Do not jump immediately to:

- autonomous agents;
- GraphRAG;
- multi-agent orchestration;
- corrective loops;
- complex query planners;
- production-scale vector infrastructure.

Those techniques are useful only when their target failure mode exists.

The beginner track establishes the baseline against which later complexity should be measured.

---

# 05 — Enterprise RAG Capstone

The capstone is the track completion challenge. It integrates everything you've learned into a realistic, end-to-end Enterprise Assistant.

Build a complete RAG pipeline over a controlled document set that:

- ingests source metadata;
- compares at least two chunking configurations;
- retrieves inspectable evidence;
- answers only from retrieved evidence;
- cites source IDs;
- abstains on an unanswerable query; and
- records enough intermediate state to explain one retrieval failure.

A successful implementation is not the most sophisticated one. It is the one whose evidence behavior you can explain.

---

# Next track

## Intermediate RAG

The intermediate track moves from a correct baseline to **retrieval quality, authorization, reranking, evaluation, synthesis, and vector-database implementation**.

> **Progression principle:** add complexity only when evaluation shows which failure you are solving.
