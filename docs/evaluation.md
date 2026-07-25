# Evaluating a RAG system

Evaluation is the feedback loop that turns a demo into an engineering system. A fluent answer is not proof of a correct answer, and a correct answer can conceal unreliable retrieval that will fail on the next query.

## Build a useful test set

Start with 50–100 representative questions, then grow it continuously from real traffic and incidents. For each question, record:

- expected answer or answer criteria;
- source documents/passages that should support it;
- query category (fact lookup, comparison, multi-hop, no-answer, etc.);
- tenant/permission context where relevant; and
- freshness or document version constraints.

Include adversarial and “answer should not be given” cases. A production RAG system should be able to say it lacks sufficient evidence.

## Measure retrieval separately

Given known relevant passages, measure whether they appear among the retrieved candidates:

- **Recall@k** — whether the needed evidence appears in the first *k* results.
- **MRR** — rewards putting the first relevant result near the top.
- **nDCG** — supports graded relevance and ranking quality.

The [BEIR benchmark](https://github.com/beir-cellar/beir) and [Stanford IR book](https://nlp.stanford.edu/IR-book/) are strong references for retrieval evaluation.

## Measure answer quality separately

Useful dimensions include:

- **Faithfulness / groundedness:** are response claims supported by the retrieved context?
- **Answer relevance:** does the response address the question?
- **Context precision:** are retrieved chunks relevant rather than distracting?
- **Context recall:** did the context contain what was needed for the answer?
- **Citation correctness:** do cited sources entail the linked claim?

[Ragas](https://docs.ragas.io/en/stable/concepts/metrics/) documents common RAG metrics and their assumptions. Automated LLM-as-a-judge metrics are helpful for iteration, but calibrate them with human review—especially in high-stakes domains.

## An iteration loop

1. Run the same dataset against the current pipeline and capture traces: query, candidates, scores, chosen context, response, citations, latency, and cost.
2. Label the failure stage: extraction, chunking, retrieval, ranking, prompt/context assembly, or generation.
3. Make one focused change and compare it with the baseline on the full set—not only the examples that motivated the change.
4. Review aggregate metrics *and* the changed failures manually.
5. Promote the change only if it improves the intended metric without unacceptable regressions.

Open-source tools such as [Phoenix](https://github.com/Arize-ai/phoenix), [Langfuse](https://github.com/langfuse/langfuse), [TruLens](https://github.com/truera/trulens), and [DeepEval](https://github.com/confident-ai/deepeval) can help capture traces and run experiments.
