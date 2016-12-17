from datetime import datetime

from pytz import utc

from datawinners.report.helper import is_idnr_question, get_indexable_question, distinct, strip_alias, get_idnr_question
from mangrove.datastore.entity import get_short_codes_by_entity_type
from mangrove.form_model.field import UniqueIdUIField
from mangrove.form_model.form_model import get_form_model_by_entity_type, FormModel


def get_report_filters(dbm, config, questionnaire):
    if not hasattr(config, "filters") or not config.filters:
        return {
            "idnr_filters": [],
            "date_filters": []
        }

    enrichable_questions = FormModel.get(dbm, questionnaire["id"]).special_questions()

    date_qns = enrichable_questions["date_questions"]
    entity_qns = enrichable_questions["entity_questions"]
    linked_idnr_qns, linked_date_qns = _get_linked_qns(dbm, entity_qns)
    filter_fields = [f['field'] for f in config.filters]

    idnr_filters = [{'field': _unique_id_with_options(qn, dbm), 'label': _get_filter_label_for_field(_get_identifier_with_alias(questionnaire["alias"], qn), config.filters)} for qn in entity_qns + linked_idnr_qns if _get_identifier_with_alias(questionnaire["alias"], qn) in filter_fields]
    date_filters = [{'field': _date_qn(qn), 'label': _get_filter_label_for_field(_get_identifier_with_alias(questionnaire["alias"], qn), config.filters)} for qn in date_qns + linked_date_qns if _get_identifier_with_alias(questionnaire["alias"], qn) in filter_fields]

    return {
        "idnr_filters": idnr_filters,
        "date_filters": date_filters
    }


def _get_filter_label_for_field(field, filters):
    return filter(lambda filter: filter['field'] == field, filters)[0]['label']


def filter_values(dbm, config, filters):
    combination_keys = []
    all_qns = []
    visited_qns = {}
    filter_fields = [f['field'] for f in config.filters]
    for qn in filter_fields:
        indexable_qn = get_indexable_question(qn)
        filter_value = _filter_value(qn, filters)
        keys = filter_value and [filter_value] or []
        if filter_value is None and _idnr_type(qn, filters) or isinstance(filter_value, dict):
            keys = _get_keys_for_idnr(dbm, _idnr_type(qn, filters), filter_value)
        if indexable_qn in visited_qns:
            keys = sorted(set(keys).intersection(set(visited_qns[indexable_qn])))
        visited_qns[indexable_qn] = keys
        all_qns.append(indexable_qn)
    combination_keys = reduce(lambda prev, qn: _combine_keys(prev, visited_qns.get(qn)), distinct(all_qns), combination_keys)
    return combination_keys, "_".join(distinct([strip_alias(qn) for qn in all_qns]))


def _combine_keys(combination_keys, keys):
    new_combination_keys = not keys and combination_keys or []
    for key in keys:
        if combination_keys:
            for combination_key in combination_keys:
                new_combination_keys.append(combination_key + [key])
        else:
            new_combination_keys.append([key])
    return new_combination_keys


def _get_keys_for_idnr(dbm, idnr, filters):
    return get_short_codes_by_entity_type(dbm, [idnr], filters=filters)


def _type(qn, filters):
    type_and_value = _filter_type_and_value(qn, filters)
    return type_and_value and type_and_value.split(";")[0]


def _idnr_type(qn, filters):
    type_and_value = _filter_type_and_value(qn, filters)
    return type_and_value and type_and_value.split(";")[1]


def _filter_value(qn, filters):
    type_and_value = _filter_type_and_value(qn, filters)
    value = type_and_value and type_and_value.split(";")[2] or None
    if _type(qn, filters) == "date":
        value = value and [datetime.strptime(date.strip(), "%d-%m-%Y").replace(tzinfo=utc) for date in value.split("to")]
    if is_idnr_question(qn):
        value = value and {get_idnr_question(qn): value}
    return value


def _filter_type_and_value(qn, filters):
    return filters.get(strip_alias(qn))


def _get_linked_qns(dbm, entity_qns):
    linked_date_qns = []
    linked_idnr_qns = []
    for field in entity_qns:
        id_number_fields = get_form_model_by_entity_type(dbm, [field.unique_id_type]).fields
        for child_field in id_number_fields:
            if child_field.type == 'unique_id':
                setattr(child_field, "path", _get_identifier(field))
                setattr(child_field, "idnr_type", field.unique_id_type)
                linked_idnr_qns.append(child_field)
            elif child_field.type == 'date':
                setattr(child_field, "path", _get_identifier(field))
                setattr(child_field, "idnr_type", field.unique_id_type)
                linked_date_qns.append(child_field)
    return linked_idnr_qns, linked_date_qns


def _get_identifier_with_alias(alias, question):
    return alias + "." + _get_identifier(question)


def _get_identifier(question):
    is_idnr_question = not question.parent_field_code and question.path
    return question.path + ("" if not question.path else ".." if is_idnr_question else ".") + (question.name if is_idnr_question else question.code)


def _unique_id_with_options(qn, dbm):
    field = UniqueIdUIField(qn, dbm)
    setattr(field, "path", qn.path)
    setattr(field, "identifier", _get_identifier(qn))
    if hasattr(qn, "idnr_type"):
        setattr(field, "idnr_type", qn.idnr_type)
    else:
        setattr(field, "idnr_type", qn.unique_id_type)
    return field


def _date_qn(qn):
    setattr(qn, "identifier", _get_identifier(qn))
    return qn
