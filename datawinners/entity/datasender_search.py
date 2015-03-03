from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search


def datasender_count_with(email, short_code=None):
    es = Elasticsearch()

    search = Search(using=es, doc_type='reporter').query("term", email_value=email.lower())
    if short_code:
        search = search.query("term", short_code_value=short_code.lower())
    body = search.to_dict()

    return es.search(doc_type='reporter', body=body, search_type='count')['hits']['total']



