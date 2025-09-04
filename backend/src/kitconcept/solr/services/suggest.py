from collective.solr.interfaces import ISolrConnectionManager
from collective.solr.utils import removeSpecialCharactersAndOperators
from plone import api
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.services import Service
from zope.component import getMultiAdapter
from zope.component import queryUtility

import json
import urllib


class SolrSuggest(Service):
    def query_suggest(self, query):
        language = api.portal.get_current_language(self.context)
        manager = queryUtility(ISolrConnectionManager)
        if manager is None:
            return {"error": "Solr is not installed or activated"}
        connection = manager.getConnection()
        if connection is None:
            return {"error": "Solr is not installed or activated"}
        data = {"error": "no response"}
        parameters = {
            "q": removeSpecialCharactersAndOperators(query),
            "fq": "-showinsearch:False -portal_type:Image -portal_type:Glossary -portal_type:FAQ -portal_type:(FAQ Item) -portal_type:(FAQ Category) -portal_type:Link +Language:%s"
            % language,
        }
        querystring = urllib.parse.urlencode(parameters)
        url = "{}/{}".format(connection.solrBase, "suggest?%s" % querystring)
        try:
            res = connection.doGet(url, {"Accept": "application/json"})
            data = json.loads(res.read())
        finally:
            if not connection.persistent:
                connection.conn.close()
        return data

    def serialize_brain(self, brain):
        if brain["portal_type"] in ["Member"]:
            obj = brain.getObject()
            data = getMultiAdapter((obj, self.request), ISerializeToJson)()
            data["@id"] = obj.absolute_url()
            return data

        return getMultiAdapter((brain, self.request), ISerializeToJsonSummary)()

    def parse_response(self, data):
        if "error" in data or "response" not in data:
            error = {"suggestions": [], "error": "No response from solr"}
            if "error" in data:
                error["error"] = data["error"]
            return error
        uids = [doc["UID"] for doc in data["response"]["docs"]]

        brains = {brain["UID"]: brain for brain in api.content.find(UID=uids)}
        return [self.serialize_brain(brains[uid]) for uid in uids if uid in brains]

    def reply(self):
        query = self.request.form.get("query", "")
        data = self.query_suggest(query)
        data = self.parse_response(data)
        if isinstance(data, dict):
            return data
        return {"suggestions": data}
