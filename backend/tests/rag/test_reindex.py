from kitconcept.solr.rag import reindex as reindex_module
from kitconcept.solr.rag.config import RagConfig
from kitconcept.solr.rag.reindex import reindex_rag
from unittest import mock


CONFIG = RagConfig(
    base_url="http://llm.example.com",
    token=None,
    embed_model="test-embed",
    chat_model="test-chat",
)


class TestReindexRag:
    def test_disabled_is_a_noop(self):
        with mock.patch.object(reindex_module, "get_rag_config", return_value=None):
            assert reindex_rag(mock.Mock()) == 0

    def test_walks_and_indexes_all_content(self):
        objects = [(f"/plone/doc{i}", mock.Mock()) for i in range(5)]
        conn = mock.Mock()
        manager = mock.Mock()
        manager.getConnection.return_value = conn
        with (
            mock.patch.object(reindex_module, "get_rag_config", return_value=CONFIG),
            mock.patch.object(reindex_module, "queryUtility", return_value=manager),
            mock.patch.object(
                reindex_module, "findObjects", return_value=iter(objects)
            ),
            mock.patch.object(
                reindex_module, "ICheckIndexable", return_value=lambda: True
            ),
            mock.patch.object(reindex_module, "RagIndexProcessor") as proc_class,
        ):
            processed = reindex_rag(mock.Mock())
        assert processed == 5
        assert proc_class.return_value.index.call_count == 5
        conn.commit.assert_called_with(soft=True)

    def test_skips_non_indexable(self):
        objects = [("/plone/doc", mock.Mock())]
        manager = mock.Mock()
        manager.getConnection.return_value = mock.Mock()
        with (
            mock.patch.object(reindex_module, "get_rag_config", return_value=CONFIG),
            mock.patch.object(reindex_module, "queryUtility", return_value=manager),
            mock.patch.object(
                reindex_module, "findObjects", return_value=iter(objects)
            ),
            mock.patch.object(
                reindex_module, "ICheckIndexable", return_value=lambda: False
            ),
            mock.patch.object(reindex_module, "RagIndexProcessor") as proc_class,
        ):
            processed = reindex_rag(mock.Mock())
        assert processed == 0
        proc_class.return_value.index.assert_not_called()

    def test_no_connection_is_a_noop(self):
        manager = mock.Mock()
        manager.getConnection.return_value = None
        with (
            mock.patch.object(reindex_module, "get_rag_config", return_value=CONFIG),
            mock.patch.object(reindex_module, "queryUtility", return_value=manager),
        ):
            assert reindex_rag(mock.Mock()) == 0
