import json
from string import lower
from django.http import HttpResponse
from django.views.generic.base import View
import elasticutils
from datawinners.main.utils import get_database_name
from datawinners.settings import ELASTIC_SEARCH_URL, ELASTIC_SEARCH_TIMEOUT,\
    ELASTIC_SEARCH_HOST, ELASTIC_SEARCH_PORT
from elasticsearch.client import Elasticsearch
from elasticsearch_dsl.search import Search
from celery.bin.celery import result


class AllDataSenderAutoCompleteView(View):
    def get(self, request):
        database_name = get_database_name(request.user)
        search_text = request.GET["term"]
        es = Elasticsearch(hosts=[{"host": ELASTIC_SEARCH_HOST, "port": ELASTIC_SEARCH_PORT}])
        search = Search(using=es, index=database_name, doc_type="reporter")
        search = search.extra(**{"size":"10"})
        if search_text:
            query_params = {
                     "query":search_text+"*",
                     "fields":["name_value","short_code_value"],
                     "analyze_wildcard":True
                     }
        search = search.query("query_string", **query_params)
        search_results = search.execute()
        resp = [{"id": result.short_code, "label": self.get_label(result)} for result in search_results.hits ]
        return HttpResponse(json.dumps(resp))

    def get_label(self, r):
        if r.name:
            return r.name
        return r.mobile_number