from kitconcept.solr.services.solr_utils import escape


class TestUtilsEscape:
    def test_escape_plus(self):
        assert escape("+") == "\\+"

    def test_escape_minus(self):
        assert escape("-") == "\\-"

    def test_escape_ampersand(self):
        assert escape("&") == "\\&"

    def test_escape_vertical_line(self):
        assert escape("|") == "\\|"

    def test_escape_exclamation_mark(self):
        assert escape("!") == "\\!"

    def test_escape_left_parenthesis(self):
        assert escape("(") == "\\("

    def test_escape_right_parenthesis(self):
        assert escape(")") == "\\)"

    def test_escape_left_curly_bracket(self):
        assert escape("{") == "\\{"

    def test_escape_right_curly_bracket(self):
        assert escape("}") == "\\}"

    def test_escape_left_bracket(self):
        assert escape("[") == "\\["

    def test_escape_right_bracket(self):
        assert escape("]") == "\\]"

    def test_escape_caret(self):
        assert escape("^") == "\\^"

    def test_escape_double_quote(self):
        assert escape('"') == '\\"'

    def test_escape_tilde(self):
        assert escape("~") == "\\~"

    def test_escape_asterisk(self):
        assert escape("*") == "\\*"

    def test_escape_question_mark(self):
        assert escape("?") == "\\?"

    def test_escape_colon(self):
        assert escape(":") == "\\:"

    def test_escape_slash(self):
        assert escape("~") == "\\~"

    def test_escape_backslash(self):
        assert escape("\\") == "\\\\"

    def test_escape_double_ampersand(self):
        assert escape("&&") == "\\&\\&"

    def test_escape_double_vertical_line(self):
        assert escape("||") == "\\|\\|"

    def test_escape_mixed_example(self):
        assert escape("Foo&Bar*Baz|") == "Foo\\&Bar\\*Baz\\|"
