# Contributing to Awesome RAG

Thank you for improving the curriculum, runnable labs, Learning Hub, quiz, or curated resources.

## What belongs here

- Primary research, official documentation, maintained open-source projects, and high-signal educational material about RAG.
- A concise description explaining the resource's specific value.
- Direct links to the project, paper, or documentation—not search results, referral links, or unmaintained mirrors.
- Focused corrections and learning improvements that help a technical reader explain, implement, test, evaluate, debug, or productionize a RAG concept.

## Submission rules

1. Search the README before adding a resource.
2. Place the link in the narrowest relevant section, alphabetically when practical.
3. Use this format: `- [Project](https://example.com) — what it is and why it belongs here.`
4. Do not add promotional descriptions, affiliate links, or star counts.
5. Verify the link, license claims, and that the project is actively maintained.
6. For substantial concepts, add an explanatory note and cite the primary source in the relevant `curriculum/` module.

Please keep pull requests focused. One topic or a small coherent group of resources per PR is easiest to review.

## Choose the right contribution path

- Use the repository's issue forms for reproducible bugs, content improvements, and feature proposals.
- Use [private vulnerability reporting](https://github.com/mahsa-teimourikia/awesome-rag/security/advisories/new) for security vulnerabilities. Never publish exploit details or sensitive data in an issue.
- Small, self-contained fixes may go directly to a pull request. For large curriculum or architecture changes, open an issue first so scope and learning outcomes can be agreed.

By participating, you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md). Usage questions and repository support boundaries are described in [SUPPORT.md](SUPPORT.md).

## Develop from the current main branch

Create a focused branch from the latest `main`. Preserve unrelated material and avoid committing generated environments, credentials, private data, notebook checkpoints, or editor artifacts.

For training changes, inspect the existing README, notebook, Python modules, assets, prerequisites, and adjacent courses before editing. Preserve useful material. Prefer one coherent, deeply developed learning experience over multiple shallow examples.

## Course and notebook expectations

A course README should stand on its own as a technical chapter. A notebook should stand on its own as a guided, runnable lab. When applicable, a contribution should:

- teach the primitive before hiding it behind a framework;
- use a scenario chosen for the concept rather than forcing every lesson into one storyline;
- explain motivation, mental model, mechanics, design choices, failures, evaluation, and production trade-offs;
- include explanatory Markdown between code cells and make internal state observable;
- use synthetic, non-sensitive data and avoid fake benchmark or API claims;
- distinguish deterministic controls from model behavior; and
- cite primary research, standards, specifications, and official documentation.

Markdown may use rendered Mermaid diagrams. Notebooks should embed a readable image version so diagrams render consistently on GitHub and in Jupyter.

## Validate the change

Run the smallest relevant checks first, then the broader contract for the files you changed:

| Change | Required validation |
| --- | --- |
| Python behavior | `make test` |
| Notebook or notebook imports | `make notebook-check` |
| Internal learning links | `make links` |
| Learning Hub or quiz | `make pages` |
| Curated external links | `make external-links` |

Document the exact checks and results in the pull request. If a check is not applicable or cannot run locally, explain why rather than marking it as passed.

## Pull request review

Complete the pull request template, link any related issue, and keep generated or unrelated changes out of the diff. Maintainer approval is required before merge. Review feedback may request narrower scope, stronger evidence, executable tests, clearer failure behavior, or closer alignment between README, notebook, code, assets, and navigation.
