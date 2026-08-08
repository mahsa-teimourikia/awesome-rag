# RAG Evaluation Lab: from impressive demo to production readiness

You are joining **Northstar Insurance** to evaluate **PolicyAssist**, an internal RAG assistant for underwriters and customer support. It looks excellent in a demo, but production-like cases reveal stale policies, weak retrieval, unsupported citations, permission leaks, injected instructions, and slow queries.

This is one evolving investigation, not a collection of metric demos. Work through the notebooks in order. Each one follows **incident → theory → investigation → experiment → metrics → diagnosis → improvement → reflection**. The notebooks contain both the learning material and runnable deterministic code; [`src/rag_evaluation/`](../../src/rag_evaluation/) holds the reusable components.

| Step | Notebook | Failure boundary |
| --- | --- | --- |
| 00 | [The broken RAG system](00_the_broken_rag.ipynb) | A high demo score hides multiple defects |
| 01 | [Evaluation dataset](01_building_eval_dataset.ipynb) | Easy questions mask real failure modes |
| 02 | [Retrieval](02_retrieval_evaluation.ipynb) | Relevant evidence never reaches the model |
| 03 | [Reranking and context](03_context_and_reranking.ipynb) | Retrieved evidence is not usable context |
| 04 | [Generation](04_generation_evaluation.ipynb) | Correctness, relevance, and grounding disagree |
| 05 | [Claims and citations](05_claims_and_citations.ipynb) | Answer-level scores hide unsupported claims |
| 06 | [LLM-as-a-judge](06_llm_as_judge.ipynb) | The evaluator itself is biased or uncalibrated |
| 07 | [Robustness and abstention](07_robustness_and_abstention.ipynb) | Noise, conflicts, and no-answer cases cause failure |
| 08 | [Security and permissions](08_security_and_permissions.ipynb) | Untrusted context or access rules are bypassed |
| 09 | [Architecture comparison](09_advanced_rag_evaluation.ipynb) | Complexity is added without measured benefit |
| 10 | [Production evaluation](10_production_observability.ipynb) | Offline success decays after deployment |
| 11 | [Production readiness capstone](11_policyassist_capstone.ipynb) | Can PolicyAssist launch? |

Start with [the evaluation theory guide](../../docs/evaluation.md), then run notebooks from the repository root with `PYTHONPATH=.`. The optional framework extensions (Ragas, DeepEval, TruLens, LangSmith) come after the deterministic metrics so the course teaches evaluation reasoning rather than a tool API.
