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
            "fq": "-showinsearch:False -portal_type:Image -portal_type:Glossary -portal_type:FAQ -portal_type:(File) -portal_type:(Rezept) -portal_type:Link"
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
        return getMultiAdapter(
            (brain, self.request), ISerializeToJsonSummary
        )()

    def serialize_non_plone_type(self, obj):
        obj_id = obj.get("UID").split("_")[1]
        obj['@type'] = obj.get("portal_type")
        if obj.get("portal_type") == "jungzeelandia.Product":
            obj['@id'] = f"/alle-produkte/{obj_id}"
            obj["type_title"] = "Produkt"
        if obj.get("portal_type") == "jungzeelandia.Recipe":
            obj['@id'] = f"/alle-rezepte/{obj_id}"
            obj["type_title"] = "Rezept"
        obj.pop("portal_type", None)

        return obj





    def parse_response(self, data):
        if "error" in data or "response" not in data:
            error = {"suggestions": [], "error": "No response from solr"}
            if "error" in data:
                error["error"] = data["error"]
            return error
        # uids = [doc["UID"] for doc in data["response"]["docs"] if doc.get("portal_type") not in ["jungzeelandia.Recipe", "jungzeelandia.Product"]]
        # brains = {brain["UID"]: brain for brain in api.content.find(UID=uids)}

        resp = []
        for obj in data["response"]["docs"]:
            if obj.get("portal_type")in ["jungzeelandia.Product","jungzeelandia.Recipe"]:
                resp.append(self.serialize_non_plone_type(obj))

            elif obj.get("portal_type"):
                brain = api.content.find(UID=obj["UID"])[0]
                resp.append(self.serialize_brain(brain))
        return resp

    def reply(self):
        query = self.request.form.get("query", "")
        data = self.query_suggest(query)
        data = self.parse_response(data)

        if isinstance(data, dict):
            return data
        return {"suggestions": data}
