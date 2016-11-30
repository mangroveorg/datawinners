from django.http import HttpResponse

from datawinners.main.database import get_database_manager
from mangrove.datastore.report_config import get_report_config


def create_report_view(request, report_id):
    dbm = get_database_manager(request.user)
    config = get_report_config(dbm, report_id)
    fields = [_form_key_for_couch_view(field) for field in config.filters]
    questionnaire_ids = '"{0}"'.format('", "'.join([questionnaire['id'] for questionnaire in config.questionnaires]))
    dbm.create_view(get_report_view_name(report_id), _get_map_function(questionnaire_ids, _combined_view_key(fields)), "")
    return HttpResponse()


def delete_report_view(request, report_id):
    dbm = get_database_manager(request.user)
    del dbm.database["_design/" + get_report_view_name(report_id)]
    return HttpResponse()


def _combined_view_key(fields):
    if len(fields) == 0:
        fields = ['doc._id']
    return ",".join(fields)


def get_report_view_name(report_id):
    return "report_" + report_id


def _form_key_for_couch_view(field_path):
    root_path = "doc.values"
    temp_path = ""
    for field in field_path.split(".")[1:]:
        temp_path += "['"
        temp_path += field
        temp_path += "'][0]"
    return root_path + temp_path[:-3]


def _get_map_function(questionnaire_ids_string, combined_view_key):
    return "function(doc) { if(doc.document_type == 'SurveyResponse' && [%s].indexOf(doc.form_model_id) > -1) {  emit([%s], 1) } }" % (questionnaire_ids_string, combined_view_key)

