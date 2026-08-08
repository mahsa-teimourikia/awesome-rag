# Enterprise RAG lab library

This package contains the reusable deterministic code imported by the nine Enterprise notebooks. It is not a second curriculum: read the notebook first, then open the module when you want to extract a component into an application.

| Module | Responsibility |
| --- | --- |
| `corpus.py` | NovaTech documents, metadata, and chunking |
| `retrieval.py` | Sparse, dense-like, hybrid, and evidence selection helpers |
| `advanced.py` | Query transformation, graph, and corrective/adaptive patterns |
| `evaluation.py` | Retrieval and answer-quality measurements |
| `generation.py` | Deterministic grounded answer formatting |
| `lab_experiments.py` | Notebook-facing comparisons and production traces |

All side effects are simulated. Provider integrations should be added as adapters with explicit credentials, budgets, permissions, and tests.
