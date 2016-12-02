from datawinners.project.submission.analysis_helper import _get_linked_id_details
from datawinners.report.helper import not_idnr_filter
from mangrove.form_model.field import DateField, UniqueIdUIField
from mangrove.form_model.form_model import get_form_model_by_entity_type, FormModel


def get_report_filters(dbm, config):
    if not hasattr(config, "filters") or not config.filters:
        return {
            "idnr_filters": [],
            "date_filters": []
        }

    enrichable_questions = FormModel.get(dbm, config.questionnaires[0]["id"]).special_questions()

    entity_qns = enrichable_questions["entity_questions"]
    entity_qns.extend(_get_linked_idnr_qns(dbm, entity_qns))
    idnrFilters = [_unique_id_with_options(qn, dbm) for qn in entity_qns if _get_identifier_with_alias(config.questionnaires[0]["alias"], qn) in config.filters]

    date_qns = enrichable_questions["date_questions"]
    date_qns.extend(_get_linked_idnr_date_qns(dbm, entity_qns))
    dateFilters = [_date_qn(qn) for qn in date_qns if _get_identifier_with_alias(config.questionnaires[0]["alias"], qn) in config.filters]

    return {
        "idnr_filters": idnrFilters,
        "date_filters": dateFilters
    }


def filter_values(request, config):
    qn_alias = config.questionnaires[0]["alias"]
    return filter(
        lambda val: val is not None,
        [_filter_value(qn_alias, qn, request) if not_idnr_filter(qn) else None for qn in config.filters]
    )


def _filter_value(alias, qn, request):
    return request.GET.get(qn.replace(alias + ".", "")) or {}


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
                setattr(field, "path", _get_identifier(qn))
                date_qns.append(field)
    return date_qns


def _get_identifier_with_alias(alias, question):
    return alias + "." + _get_identifier(question)


def _get_identifier(question):
    return question.path + (".." if not question.parent_field_code and question.path else ".") + question.code


def _unique_id_with_options(qn, dbm):
    field = UniqueIdUIField(qn, dbm)
    setattr(field, "path", qn.path)
    setattr(field, "identifier", _get_identifier(qn))
    return field


def _date_qn(qn):
    setattr(qn, "identifier", _get_identifier(qn))
    return qn


def _linked_id_handler(field, linked_id_field, children, linked_id_details):
    setattr(linked_id_field, "path", _get_identifier(field))
    linked_id_details.append(linked_id_field)
