from datawinners.project.submission.analysis_helper import _get_linked_id_details
from datawinners.search.submission_index import get_label_to_be_displayed, get_entity, get_datasender_info
from mangrove.datastore.documents import SurveyResponseDocument
from mangrove.form_model.field import FieldSet, UniqueIdField, SelectField, UniqueIdUIField, DateField
from mangrove.form_model.form_model import FormModel, get_form_model_by_entity_type
from mangrove.transport.contract.survey_response import get_survey_responses_by_form_model_id


BATCH_SIZE = 25


def _build_enrichable_questions(fields, path):
    temp_path = path
    temp_enrichable_questions = {"entity_questions": [], "choice_questions": [], "date_questions": []}
    for field in fields:
        if isinstance(field, UniqueIdField):
            setattr(field, "path", path[:-1])
            temp_enrichable_questions["entity_questions"].append(field)
        elif isinstance(field, DateField):
            setattr(field, "path", path[:-1])
            temp_enrichable_questions["date_questions"].append(field)
        elif isinstance(field, SelectField):
            setattr(field, "path", path[:-1])
            temp_enrichable_questions["choice_questions"].append(field)
        elif isinstance(field, FieldSet):
            temp_path += field.code + "."
            intermediate_questions = _build_enrichable_questions(field.fields, temp_path)
            temp_enrichable_questions["date_questions"].extend(intermediate_questions["date_questions"])
            temp_enrichable_questions["choice_questions"].extend(intermediate_questions["choice_questions"])
            temp_enrichable_questions["entity_questions"].extend(intermediate_questions["entity_questions"])
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
    path_components = question.path and question.path.split(".")
    return reduce(lambda prev_values, comp: prev_values[comp][0], path_components, row.value["values"])


def get_report_data(dbm, config, page_number):
    questionnaire = FormModel.get(dbm, config.questionnaires[0]["id"])
    rows = get_survey_responses_by_form_model_id(dbm, config.questionnaires[0]["id"], BATCH_SIZE, BATCH_SIZE*(page_number-1))
    return [{config.questionnaires[0]["alias"]: _enrich_questions(dbm, row, questionnaire)} for index, row in enumerate(rows) if index < BATCH_SIZE]


def _linked_id_handler(field, linked_id_field, children, linked_id_details):
    setattr(linked_id_field, "path", field.path + "." + field.code)
    linked_id_details.append(linked_id_field)


def _get_path(alias, question):
    return alias + "." + question.path + "." + question.code


def _get_linked_idnr_qns(dbm, entity_qns):
    linked_idnrs = []
    [_get_linked_id_details(dbm, field, _linked_id_handler, [], linked_idnrs) for field in entity_qns]
    return linked_idnrs


def _get_linked_idnr_date_qns(dbm, entity_qns):
    date_qns = []
    for qn in entity_qns:
        id_number_fields = get_form_model_by_entity_type(dbm, [qn.unique_id_type]).fields
        for field in id_number_fields:
            if isinstance(field, DateField):
                setattr(field, "path", qn.path + "." + qn.code)
                date_qns.append(field)
    return date_qns


def get_report_filters(dbm, config):
    if not hasattr(config, "filters") or not config.filters:
        return []

    enrichable_questions = _build_enrichable_questions(FormModel.get(dbm, config.questionnaires[0]["id"]).fields, "")

    entity_qns = enrichable_questions["entity_questions"]
    entity_qns.extend(_get_linked_idnr_qns(dbm, entity_qns))
    idnrFilters = [UniqueIdUIField(qn, dbm) for qn in entity_qns if _get_path(config.questionnaires[0]["alias"], qn) in config.filters]

    date_qns = enrichable_questions["date_questions"]
    date_qns.extend(_get_linked_idnr_date_qns(dbm, entity_qns))
    dateFilters = [qn for qn in date_qns if _get_path(config.questionnaires[0]["alias"], qn) in config.filters]

    return {
        "idnr_filters": idnrFilters,
        "date_filters": dateFilters
    }
