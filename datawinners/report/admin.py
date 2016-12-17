from itertools import permutations

from django.http import HttpResponse

from datawinners.main.database import get_database_manager
from datawinners.report.helper import get_indexable_question, distinct, strip_alias
from mangrove.datastore.report_config import get_report_config


def create_report_view(request, report_id):
    dbm = get_database_manager(request.user)
    config = get_report_config(dbm, report_id)
    filter_fields = [f['field'] for f in config.filters]
    indexes = list(permutations(distinct([strip_alias(get_indexable_question(qn)) for qn in filter_fields])))
    questionnaire_ids = '"{0}"'.format('", "'.join([questionnaire['id'] for questionnaire in config.questionnaires]))
    for index in indexes:
        dbm.create_view(get_report_view_name(report_id, "_".join(index)), _get_map_function(questionnaire_ids, _combined_view_key(map(_form_key_for_couch_view, index))), _get_reduce_function("count"))
    return HttpResponse()


def delete_report_view(request, report_id):
    dbm = get_database_manager(request.user)
    config = get_report_config(dbm, report_id)
    filter_fields = [f['field'] for f in config.filters]
    indexes = list(permutations(distinct([strip_alias(get_indexable_question(qn)) for qn in filter_fields])))
    for index in indexes:
        del dbm.database["_design/" + get_report_view_name(report_id, "_".join(index))]
    return HttpResponse()


def _combined_view_key(fields):
    if len(fields) == 0:
        fields = ['doc._id']
    return ",".join(fields)


def get_report_view_name(report_id, qn):
    return "report_" + report_id + "_" + qn


def _form_key_for_couch_view(field_path):
    root_path = "doc.values"
    temp_path = ""
    for field in field_path.split("."):
        temp_path += "['"
        temp_path += field
        temp_path += "'][0]"
    return root_path + temp_path[:-3]


def _get_reduce_function(function_name):
    builtin_reduce_functions = {"count": "_count"}
    return builtin_reduce_functions.get(function_name) or ""


def _get_map_function(questionnaire_ids_string, combined_view_key):
    return "function(doc) {if(doc.document_type == 'SurveyResponse' && [%s].indexOf(doc.form_model_id) > -1) {var keys = [%s];for(key in keys) {var date = keys[key] && keys[key].split('.');if(date && date.length == 3) {var tmp = date[0]; date[0] = date[1]; date[1] = tmp;date = Date.parse(date.join('/'));if(date) {keys[key] = date;}}}emit(keys, 1);}}" % (questionnaire_ids_string, combined_view_key)

