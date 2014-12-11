import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_view_exempt, csrf_response_exempt
import elasticutils

from datawinners.accountmanagement.decorators import is_datasender
from datawinners.common.constant import DELETED_IDENTIFICATION_NUMBER
from datawinners.entity.helper import delete_entity_instance
from datawinners.entity.views import log_activity, get_success_message
from datawinners.main.database import get_database_manager
from datawinners.project.helper import get_projects_by_unique_id_type
from datawinners.search.entity_search import SubjectQuery
from datawinners.search.index_utils import es_questionnaire_field_name
from datawinners.settings import ELASTIC_SEARCH_URL, ELASTIC_SEARCH_TIMEOUT
from mangrove.datastore.documents import EntityActionDocument, HARD_DELETE, SOFT_DELETE
from mangrove.datastore.entity import get_by_short_code, delete_data_record
from mangrove.form_model.form_model import get_form_model_by_entity_type, header_fields
from mangrove.transport import TransportInfo


def _log_soft_deleted_unique_ids(all_ids, dbm, entity_type):
    for id in all_ids:
        dbm._save_document(EntityActionDocument(entity_type, id, SOFT_DELETE))


def _soft_delete_unique_ids(all_ids, entity_type, dbm, request):
    transport_info = TransportInfo("web", request.user.username, "")
    delete_entity_instance(dbm, all_ids, entity_type, transport_info)
    _log_soft_deleted_unique_ids(all_ids, dbm, entity_type)
    log_activity(request, DELETED_IDENTIFICATION_NUMBER, "%s: [%s]" % (entity_type.capitalize(), ", ".join(all_ids)))


def _delete_unique_id_from_elastic_search(dbm, entity_type, document_id):
    elasticutils.get_es(urls=ELASTIC_SEARCH_URL, timeout=ELASTIC_SEARCH_TIMEOUT).delete(dbm.database_name, entity_type,
                                                                                        document_id)


def _refresh_elastic_search_index(dbm):
    elasticutils.get_es(urls=ELASTIC_SEARCH_URL, timeout=ELASTIC_SEARCH_TIMEOUT).refresh(index=dbm.database_name)


def _hard_delete_unique_ids(unique_ids, dbm, form_model, request):
    for unique_id in unique_ids:
        entity = get_by_short_code(dbm, unique_id, form_model.entity_type)
        _delete_unique_id_from_elastic_search(dbm, form_model.entity_type[0], entity.id)
        delete_data_record(dbm, form_model.form_code, unique_id)
        dbm._save_document(EntityActionDocument(form_model.entity_type[0], unique_id, HARD_DELETE))
        entity.delete()
    if unique_ids:
        _refresh_elastic_search_index(dbm)
        log_activity(request, DELETED_IDENTIFICATION_NUMBER, "%s: [%s]" % (form_model.entity_type.capitalize(), ", ".join(unique_ids)))


def _check_if_questionnaire_has_submissions_with_unique_id(manager, project, unique_id):
    field_names = [_get_unique_id_es_field_name(field, project.id) for field in project.entity_questions]
    query = elasticutils.S().es(urls=ELASTIC_SEARCH_URL, timeout=ELASTIC_SEARCH_TIMEOUT).indexes(
        manager.database_name).doctypes(project.id)[:1]
    for field_name in field_names:
        params = {field_name: unique_id}
        query = query.filter(**params)

    return list(query.values_list('status'))


def _get_unique_id_es_field_name(field, project_id):
    unique_id_field_name = es_questionnaire_field_name(field.code, project_id)
    return unique_id_field_name + '_unique_code_exact'


def _get_unique_ids_to_hard_delete(unique_ids, entity_type, manager):
    projects = get_projects_by_unique_id_type(manager, [entity_type])
    unique_ids_with_submissions = []
    for project in projects:
        for unique_id in unique_ids:

            if unique_id in unique_ids_with_submissions:
                continue

            if _check_if_questionnaire_has_submissions_with_unique_id(manager, project, unique_id):
                unique_ids_with_submissions.append(unique_id)

    return set(unique_ids) - set(unique_ids_with_submissions)


@csrf_view_exempt
@csrf_response_exempt
@login_required
@is_datasender
def delete_subjects(request):
    manager = get_database_manager(request.user)
    entity_type = request.POST['entity_type']
    form_model = get_form_model_by_entity_type(manager, [entity_type])
    all_ids = _subject_short_codes_to_delete(request, form_model, entity_type)
    hard_delete_unique_ids = _get_unique_ids_to_hard_delete(all_ids, entity_type, manager)
    _hard_delete_unique_ids(hard_delete_unique_ids, manager, form_model, request)
    unique_ids_to_soft_delete = list(set(all_ids) - set(hard_delete_unique_ids))
    _soft_delete_unique_ids(unique_ids_to_soft_delete, entity_type, manager, request)
    message = get_success_message(entity_type)
    return HttpResponse(json.dumps({'success': True, 'message': message}))


def _subject_short_codes_to_delete(request, form_model, entity_type):
    if request.POST.get("all_selected") == 'true':
        search_query = request.POST.get('search_query')
        subject_list = SubjectQuery().query(request.user, entity_type, search_query)
        short_code_index = header_fields(form_model).keys().index("short_code")
        return [s[short_code_index] for s in subject_list]

    return request.POST['all_ids'].split(';')