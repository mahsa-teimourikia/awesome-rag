import importlib.util
from pathlib import Path


ROOT = Path(__file__).parents[1]
SPEC = importlib.util.spec_from_file_location("documentation_assistant", ROOT / "use-cases/documentation-assistant/app.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_documentation_assistant_answers_with_api_key_citation():
    result = MODULE.ask("How do I rotate an API key?")
    assert "api-keys-1" in result
    assert "Sources:" in result


def test_documentation_assistant_abstains_outside_corpus():
    result = MODULE.ask("How do I order lunch?")
    assert result.startswith("I don't have enough evidence")
