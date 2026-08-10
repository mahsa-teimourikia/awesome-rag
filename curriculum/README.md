# Curriculum modules

The curriculum is organized by learner outcome rather than by vendor. Use the repository’s [canonical course map](../COURSE_MAP.md) for the complete flow and asset map; this page stays focused on the module-level prerequisites and outcomes.

## Beginner

Start with [`beginner/README.md`](beginner/README.md). Build a local, cited document assistant and learn the vocabulary of ingestion, chunking, embeddings, retrieval, context, grounding, and abstention.

## Intermediate

Continue with [`intermediate/README.md`](intermediate/README.md). Treat retrieval as an information-retrieval system: compare lexical and dense search, add filters and reranking, and evaluate changes with a fixed dataset.

## Advanced

Finish with [`advanced/README.md`](advanced/README.md). Design systems that route, recover, protect permissions, handle multiple modalities, and operate with measurable quality and cost.

## Notebook-first lesson format

The notebooks are the primary learning artifacts, not just launchers for code. Open the notebook linked from each module and work through it in order:

1. Read the scenario, concept explanation, trade-offs, and Mermaid architecture map.
2. Run the deterministic implementation and inspect the evidence, trace, or evaluation output.
3. Compare at least two examples, change one variable, and observe the failure or quality trade-off.
4. Complete the production checklist and reflection questions before moving to the next lesson.

Each notebook keeps the theory and implementation together, while larger reusable modules remain in `examples/` or `src/`. The split makes the lesson readable in GitHub and executable locally without hiding the engineering decisions behind a framework.

## Reference docs are part of the route

The documents in [`docs/`](../docs/) are not a parallel curriculum. They are
deeper, cross-cutting references connected to the lessons below. Read the linked
reference when a lesson asks you to make a design, evaluation, or operational
decision; return to the notebook to implement and test it.

| Reference | Curriculum home | Notebook track |
| --- | --- | --- |
| [What is RAG?](../docs/what-is-rag.md) | [Beginner foundations](beginner/01-rag-foundations/README.md) | [Foundations notebook](beginner/01-rag-foundations/rag_foundations.ipynb) |
| [Technology decisions](../docs/technology-decisions.md) | [First local RAG](beginner/02-first-local-rag/README.md), [retrieval strategies](intermediate/01-retrieval-strategies/README.md), and [local Qdrant](intermediate/06-qdrant-local/README.md) | Their linked notebooks |
| [Retrieval patterns](../docs/retrieval-patterns.md) | [Retrieval strategies](intermediate/01-retrieval-strategies/README.md) and [query/reranking](intermediate/03-query-reranking/README.md) | Their linked notebooks |
| [Evaluation guide](../docs/evaluation.md) | [Evaluation](intermediate/04-evaluation/README.md) and [production operations](advanced/05-production-operations/README.md) | [PolicyAssist track](../notebooks/evaluation/README.md) |
| [Adaptive RAG guide](../docs/adaptive-rag.md) | [Corrective RAG](advanced/01-corrective-rag/README.md) and [agentic RAG](advanced/03-agentic-rag/README.md) | [Adaptive track](../notebooks/adaptive-rag/README.md) |
| [Local development](../docs/local-development.md) | Every runnable lesson | Local setup and notebook execution |
| [Tutorial template](../docs/tutorial-template.md) | Course contributors | Use when adding a lesson and its notebook |

## Notebook coverage

Every curriculum lesson now has a notebook route. Beginner lessons 2–4 use the
connected Harborline scenario notebooks in `notebooks/beginner/`; all
intermediate and advanced lessons keep their notebook beside the lesson README.

| Level | Lesson | Practical notebook |
| --- | --- | --- |
| Beginner | Foundations | [01 foundations](beginner/01-rag-foundations/rag_foundations.ipynb) |
| Beginner | First local RAG | [Harborline 01](../notebooks/beginner/01_first_local_rag.ipynb) |
| Beginner | Chunking | [Harborline 02](../notebooks/beginner/02_chunking_lab.ipynb) |
| Beginner | Citations and abstention | [Harborline 03](../notebooks/beginner/03_citations_abstention.ipynb) |
| Intermediate | Lessons 01–06 | Each lesson's adjacent notebook |
| Advanced | Lessons 01–05 | Each lesson's adjacent notebook |

Use the specialist [evaluation](../notebooks/evaluation/README.md) and
[adaptive retrieval](../notebooks/adaptive-rag/README.md) tracks after their
curriculum anchor lessons when you want a longer, scenario-first investigation.
