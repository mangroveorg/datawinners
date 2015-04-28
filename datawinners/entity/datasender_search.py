from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from datawinners.settings import ELASTIC_SEARCH_HOST, ELASTIC_SEARCH_PORT


def datasender_count_with(email):
    es = Elasticsearch(hosts=[{"host": ELASTIC_SEARCH_HOST, "port": ELASTIC_SEARCH_PORT}])

    search = Search(using=es, doc_type='reporter').filter("term", email_value=email.lower(), cache=False)
    search = search.filter("term", void=False)
    search = search.extra(from_=0, size=1)
    body = search.to_dict()

    return es.search(doc_type='reporter', body=body, search_type='count')['hits']['total']



