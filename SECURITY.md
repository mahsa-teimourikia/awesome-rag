# Security policy

## Supported version

Awesome RAG is an educational repository. Security fixes are applied to the current `main` branch; older commits, branches, forks, and deployed copies are not maintained as separate supported versions.

## Report a vulnerability privately

Do not open a public issue for a suspected vulnerability or include exploit details, credentials, personal data, or cross-tenant evidence in public artifacts.

Use [GitHub private vulnerability reporting](https://github.com/mahsa-teimourikia/awesome-rag/security/advisories/new). Include:

- the affected file, page, workflow, dependency, or commit;
- the impact and required preconditions;
- minimal reproducible steps or a proof of concept;
- whether credentials, private data, or deployed services may be affected; and
- a safe way to validate a proposed fix.

The maintainer will acknowledge the report, assess scope and severity, coordinate remediation, and publish an advisory when disclosure is appropriate. Please allow time for investigation before public disclosure.

## What belongs in a normal issue

Broken educational examples, inaccurate security explanations, and failures limited to synthetic course data can normally use the public bug or content-improvement forms—provided the report does not expose a real vulnerability or sensitive data.

## Educational code disclaimer

Labs favor inspectability and local execution. They are not production security controls by themselves. Before deploying a derived system, perform a threat model, enforce identity and authorization outside the model, isolate credentials, validate tool actions, test adversarial paths, and follow the security guidance of every dependency and platform involved.

