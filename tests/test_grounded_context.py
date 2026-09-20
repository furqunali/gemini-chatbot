import pytest
from grounded_context import ContextItem, build_grounded_prompt

def test_build_grounded_prompt_preserves_source_boundaries():
    prompt = build_grounded_prompt("What is RAG?", [ContextItem("docs/rag.md","RAG retrieves context.",2)])
    assert "[SOURCE 2] docs/rag.md" in prompt
    assert "QUESTION: What is RAG?" in prompt

@pytest.mark.parametrize("question", ["", "   "])
def test_build_grounded_prompt_rejects_empty_question(question):
    with pytest.raises(ValueError):
        build_grounded_prompt(question, [ContextItem("a","b",0)])

def test_build_grounded_prompt_rejects_invalid_context():
    with pytest.raises(ValueError):
        build_grounded_prompt("q", [ContextItem("", "text", 0)])
