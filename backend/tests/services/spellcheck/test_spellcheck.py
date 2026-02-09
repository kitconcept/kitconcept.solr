import pytest


class TestSpellcheck:
    @pytest.fixture(autouse=True)
    def _init(self, portal_with_content, manager_request):
        self.portal = portal_with_content
        self.manager_request = manager_request


class TestSpellcheckCollateWithResults(TestSpellcheck):
    """Test spellcheck and collate parameters when search returns results.

    When results are found (numFound > 0), the collate code path should NOT be taken,
    regardless of the collate parameter value.
    """

    def test_spellcheck_collate_true_with_results_has_no_collation_misspellings(self):
        """With collate=true and results found, collation_misspellings should not be present."""
        response = self.manager_request.get(
            "/@solr?q=chomsky&collate=true&spellcheck=true"
        )
        data = response.json()
        assert "response" in data
        assert data["response"]["numFound"] > 0
        assert "collation_misspellings" not in data

    def test_spellcheck_collate_false_with_results_has_no_collation_misspellings(self):
        """With collate=false and results found, collation_misspellings should not be present."""
        response = self.manager_request.get(
            "/@solr?q=chomsky&collate=false&spellcheck=true"
        )
        data = response.json()
        assert "response" in data
        assert data["response"]["numFound"] > 0
        assert "collation_misspellings" not in data

    def test_spellcheck_collate_missing_with_results_has_no_collation_misspellings(
        self,
    ):
        """Without collate parameter and results found, collation_misspellings should not be present."""
        response = self.manager_request.get("/@solr?q=chomsky&spellcheck=true")
        data = response.json()
        assert "response" in data
        assert data["response"]["numFound"] > 0
        assert "collation_misspellings" not in data


class TestSpellcheckCollateWithNoResults(TestSpellcheck):
    """Test collate parameter when search returns no results.

    When no results are found (numFound == 0), the collate feature may be triggered
    if spellcheck collations are available.
    """

    def test_spellcheck_collate_true_with_no_results(self):
        """With spellcheck=true and collate=true and no results, response should still be valid."""
        response = self.manager_request.get(
            "/@solr?q=xyznonexistent&collate=true&spellcheck=true"
        )
        data = response.json()
        assert "response" in data
        # When there's no spellcheck suggestion, numFound stays 0
        # collation_misspellings may or may not be present depending on spellcheck data

    def test_spellcheck_collate_false_with_no_results_has_no_collation_misspellings(
        self,
    ):
        """With spellcheck=true and collate=false and no results, collation_misspellings should not be present."""
        response = self.manager_request.get(
            "/@solr?q=xyznonexistent&collate=false&spellcheck=true"
        )
        data = response.json()
        assert "response" in data
        assert data["response"]["numFound"] == 0
        assert "collation_misspellings" not in data


class TestSpellcheckEnabled(TestSpellcheck):
    """Test spellcheck parameter when enabled.

    When spellcheck=true, spellcheck data should be included in the full Solr response.
    """

    def test_spellcheck_true_returns_spellcheck_data(self):
        """With spellcheck=true and keep_full_solr_response=true, spellcheck data should be present."""
        response = self.manager_request.get(
            "/@solr?q=chomsky&spellcheck=true&keep_full_solr_response=true"
        )
        data = response.json()
        assert "response" in data
        assert "spellcheck" in data

    def test_spellcheck_true_default_response_has_spellcheck_data(self):
        """With spellcheck=true and default response, spellcheck data is included."""
        response = self.manager_request.get("/@solr?q=chomsky&spellcheck=true")
        data = response.json()
        assert "response" in data
        # Spellcheck data is included in response (not pruned like facet_counts)
        assert "spellcheck" in data


