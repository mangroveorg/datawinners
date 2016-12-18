from itertools import permutations

from django.http import HttpResponse

from datawinners.main.database import get_database_manager
from datawinners.report.helper import get_indexable_question, distinct, strip_alias
from mangrove.datastore.report_config import get_report_config


def create_report_view(request, report_id):
    dbm = get_database_manager(request.user)
    config = get_report_config(dbm, report_id)
    filter_fields = [f['field'] for f in config.filters]
    date_field = config.date_filter and [strip_alias(config.date_filter['field'])] or []
    indexes = distinct([strip_alias(get_indexable_question(qn)) for qn in filter_fields]) + date_field
    questionnaire_ids = '"{0}"'.format('", "'.join([questionnaire['id'] for questionnaire in config.questionnaires]))
    dbm.create_view(get_report_view_name(report_id, "_".join(indexes)), _get_map_function(questionnaire_ids, _combined_view_key(map(_form_key_for_couch_view, indexes))), _get_reduce_function())
    return HttpResponse()


def delete_report_view(request, report_id):
    dbm = get_database_manager(request.user)
    config = get_report_config(dbm, report_id)
    filter_fields = [f['field'] for f in config.filters]
    date_field = config.date_filter and [strip_alias(config.date_filter['field'])] or []
    indexes = distinct([strip_alias(get_indexable_question(qn)) for qn in filter_fields]) + date_field
    del dbm.database["_design/" + get_report_view_name(report_id, "_".join(indexes))]
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


def _get_reduce_function():
    return "function(key, values, rereduce) {return values.join(',');}"


def _get_map_function(questionnaire_ids_string, combined_view_key):
    return "function(doc) {if(doc.document_type == 'SurveyResponse' && [%s].indexOf(doc.form_model_id) > -1) {emit([%s], %s);}}" % (questionnaire_ids_string, combined_view_key, combined_view_key and combined_view_key.split(",")[-1] or "1")

