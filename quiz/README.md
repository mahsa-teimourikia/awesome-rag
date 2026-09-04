# Full quiz implementation

The canonical learning experience is now the **RAG Field Guide** at
<https://mahsa-teimourikia.github.io/awesome-rag/>. It includes the curriculum,
lesson material, labs, references, and per-lesson checkpoints.

This directory contains the dependency-light full knowledge check published at
<https://mahsa-teimourikia.github.io/awesome-rag/quiz/>. The main Learning Hub
uses focused checkpoints inside each lesson; this page remains useful when a
learner wants one larger quiz across foundations, ingestion, retrieval,
generation, security, evaluation, and operations.

The learning registry currently covers all 18 curriculum topics and exposes
every topic-owned notebook and reusable Python implementation. The full bank
contains 54 source-linked questions—three for each course—and the Hub reuses
those same questions for its focused checkpoints so the two assessments do not
drift apart.

The Pages workflow copies this directory into the static artifact after the
React hub build. Keep links repository-backed through `resourceHref()` so the
deployed quiz can always open the matching lesson material and notebooks on
GitHub.