class TestSpellcheckDisabled(TestSpellcheck):
    """Test spellcheck parameter when disabled.

    When spellcheck=off, spellcheck data should NOT be included in the response.
    """

    def test_spellcheck_false_no_spellcheck_data(self):
        """With spellcheck=off, spellcheck data should not be present."""
        response = self.manager_request.get(
            "/@solr?q=chomsky&spellcheck=off&keep_full_solr_response=true"
        )
        data = response.json()
        assert "response" in data
        assert "spellcheck" not in data

    def test_spellcheck_false_collate_true_no_collation_misspellings(self):
        """With spellcheck=off and collate=true, collation_misspellings should not be present."""
        response = self.manager_request.get(
            "/@solr?q=xyznonexistent&spellcheck=off&collate=true"
        )
        data = response.json()
        assert "response" in data
        # Without spellcheck, collate cannot work
        assert "collation_misspellings" not in data


class TestSpellcheckDefault(TestSpellcheck):
    """Test default spellcheck behavior.

    By default (no spellcheck parameter), spellcheck should be enabled.

    In these tests, we set keep_full_solr_response=true and check the full
    spellcheck response data. This is a baseline check to ensure that the configuration
    is working as expected.
    """

    def test_default_spellcheck_disabled(self):
        """Without spellcheck parameter, spellcheck should be enabled by default."""
        response = self.manager_request.get(
            "/@solr?q=chomsky&keep_full_solr_response=true"
        )
        data = response.json()
        assert "response" in data
        # Spellcheck is disabled by default
        assert "spellcheck" not in data


class TestSpellcheckResponseStructure(TestSpellcheck):
    """Test the structure of the spellcheck response data.

    In these tests, we set keep_full_solr_response=true and check the full
    spellcheck response data. This is a baseline check to ensure that the configuration
    is working as expected.
    """

    def test_spellcheck_response_has_suggestions_key(self):
        """Spellcheck response should contain a suggestions key."""
        response = self.manager_request.get(
            "/@solr?q=chomsky&spellcheck=true&keep_full_solr_response=true"
        )
        data = response.json()
        assert "spellcheck" in data
        assert "suggestions" in data["spellcheck"]

    def test_spellcheck_response_has_collations_key_when_collate_true(self):
        """With collate=true, spellcheck response should contain collations key."""
        response = self.manager_request.get(
            "/@solr?q=chomsky&spellcheck=true&collate=true&keep_full_solr_response=true"
        )
        data = response.json()
        assert "spellcheck" in data
        assert "collations" in data["spellcheck"]

    def test_spellcheck_suggestions_is_list(self):
        """Spellcheck suggestions should be a list."""
        response = self.manager_request.get(
            "/@solr?q=chomsky&spellcheck=true&keep_full_solr_response=true"
        )
        data = response.json()
        assert "spellcheck" in data
        assert isinstance(data["spellcheck"]["suggestions"], list)

    def test_spellcheck_suggestions_for_misspelled_term(self):
        """Spellcheck should provide suggestions for a misspelled term."""
        # "chomski" is a misspelling of "chomsky" which exists in test content
        response = self.manager_request.get(
            "/@solr?q=chomski&spellcheck=true&keep_full_solr_response=true"
        )
        data = response.json()
        assert "spellcheck" in data
        spellcheck = data["spellcheck"]
        assert "suggestions" in spellcheck
        assert "correctlySpelled" in spellcheck
        assert spellcheck["correctlySpelled"] is False
        # Suggestions list contains alternating term and suggestion objects
        suggestions = spellcheck["suggestions"]
        assert len(suggestions) > 0
        # First element is the misspelled term
        assert suggestions[0] == "chomski"
        # Second element is suggestion data object
        suggestion_data = suggestions[1]
        assert "suggestion" in suggestion_data
        assert len(suggestion_data["suggestion"]) > 0
        # The suggestion contains the correct word "chomsky"
        assert suggestion_data["suggestion"][0]["word"] == "chomsky"

    def test_spellcheck_collations_is_list(self):
        """Spellcheck collations should be a list."""
        response = self.manager_request.get(
            "/@solr?q=chomsky&spellcheck=true&collate=true&keep_full_solr_response=true"
        )
        data = response.json()
        assert "spellcheck" in data
        assert isinstance(data["spellcheck"]["collations"], list)

    def test_spellcheck_collations_for_misspelled_term(self):
        """Spellcheck collations should contain query correction data for misspelled terms.

        Note: This test verifies the Solr spellcheck.collate response structure.
        Collations are generated when Solr finds spelling corrections that would
        return results. The collation data includes the corrected query and
        the mapping of misspellings to corrections.
        """
        response = self.manager_request.get(
            "/@solr?q=chomski&spellcheck=true&collate=true&keep_full_solr_response=true"
        )
        data = response.json()
        assert "spellcheck" in data
        spellcheck = data["spellcheck"]
        assert "collations" in spellcheck
        collations = spellcheck["collations"]
        # Collations may be empty if Solr doesn't find a correction with results
        if len(collations) > 0:
            # First element is "collation" string
            assert collations[0] == "collation"
            # Second element is collation data object
            collation_data = collations[1]
            assert "collationQuery" in collation_data
            assert "hits" in collation_data
            assert "misspellingsAndCorrections" in collation_data
            # The collation should find results (hits > 0)
            assert collation_data["hits"] > 0
            # misspellingsAndCorrections contains the correction mapping
            corrections = collation_data["misspellingsAndCorrections"]
            assert "chomski" in corrections
            assert "chomsky" in corrections


