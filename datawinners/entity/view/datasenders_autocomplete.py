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
from elasticsearch_dsl.query import Q
from datawinners.search.query import ElasticUtilsHelper


class AllDataSenderAutoCompleteView(View):
    def get(self, request):
        database_name = get_database_name(request.user)
        search_text = lower(request.GET["term"] or "")
        es = Elasticsearch(hosts=[{"host": ELASTIC_SEARCH_HOST, "port": ELASTIC_SEARCH_PORT}])
        search = Search(using=es, index=database_name, doc_type="reporter")
        search = search.extra(**{"size":"10"})
        resp = []
        if search_text:
            query_text_escaped = ElasticUtilsHelper().replace_special_chars(search_text)
            query_fields = ["name","name_value","name_exact","short_code","short_code_exact","short_code_value"]
            search = search.query("query_string", query=query_text_escaped, fields=query_fields)
            search_results = search.execute()
            resp = [{"id": result.short_code, "label": self.get_label(result)} for result in search_results.hits ]
        return HttpResponse(json.dumps(resp))

    def get_label(self, r):
        if r.name:
            return r.name
        return r.mobile_number