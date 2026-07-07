from kitconcept.solr.rag.client import LLMClient
from kitconcept.solr.rag.client import LLMClientError
from kitconcept.solr.rag.client import LLMResponseError
from kitconcept.solr.rag.client import LLMTimeout
from kitconcept.solr.rag.client import SEARCH_DOCUMENT_PREFIX
from kitconcept.solr.rag.client import SEARCH_QUERY_PREFIX
from kitconcept.solr.rag.config import RagConfig
from unittest import mock

import pytest
import requests


@pytest.fixture
def config() -> RagConfig:
    return RagConfig(
        base_url="http://llm.example.com",
        token="secret",
        embed_model="test-embed",
        chat_model="test-chat",
    )


@pytest.fixture
def client(config) -> LLMClient:
    return LLMClient(config)


def embed_response(inputs):
    response = mock.Mock()
    response.status_code = 200
    response.json.return_value = {"embeddings": [[0.1, 0.2] for _ in inputs]}
    return response


class TestEmbed:
    def test_document_prefix_applied(self, client):
        with mock.patch.object(requests, "post") as post:
            post.side_effect = lambda url, json, **kw: embed_response(json["input"])
            client.embed_documents(["hello", "world"])
        sent = post.call_args.kwargs["json"]["input"]
        assert sent == [
            f"{SEARCH_DOCUMENT_PREFIX}hello",
            f"{SEARCH_DOCUMENT_PREFIX}world",
        ]

    def test_query_prefix_applied(self, client):
        with mock.patch.object(requests, "post") as post:
            post.side_effect = lambda url, json, **kw: embed_response(json["input"])
            vector = client.embed_query("what is the leave policy?")
        sent = post.call_args.kwargs["json"]["input"]
        assert sent == [f"{SEARCH_QUERY_PREFIX}what is the leave policy?"]
        assert vector == [0.1, 0.2]

    def test_batching(self, client):
        texts = [f"text {i}" for i in range(70)]
        with mock.patch.object(requests, "post") as post:
            post.side_effect = lambda url, json, **kw: embed_response(json["input"])
            vectors = client.embed_documents(texts)
        # 70 texts with batch size 32 -> 3 requests
        assert post.call_count == 3
        assert len(vectors) == 70

    def test_url_and_auth_header(self, client):
        with mock.patch.object(requests, "post") as post:
            post.side_effect = lambda url, json, **kw: embed_response(json["input"])
            client.embed_documents(["hello"])
        assert post.call_args.args[0] == "http://llm.example.com/ollama/api/embed"
        assert post.call_args.kwargs["headers"]["Authorization"] == "Bearer secret"

    def test_no_token_no_auth_header(self, config):
        client = LLMClient(
            RagConfig(
                base_url=config.base_url,
                token=None,
                embed_model=config.embed_model,
                chat_model=config.chat_model,
            )
        )
        with mock.patch.object(requests, "post") as post:
            post.side_effect = lambda url, json, **kw: embed_response(json["input"])
            client.embed_documents(["hello"])
        assert "Authorization" not in post.call_args.kwargs["headers"]

    def test_timeout_maps_to_typed_error(self, client):
        with (
            mock.patch.object(requests, "post", side_effect=requests.Timeout),
            pytest.raises(LLMTimeout),
        ):
            client.embed_documents(["hello"])

    def test_connection_error_maps_to_typed_error(self, client):
        with (
            mock.patch.object(requests, "post", side_effect=requests.ConnectionError),
            pytest.raises(LLMClientError),
        ):
            client.embed_documents(["hello"])

    def test_http_error_status(self, client):
        response = mock.Mock()
        response.status_code = 503
        response.text = "unavailable"
        with (
            mock.patch.object(requests, "post", return_value=response),
            pytest.raises(LLMResponseError),
        ):
            client.embed_documents(["hello"])

    def test_embedding_count_mismatch(self, client):
        response = mock.Mock()
        response.status_code = 200
        response.json.return_value = {"embeddings": [[0.1]]}
        with (
            mock.patch.object(requests, "post", return_value=response),
            pytest.raises(LLMResponseError),
        ):
            client.embed_documents(["hello", "world"])

    def test_overlong_input_logs_warning(self, client, caplog):
        long_text = "word " * 1000
        with mock.patch.object(requests, "post") as post:
            post.side_effect = lambda url, json, **kw: embed_response(json["input"])
            with caplog.at_level("WARNING", logger="kitconcept.solr.rag"):
                client.embed_documents([long_text])
        assert any("truncated" in r.message for r in caplog.records)


class TestChat:
    def chat_response(self, content="the answer"):
        response = mock.Mock()
        response.status_code = 200
        response.json.return_value = {"choices": [{"message": {"content": content}}]}
        return response

    def test_basic_answer(self, client):
        with mock.patch.object(
            requests, "post", return_value=self.chat_response()
        ) as post:
            answer = client.chat("a question", system="a system prompt")
        assert answer == "the answer"
        assert post.call_args.args[0] == "http://llm.example.com/api/chat/completions"
        payload = post.call_args.kwargs["json"]
        assert payload["stream"] is False
        assert payload["messages"][0] == {
            "role": "system",
            "content": "a system prompt",
        }
        assert payload["messages"][1] == {"role": "user", "content": "a question"}

    def test_unexpected_shape(self, client):
        response = mock.Mock()
        response.status_code = 200
        response.json.return_value = {"unexpected": True}
        with (
            mock.patch.object(requests, "post", return_value=response),
            pytest.raises(LLMResponseError),
        ):
            client.chat("a question")
