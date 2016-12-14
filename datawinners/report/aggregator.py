from datawinners.search.submission_index import get_label_to_be_displayed, get_entity, get_datasender_info
from mangrove.datastore.documents import SurveyResponseDocument
from mangrove.form_model.form_model import FormModel
from mangrove.transport.contract.survey_response import get_total_number_of_survey_reponse_by_form_model_id, get_survey_response_by_report_view_name

BATCH_SIZE = 25


def get_report_data(dbm, config, page_number, startkey, endkey, index):
    questionnaire = FormModel.get(dbm, config.questionnaires[0]["id"])
    enrichable_questions = questionnaire.special_questions()
    rows = get_survey_response_by_report_view_name(dbm, "report_"+config.id+"_"+index, BATCH_SIZE, BATCH_SIZE*(page_number-1), startkey, endkey)
    return [{config.questionnaires[0]["alias"]: _enrich_questions(dbm, row, questionnaire, enrichable_questions)} for index, row in enumerate(rows) if index < BATCH_SIZE]


def get_total_count(dbm, config):
    questionnaire = FormModel.get(dbm, config.questionnaires[0]["id"])
    return get_total_number_of_survey_reponse_by_form_model_id(dbm, questionnaire.id).next().value['count']


def _enrich_questions(dbm, row, questionnaire, enrichable_questions):

    for question in enrichable_questions["entity_questions"]:
        parent = _get_parent(question, row)
        parent[question.code] = get_entity(dbm, parent[question.code], question, questionnaire, SurveyResponseDocument._wrap_row(row))[0].get("q2")

    for question in enrichable_questions["choice_questions"]:
        parent = _get_parent(question, row)
        parent[question.code] = get_label_to_be_displayed(parent[question.code], question, questionnaire, SurveyResponseDocument._wrap_row(row))

    row["doc"]["created_by"] = get_datasender_info(dbm,  SurveyResponseDocument._wrap_row(row)).get('name', '')

    return row


def _get_parent(question, row):
    path_components = question.path and question.path.split(".")
    return reduce(lambda prev_values, comp: prev_values[comp][0], path_components, row["doc"]["values"])
