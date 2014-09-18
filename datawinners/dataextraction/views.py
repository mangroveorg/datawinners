import json
from django.http import HttpResponse
from django_digest.decorators import httpdigest
import elasticutils
from datawinners.search.entity_search import SubjectQueryResponseCreator, SubjectQuery
from datawinners.settings import ELASTIC_SEARCH_URL, ELASTIC_SEARCH_TIMEOUT
from mangrove.form_model.form_model import get_form_model_by_code, header_fields
from datawinners.dataextraction.helper import  encapsulate_data_for_form, convert_to_json_file_download_response, generate_filename
from datawinners.main.database import get_database_manager


@httpdigest
def get_for_form(request, form_code, start_date=None, end_date=None):
    if request.method == 'GET':
        user = request.user
        dbm = get_database_manager(user)
        data_for_form = encapsulate_data_for_form(dbm, form_code, start_date, end_date)
        return convert_to_json_file_download_response(data_for_form, generate_filename(form_code, start_date, end_date))
    return HttpResponse("Error. Only support GET method.")


@httpdigest
def get_unique_id_for_form_code(request, form_code, start_date=None, end_date=None):
    if request.method == 'GET':
        user = request.user
        dbm = get_database_manager(user)
        form_model = get_form_model_by_code(dbm, form_code)
        header_dict = header_fields(form_model)
        required_field_names = SubjectQuery().get_headers(user, form_model.entity_type[0])
        query = create_elastic_search_query(form_model.entity_type[0], dbm)
        subjects = create_response(required_field_names, query, header_dict)
        return HttpResponse(json.dumps(subjects), content_type='application/json; charset=UTF-8')


def create_elastic_search_query(entity_type, dbm):
    return elasticutils.S().es(urls=ELASTIC_SEARCH_URL, timeout=ELASTIC_SEARCH_TIMEOUT).\
        indexes(dbm.database_name).doctypes(entity_type)[0:2000]

def create_response(required_field_names, query, header_dict):
        subjects = []
        required_field_names.append('void')
        header_dict.update({'void':'deleted'})
        label_names = header_dict.values()
        for res in query.values_dict(tuple(required_field_names)):
            subject = {}
            for index, key in enumerate(required_field_names):
                subject.update({label_names[index]: res.get(key)})
            subjects.append(subject)
        return subjects
