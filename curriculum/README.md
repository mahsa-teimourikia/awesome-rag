# Curriculum map

The curriculum is organized by learner outcome rather than by vendor. Complete the levels in order unless you already meet the stated outcome.

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
