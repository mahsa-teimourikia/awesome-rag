# RAG basics

Retrieval-Augmented Generation retrieves external evidence at answer time and supplies that evidence to a language model. Retrieval is useful when knowledge changes, is private, or is too specialized to rely on model parameters alone.

The core pipeline is ingestion, chunking, indexing, retrieval, optional reranking, and grounded generation. Each stage can fail independently, so evaluation should separate retrieval quality from answer quality.

An abstention is a valid answer when the indexed evidence does not support the question. A trustworthy assistant should explain that it lacks evidence instead of inventing a citation.
