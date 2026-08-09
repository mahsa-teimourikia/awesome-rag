# Beginner path

**Outcome:** build a local RAG assistant that answers from a small document set, cites its evidence, and abstains when a documented policy says the evidence is insufficient.

| Step | Lesson | What you learn |
| --- | --- | --- |
| 1 | RAG foundations | The pipeline, groundedness, and when retrieval helps |
| 2 | First local RAG app | Load documents, embed chunks, retrieve, and generate |
| 3 | Chunking lab | Compare structure-aware and fixed-size chunks |
| 4 | Citations and abstention | Preserve provenance and decline unsupported questions |
| 5 | Beginner capstone | Ship a documentation or notes assistant — start with the [documentation assistant](../../use-cases/documentation-assistant/README.md) |

Prerequisites: basic Python and command-line usage. Start with [What is RAG?](../../docs/what-is-rag.md), then complete [RAG foundations](01-rag-foundations/README.md), [the first local baseline](02-first-local-rag/README.md), [the chunking lab](03-chunking-lab/README.md), and [citations and abstention](04-citations-abstention/README.md).

For the notebook-first route, complete the connected [Harborline Support beginner track](../../notebooks/README.md#harborline-support--beginner-notebook-track). It uses one realistic support-policy corpus to turn each concept into a measurable design decision: inspect retrieval traces, compare boundaries, then audit citations and abstention policy.
