from kitconcept.solr.rag.config import RagConfig
from kitconcept.solr.rag.pipeline import ERROR_NOT_CONFIGURED
from kitconcept.solr.rag.pipeline import RagResult
from kitconcept.solr.services import rag_search as service_module
from kitconcept.solr.services.rag_search import RagSearch
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.restapi.testing import RelativeSession
from unittest import mock
from zExceptions import BadRequest

import pytest
import transaction


CONFIG = RagConfig(
    base_url="http://llm.example.com",
    token=None,
    embed_model="test-embed",
    chat_model="test-chat",
)


@pytest.fixture
def service(integration):
    portal = integration["portal"]
    request = integration["request"]
    service = RagSearch()
    service.context = portal
    service.request = request
    return service


class TestRagSearchService:
    def test_missing_question_is_bad_request(self, service):
        with pytest.raises(BadRequest):
            service.reply()

    def test_not_configured(self, service):
        service.request.form["q"] = "a question"
        with mock.patch.object(service_module, "get_rag_config", return_value=None):
            data = service.reply()
        assert data["answer"] is None
        assert data["sources"] == []
        assert data["error_code"] == ERROR_NOT_CONFIGURED
        assert data["error"]

    def test_success_shape(self, service):
        service.request.form["q"] = "a question"
        result = RagResult(
            answer="The answer.",
            sources=[{"@id": "http://nohost/plone/doc", "title": "Doc"}],
        )
        with (
            mock.patch.object(service_module, "get_rag_config", return_value=CONFIG),
            mock.patch.object(
                service_module, "run_rag_search", return_value=result
            ) as runner,
        ):
            data = service.reply()
        assert data == {
            "answer": "The answer.",
            "sources": [{"@id": "http://nohost/plone/doc", "title": "Doc"}],
            "error": None,
            "error_code": None,
        }
        # the security filter of the current user is passed through
        assert "allowedRolesAndUsers" in runner.call_args.args[2]

    def test_optional_params_passed(self, service):
        service.request.form.update({
            "q": "a question",
            "path_prefix": "/documents",
            "lang": "en",
        })
        with (
            mock.patch.object(service_module, "get_rag_config", return_value=CONFIG),
            mock.patch.object(
                service_module, "run_rag_search", return_value=RagResult()
            ) as runner,
        ):
            service.reply()
        assert runner.call_args.kwargs["path_prefix"] == "/documents"
        assert runner.call_args.kwargs["lang"] == "en"

    def test_extra_conditions_become_filters(self, service):
        import base64
        import json

        rows = [["portal_type", "string", {"in": ["Document"]}]]
        encoded = base64.b64encode(json.dumps(rows).encode()).decode()
        service.request.form.update({"q": "a question", "extra_conditions": encoded})
        with (
            mock.patch.object(service_module, "get_rag_config", return_value=CONFIG),
            mock.patch.object(
                service_module, "run_rag_search", return_value=RagResult()
            ) as runner,
        ):
            service.reply()
        assert runner.call_args.kwargs["extra_filters"] == ['portal_type:("Document")']

    def test_no_extra_conditions_is_none(self, service):
        service.request.form.update({"q": "a question"})
        with (
            mock.patch.object(service_module, "get_rag_config", return_value=CONFIG),
            mock.patch.object(
                service_module, "run_rag_search", return_value=RagResult()
            ) as runner,
        ):
            service.reply()
        assert runner.call_args.kwargs["extra_filters"] is None

    def test_empty_optional_params_are_none(self, service):
        service.request.form.update({"q": "a question", "path_prefix": " "})
        with (
            mock.patch.object(service_module, "get_rag_config", return_value=CONFIG),
            mock.patch.object(
                service_module, "run_rag_search", return_value=RagResult()
            ) as runner,
        ):
            service.reply()
        assert runner.call_args.kwargs["path_prefix"] is None
        assert runner.call_args.kwargs["lang"] is None


class TestRagSearchOverHttp:
    """The endpoint is registered and traversable (no LLM involved)."""

    @pytest.fixture
    def manager_session(self, functional):
        portal = functional["app"]["plone"]
        transaction.commit()
        session = RelativeSession(portal.absolute_url())
        session.headers.update({"Accept": "application/json"})
        session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
        return session

    def test_not_configured_over_http(self, manager_session):
        response = manager_session.get("/@rag-search", params={"q": "hello"})
        assert response.status_code == 200
        data = response.json()
        assert data["error_code"] == ERROR_NOT_CONFIGURED

    def test_missing_question_over_http(self, manager_session):
        response = manager_session.get("/@rag-search")
        assert response.status_code == 400
