# Retrieval patterns and when to use them

Choose a retrieval pattern based on the shape of the question and corpus—not on novelty. Start with a simple baseline, measure it, then introduce complexity only where it fixes observed failures.

## Dense retrieval

Embed queries and chunks in the same vector space, then retrieve nearest chunks. It handles paraphrase and conceptual similarity well.

Use it when users express the same idea in many ways. Validate on rare terms and exact-match questions, which can be weak spots. [Sentence Transformers' semantic-search guide](https://www.sbert.net/examples/sentence_transformer/applications/semantic-search/README.html) explains the bi-encoder trade-off; [DPR](https://arxiv.org/abs/2004.04906) is a foundational reference.

## Lexical retrieval

Search for terms using algorithms such as BM25. It is fast, inspectable, and strong at product names, error strings, legal citations, code identifiers, and dates.

Use it as a baseline even when planning to use embeddings. The [Stanford IR book](https://nlp.stanford.edu/IR-book/) explains BM25 and ranking fundamentals.

## Hybrid retrieval

Combine dense and lexical candidates, then merge or rank them. This often improves robustness because semantic and term-based search fail differently.

Use it for documentation, enterprise content, support, and code—corpora that mix prose with identifiers. [OpenSearch hybrid search documentation](https://opensearch.org/docs/latest/search-plugins/hybrid-search/) offers an implementation-oriented reference.

## Reranking

Retrieve a broad candidate set cheaply, then score the question–chunk pairs with a stronger model. Cross-encoders usually offer high precision but are too expensive to run over every corpus item.

Use it when top-k candidates are plausible but poorly ordered. [Sentence Transformers' retrieve-and-rerank guide](https://www.sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html) explains this two-stage architecture.

## Query rewriting and multi-query retrieval

Generate a clearer search query, several paraphrases, or decomposed subquestions before retrieval. This helps with conversational follow-ups, ambiguous wording, and multi-hop questions.

Use only when evaluation shows the original query is the failure point; generated queries can add latency and drift. The [RAG from scratch examples](https://github.com/langchain-ai/rag-from-scratch) include query transformation patterns.

## Metadata-filtered retrieval

Restrict candidate documents by fields such as tenant, team, region, document type, date, language, or classification. Permission filtering belongs here and must happen before evidence reaches the model.

Use this for any multi-user or regulated application. Treat access control as a security boundary, not as prompt text.

## Parent–child retrieval

Index small child chunks for precise matching, but return a larger parent section for generation. This balances precise retrieval with enough context to interpret the match.

Use it when chunks either retrieve well but lack context, or have enough context but retrieve too broadly. [LlamaIndex's node parsers](https://docs.llamaindex.ai/en/stable/module_guides/loading/node_parsers/) are useful implementation references for structured chunking.

## Graph retrieval

Use entities and relationships to retrieve connected evidence, sometimes alongside vector or lexical retrieval. Graph approaches can help when questions require connecting facts across the corpus or summarizing themes rather than finding one passage.

Use only after validating that relationship-aware/global questions are important. Start with [Microsoft GraphRAG](https://github.com/microsoft/graphrag) and its [paper](https://arxiv.org/abs/2404.16130).
