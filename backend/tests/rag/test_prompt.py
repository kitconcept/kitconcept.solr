from kitconcept.solr.rag.config import TOP_K
from kitconcept.solr.rag.prompt import build_prompt
from kitconcept.solr.rag.prompt import strip_thinking
from kitconcept.solr.rag.prompt import SYSTEM_PROMPT


def chunk(title, text):
    return {"parent_title": title, "chunk_text": text}


class TestBuildPrompt:
    def test_contains_question_and_context(self):
        prompt = build_prompt(
            "How many vacation days?",
            [chunk("Vacation policy", "30 days of paid vacation.")],
        )
        assert "Question: How many vacation days?" in prompt
        assert 'Document "Vacation policy":\n30 days of paid vacation.' in prompt
        assert "based only on the context documents" in prompt

    def test_chunks_are_labeled_by_title_in_order(self):
        prompt = build_prompt(
            "q",
            [chunk("First", "text one"), chunk("Second", "text two")],
        )
        assert prompt.index('Document "First":') < prompt.index('Document "Second":')

    def test_context_is_capped_at_top_k(self):
        chunks = [chunk(f"Doc {i}", f"text {i}") for i in range(TOP_K + 3)]
        prompt = build_prompt("q", chunks)
        assert prompt.count('Document "') == TOP_K

    def test_no_bracketed_numbering_in_context(self):
        # Models reliably leak "[1]"-style context numbers into user
        # facing answers, so the prompt must not contain any: chunks
        # are labeled by document title instead.
        chunks = [chunk(f"Doc {i}", f"text {i}") for i in range(3)]
        prompt = build_prompt("q", chunks)
        assert "[1]" not in prompt
        assert "[2]" not in prompt

    def test_system_prompt_constrains_generation(self):
        assert "based only on the provided context" in SYSTEM_PROMPT
        assert "could not find the answer" in SYSTEM_PROMPT
        assert "language of the question" in SYSTEM_PROMPT
        # documents are referenced by title in the answer
        assert "use its title" in SYSTEM_PROMPT


class TestStripThinking:
    def test_removes_thinking_block(self):
        answer = "<think>\nreasoning here\n</think>\nThe answer."
        assert strip_thinking(answer) == "The answer."

    def test_plain_answer_untouched(self):
        assert strip_thinking("The answer.") == "The answer."

    def test_multiline_thinking(self):
        answer = "<think>line1\nline2</think>  \n\nAnswer\nwith lines."
        assert strip_thinking(answer) == "Answer\nwith lines."
