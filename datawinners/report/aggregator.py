from datawinners.search.submission_index import get_label_to_be_displayed, get_entity, get_datasender_info
from mangrove.datastore.documents import SurveyResponseDocument
from mangrove.form_model.field import FieldSet, UniqueIdField, SelectField
from mangrove.form_model.form_model import FormModel
from mangrove.transport.contract.survey_response import get_survey_responses_by_form_model_id


BATCH_SIZE = 25


def _build_enrichable_questions(fields, path):
    temp_path = path
    temp_enrichable_questions = {"entity_questions": [], "choice_questions": []}
    for field in fields:
        if isinstance(field, UniqueIdField):
            setattr(field, "path", path[:-1])
            temp_enrichable_questions["entity_questions"].append(field)
        elif isinstance(field, SelectField):
            setattr(field, "path", path[:-1])
            temp_enrichable_questions["choice_questions"].append(field)
        elif isinstance(field, FieldSet):
            temp_path += field.code + ","
            intermediate_questions = _build_enrichable_questions(field.fields, temp_path)
            temp_enrichable_questions["entity_questions"].extend(intermediate_questions["entity_questions"])
            temp_enrichable_questions["choice_questions"].extend(intermediate_questions["choice_questions"])
    return temp_enrichable_questions


def _enrich_questions(dbm, row, questionnaire):
    enrichable_questions = _build_enrichable_questions(questionnaire.fields, "")

    for question in enrichable_questions["entity_questions"]:
        parent = _get_parent(question, row)
        parent[question.code] = get_entity(dbm, parent[question.code], question, questionnaire, SurveyResponseDocument._wrap_row(row))[0].get("q2")

    for question in enrichable_questions["choice_questions"]:
        parent = _get_parent(question, row)
        parent[question.code] = get_label_to_be_displayed(parent[question.code], question, questionnaire, SurveyResponseDocument._wrap_row(row))

    row.value["created_by"] = get_datasender_info(dbm,  SurveyResponseDocument._wrap_row(row)).get('name', '')

    return row


def _get_parent(question, row):
    path_components = question.path and question.path.split(",")
    return reduce(lambda prev_values, comp: prev_values[comp][0], path_components, row.value["values"])


def get_report_data(dbm, config):
    questionnaire = FormModel.get(dbm, config.questionnaires[0]["id"])
    rows = get_survey_responses_by_form_model_id(dbm, config.questionnaires[0]["id"], BATCH_SIZE)
    return [{config.questionnaires[0]["alias"]: _enrich_questions(dbm, row, questionnaire)} for index, row in enumerate(rows) if index < BATCH_SIZE]
