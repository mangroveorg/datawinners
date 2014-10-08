import json
from django.http import HttpResponse
from django_digest.decorators import httpdigest
import elasticutils
from datawinners.main.database import get_database_manager
from datawinners.search.entity_search import SubjectQuery
from datawinners.settings import ELASTIC_SEARCH_URL, ELASTIC_SEARCH_TIMEOUT
from mangrove.errors.MangroveException import FormModelDoesNotExistsException
from mangrove.form_model.form_model import get_form_model_by_code, header_fields


def _create_elastic_search_query(entity_type, dbm, response_limit):
    return elasticutils.S().es(urls=ELASTIC_SEARCH_URL, timeout=ELASTIC_SEARCH_TIMEOUT).\
        indexes(dbm.database_name).doctypes(entity_type)[0:response_limit]


def _create_response(required_field_names, query, header_dict):
        subjects = []
        required_field_names.append('void')
        header_dict.update({'deleted': 'deleted'})
        label_names = header_dict.keys()
        for res in query.values_dict(tuple(required_field_names)):
            subject = {}
            for index, key in enumerate(required_field_names):
                subject.update({label_names[index]: res.get(key)})
            subjects.append(subject)
        header_dict.pop('deleted')

        return subjects


def _get_response(dbm, form_code, user, response_limit):
    """
    :param dbm: database-manager
    :param form_code: questionnaire-code
    :param user: authenticated-usr
    :param response_limit: limit the number of unique-id returned
    :return: tuple of unique-ids and questionnaire details
    unique-ids is a list of dicts where each dict consist of question-name: question-label
    questionnaire details is a dict of question-name:question-label
    """
    try:
        form_model = get_form_model_by_code(dbm, form_code)
        if not form_model.is_entity_registration_form():
            return None, None
    except FormModelDoesNotExistsException:
        return None, None
    header_dict = header_fields(form_model)
    required_field_names = SubjectQuery().get_headers(user, form_model.entity_type[0])
    query = _create_elastic_search_query(form_model.entity_type[0], dbm, response_limit)
    unique_ids = _create_response(required_field_names, query, header_dict)
    return unique_ids, header_dict


@httpdigest
def get_unique_ids_for_form_code(request, form_code):
    if request.method == 'GET':
        user = request.user
        dbm = get_database_manager(user)
        response_limit = request.GET.get('limit', 15000)
        unique_ids, questionnaire_dict = _get_response(dbm, form_code, user, response_limit)
        if unique_ids is None:
            return HttpResponse(status=404)
        return HttpResponse(json.dumps({
                                        'unique-ids': unique_ids,
                                        'questionnaire': questionnaire_dict
                                       }), content_type='application/json; charset=UTF-8')