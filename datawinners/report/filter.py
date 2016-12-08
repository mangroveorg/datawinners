from datetime import datetime

from pytz import utc

from datawinners.project.submission.analysis_helper import _get_linked_id_details
from datawinners.report.helper import idnr_question, get_indexable_question, distinct, strip_alias
from mangrove.datastore.entity import get_short_codes_by_entity_type
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


def filter_values(dbm, config, filters):
    endkey = []
    startkey = []
    all_qns = []
    visited_idnr_qns = {}
    for qn in config.filters:
        indexable_qn = get_indexable_question(qn)
        if idnr_question(qn):
            idnr = _idnr_type(qn, filters)
            filter_value = _filter_value(qn, filters)
            if filter_value:
                endkey.pop()
                startkey.pop()
                entities = _get_entities_for_idnr(dbm, idnr, {qn.split(".")[-1:][0]: filter_value})
                if indexable_qn in visited_idnr_qns:
                    entities = list(set(entities).intersection(set(visited_idnr_qns[indexable_qn])))
                endkey.append(entities and entities[-1:][0])
                startkey.append(entities and entities[0])
                visited_idnr_qns[indexable_qn] = entities
        else:
            filter_value = _filter_value(qn, filters)
            endkey.append(isinstance(filter_value, list) and int(filter_value[1].strftime("%s")) or filter_value)
            startkey.append(isinstance(filter_value, list) and int(filter_value[0].strftime("%s")) or filter_value)
        all_qns.append(strip_alias(indexable_qn))
    startkey, endkey, index = _reorder_keys_for_index(startkey, endkey, distinct(all_qns))
    return startkey, endkey, index


def _reorder_keys_for_index(startkey, endkey, all_qns):
    empty_key_indices = [startkey.index(key) for key in startkey if key == {}]
    sorted_endkey = filter(lambda key: key != {}, endkey)
    sorted_startkey = filter(lambda key: key != {}, startkey)
    for index in empty_key_indices:
        sorted_endkey.append({})
        qn = all_qns[index]
        del all_qns[index]
        all_qns.append(qn)
    return sorted_startkey, sorted_endkey, "_".join(all_qns)


def _get_entities_for_idnr(dbm, idnr, filters):
    return get_short_codes_by_entity_type(dbm, [idnr], filters=filters)


def _type(qn, filters):
    type_and_value = _filter_type_and_value(qn, filters)
    return type_and_value and type_and_value.split(";")[0]


def _idnr_type(qn, filters):
    type_and_value = _filter_type_and_value(qn, filters)
    return type_and_value and type_and_value.split(";")[1]


def _filter_value(qn, filters):
    type_and_value = _filter_type_and_value(qn, filters)
    if type_and_value:
        type = type_and_value.split(";")[0]
        value = type_and_value.split(";")[2] or {}
        return value and (type == 'date' and [datetime.strptime(date.strip(), "%d-%m-%Y").replace(tzinfo=utc) for date in value.split("to")] or value)
    return {}


def _filter_type_and_value(qn, filters):
    return filters.get(strip_alias(qn))


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
                setattr(field, "idnr_type", qn.unique_id_type)
                date_qns.append(field)
    return date_qns


def _get_identifier_with_alias(alias, question):
    return alias + "." + _get_identifier(question)


def _get_identifier(question):
    is_idnr_question = not question.parent_field_code and question.path
    return question.path + (".." if is_idnr_question else ".") + (question.name if is_idnr_question else question.code)


def _unique_id_with_options(qn, dbm):
    field = UniqueIdUIField(qn, dbm)
    setattr(field, "path", qn.path)
    setattr(field, "identifier", _get_identifier(qn))
    hasattr(qn, "idnr_type") and setattr(field, "idnr_type", qn.idnr_type)
    return field


def _date_qn(qn):
    setattr(qn, "identifier", _get_identifier(qn))
    return qn


def _linked_id_handler(field, linked_id_field, children, linked_id_details):
    setattr(linked_id_field, "path", _get_identifier(field))
    setattr(linked_id_field, "idnr_type", field.unique_id_type)
    linked_id_details.append(linked_id_field)
