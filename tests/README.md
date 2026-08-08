# Tests and validation

Tests protect the deterministic examples and the browser learning product. Use the [course map](../COURSE_MAP.md) to trace a lesson to its implementation and test.

```bash
export PYTHONPATH=.
pytest -q
npm run check:pages-links
npm run test:pages
```

Notebook JSON and Python code-cell compilation are also checked in CI. A lesson is complete only when its explanation, runnable code, references, and tests agree.
