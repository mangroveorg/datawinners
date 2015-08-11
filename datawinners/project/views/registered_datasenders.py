import json
from django.http import HttpResponse
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from datawinners.main.database import get_database_manager
from datawinners.settings import ELASTIC_SEARCH_HOST, ELASTIC_SEARCH_PORT
from datawinners.utils import strip_accents, lowercase_and_strip_accents
from mangrove.datastore.user_permission import get_questionnaires_for_user

def registered_ds_count(request):
    dbm = get_database_manager(request.user)
    result = []
    if request.user.get_profile().isNGOAdmin:
        rows = [row['value'] for row in dbm.load_all_rows_in_view('all_projects')]
    else:
        rows = get_questionnaires_for_user(request.user.id, dbm)
    
    for row in rows:
        if not row.get('is_poll', False):
            result.append({'name': row.get('name'), 'id': row.get('_id'),
                           'ds-count': get_registered_datasender_count(dbm, row.get('name'))})
    return HttpResponse(json.dumps(result))


def get_registered_datasender_count(dbm, questionnaire_name):
    es = Elasticsearch(hosts=[{"host": ELASTIC_SEARCH_HOST, "port": ELASTIC_SEARCH_PORT}])
    search = Search(using=es, index=dbm.database_name, doc_type='reporter')
    search = search.query("term", projects_value=lowercase_and_strip_accents(questionnaire_name))
    search = search.query("term", void=False)
    body = search.to_dict()
    return es.search(index=dbm.database_name, doc_type='reporter', body=body, search_type='count')['hits']['total']