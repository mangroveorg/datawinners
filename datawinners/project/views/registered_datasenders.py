import json
from django.http import HttpResponse
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from datawinners.main.database import get_database_manager


def registered_ds_count(request):
    dbm = get_database_manager(request.user)
    result = []
    for row in dbm.database.view("project_names/project_names"):
        questionnaire_name = row['value']['name']
        result.append({'name': questionnaire_name, 'id': row['value']['id'],
                       'ds-count': get_registered_datasender_count(dbm, questionnaire_name)})

    return HttpResponse(json.dumps(result))


def get_registered_datasender_count(dbm, questionnaire_name):
    es = Elasticsearch()
    search = Search(using=es, index=dbm.database_name, doc_type='reporter')
    search = search.query("term", projects_value=questionnaire_name)
    body = search.to_dict()
    return es.search(index=dbm.database_name, doc_type='reporter', body=body, search_type='count')['hits']['total']