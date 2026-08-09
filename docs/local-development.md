# Local installation and development

This course is designed to run without an API key. The deterministic notebooks, examples, tests, Hub, and quiz use fixtures committed to the repository. Optional labs that use Qdrant, embeddings, or provider SDKs document their extra setup where they appear.

## Quick start (macOS, Linux, or Codespaces)

Requirements:

- Python 3.11 or newer;
- Node.js 20 or newer for the Hub and quiz; and
- GNU Make (already present on most macOS/Linux development environments).

```bash
git clone https://github.com/mahsa-teimourikia/awsome-rag.git
cd awsome-rag
make setup
make test
make notebook-check
```

`make setup` creates `.venv` and installs the project’s `dev` extra, including pytest and the Jupyter execution runtime. `make notebook-check` executes the 32 deterministic beginner, Enterprise, Evaluation, and Adaptive RAG notebooks in real kernels—the same notebook contract used by CI.

## Study in Jupyter

Activate the environment, then launch Jupyter from the repository root so imports and data paths resolve correctly:

```bash
source .venv/bin/activate
PYTHONPATH=. python -m jupyterlab notebooks
```

Start with the [Harborline Support beginner notebooks](../notebooks/README.md#harborline-support--beginner-notebook-track), then follow the [course map](../COURSE_MAP.md). Notebooks are self-contained: they explain theory, include their exercises, and import reusable deterministic modules rather than requiring a model API.

## Preview the Learning Hub and quiz

Install the Node dependencies and build the same static artifact GitHub Pages deploys:

```bash
npm ci
npm run test:pages
```

The generated site is written to `out/`; the command also checks that the Hub bundle, One+i asset, and `/quiz/` artifact exist. For a development server, use `npm run dev`.

## Manual setup and Windows

If you do not have Make, create and use a virtual environment directly:

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell
# .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
PYTHONPATH=. python -m pytest -q
PYTHONPATH=. python scripts/execute-notebooks.py --timeout 90
```

On Windows PowerShell, set the Python path for the current shell with `$env:PYTHONPATH='.'` before running the final two commands.

## Optional infrastructure

The core path does not require a model download, Docker, Qdrant, or an API key. Add optional capabilities only when you reach the related lesson:

- `pip install -e '.[llamaindex]'` for LlamaIndex comparisons;
- `pip install -e '.[qdrant]'` for the Qdrant/Sentence Transformers lab; and
- `docker compose up -d` only when following the local Qdrant service instructions.

Never commit API keys. Put provider credentials in a local environment file ignored by Git, set a budget, and keep side-effecting tools behind explicit approval boundaries.

## Useful checks

| Goal | Command |
| --- | --- |
| Python behavior | `make test` |
| Execute deterministic notebooks | `make notebook-check` |
| Validate Hub resource paths | `make links` |
| Build and smoke-test Hub + quiz | `make pages` |
| Check external curated links | `make external-links` |

The `external-links` target needs network access and is intentionally separate from the deterministic local test path.
