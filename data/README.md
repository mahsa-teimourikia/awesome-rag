# Learning data

`data/enterprise/` contains the fictional NovaTech corpus used by the Enterprise notebook track. It is deliberately small and inspectable: documents, metadata, incidents, deployments, runbooks, and labelled evaluation cases are fixtures for learning retrieval and operations—not production data.

Evaluation questions live in [`enterprise/evaluation/questions.json`](enterprise/evaluation/questions.json). Add a question and expected evidence there when an experiment needs a regression case; keeping it beside the corpus makes fixture versioning and local discovery straightforward.
