from mangrove.datastore.documents import SurveyResponseDocument
from mangrove.datastore.entity import get_all_entities
from mangrove.form_model.form_model import FormModel
from mangrove.transport.contract.survey_response import get_survey_response_by_report_view_name, \
    reduce_survey_response_by_report_view_name

from datawinners.search.submission_index import get_label_to_be_displayed, get_datasender_info


def get_report_data(dbm, config, keys, index):
    questionnaire = FormModel.get(dbm, config.questionnaires[0]["id"])
    enrichable_questions = questionnaire.special_questions()
    _load_entities_to_entity_questions(dbm, enrichable_questions)
    rows = get_survey_response_by_report_view_name(dbm, "report_"+config.id+"_"+index, keys)
    return [{config.questionnaires[0]["alias"]: _enrich_questions(dbm, row, questionnaire, enrichable_questions)} for row in rows]


def get_date_values(dbm, config, index):
    result_rows = get_survey_response_by_report_view_name(dbm, "report_"+config.id+"_"+index, []).rows
    return reduce(lambda prev, row: prev + row.key, result_rows, [])


def get_total_count(dbm, config, keys, index):
    result_rows = reduce_survey_response_by_report_view_name(dbm, "report_" + config.id + "_" + index, keys).rows
    return reduce(lambda prev, row: prev + row.value, result_rows, 0)


def _load_entities_to_entity_questions(dbm, enrichable_questions):
    for question in enrichable_questions["entity_questions"]:
        all_entities = get_all_entities(dbm, [question.unique_id_type])
        setattr(question, "entities", {entity.short_code: entity.data.get("name")["value"] for entity in all_entities})


def _enrich_questions(dbm, row, questionnaire, enrichable_questions):
    for question in enrichable_questions["entity_questions"]:
        parent = _get_parent(question, row)
        parent[question.code] = question.entities.get(parent.get(question.code)) or ""
    for question in enrichable_questions["choice_questions"]:
        parent = _get_parent(question, row)
        parent[question.code] = get_label_to_be_displayed(parent[question.code], question, questionnaire, SurveyResponseDocument._wrap_row(row))
    row["doc"]["created_by"] = get_datasender_info(dbm,  SurveyResponseDocument._wrap_row(row)).get('name', '')
    return row


def _get_parent(question, row):
    path_components = question.path and question.path.split(".")
    return reduce(lambda prev_values, comp: prev_values[comp][0], path_components, row["doc"]["values"])