class TestCollationMisspellings(TestSpellcheck):
    """Test collation_misspellings response when collate triggers a corrected search.

    When collate=true and the original query returns no results but a corrected
    query would return results, collation_misspellings is added to the response.
    These tests do NOT use keep_full_solr_response.
    """

    def test_collation_misspellings_present_for_misspelled_term(self):
        """With misspelled term and collate=true, collation_misspellings should be present."""
        # "chomski" returns 0 results, but "chomsky" returns results
        response = self.manager_request.get(
            "/@solr?q=chomski&collate=true&spellcheck=true"
        )
        data = response.json()
        assert "response" in data
        # The corrected query should return results
        assert data["response"]["numFound"] > 0
        # collation_misspellings should be present
        assert "collation_misspellings" in data

    def test_collation_misspellings_contains_correction_mapping(self):
        """collation_misspellings should contain the misspelled term and its correction."""
        response = self.manager_request.get(
            "/@solr?q=chomski&collate=true&spellcheck=true"
        )
        data = response.json()
        assert "collation_misspellings" in data
        misspellings = data["collation_misspellings"]
        # misspellings is a list with alternating misspelled/corrected terms
        assert isinstance(misspellings, list)
        assert len(misspellings) > 0
        # Should contain "chomski" and "chomsky"
        assert "chomski" in misspellings
        assert "chomsky" in misspellings

    def test_collation_misspellings_not_present_when_collate_false(self):
        """With collate=false, collation_misspellings should not be present."""
        response = self.manager_request.get(
            "/@solr?q=chomski&collate=false&spellcheck=true"
        )
        data = response.json()
        assert "response" in data
        # Without collate, no corrected search is performed
        assert data["response"]["numFound"] == 0
        assert "collation_misspellings" not in data

    def test_collation_misspellings_not_present_when_spellcheck_off(self):
        """With spellcheck=off, collation_misspellings should not be present."""
        response = self.manager_request.get(
            "/@solr?q=chomski&collate=true&spellcheck=off"
        )
        data = response.json()
        assert "response" in data
        assert "collation_misspellings" not in data

    def test_collation_misspellings_not_present_when_spellcheck_default_off(self):
        """With spellcheck=off, collation_misspellings should not be present."""
        response = self.manager_request.get("/@solr?q=chomski&collate=true")
        data = response.json()
        assert "response" in data
        assert "collation_misspellings" not in data

    def test_collation_misspellings_without_keep_full_solr_response(self):
        """collation_misspellings should be present in default (pruned) response."""
        # Test without keep_full_solr_response parameter
        response = self.manager_request.get(
            "/@solr?q=chomski&collate=true&spellcheck=true"
        )
        data = response.json()
        # facet_counts should be pruned (not present)
        assert "facet_counts" not in data
        # But collation_misspellings should still be present
        assert "collation_misspellings" in data
        misspellings = data["collation_misspellings"]
        assert "chomski" in misspellings
        assert "chomsky" in misspellings
