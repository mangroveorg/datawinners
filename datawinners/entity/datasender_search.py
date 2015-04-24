from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search


def datasender_count_with(email):
    es = Elasticsearch()

    search = Search(using=es, doc_type='reporter').filter("term", email_value=email.lower(), cache=False)
    search = search.extra(from_=0, size=1)
    body = search.to_dict()

    return es.search(doc_type='reporter', body=body, search_type='count')['hits']['total']



