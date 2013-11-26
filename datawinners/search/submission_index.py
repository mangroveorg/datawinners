from babel.dates import format_datetime
from datawinners.main.database import get_db_manager
from datawinners.search.index_utils import get_fields_mapping, get_elasticsearch_handle
from mangrove.datastore.datadict import DataDictType
from mangrove.form_model.field import TextField, DateField
from mangrove.form_model.form_model import get_form_model_by_code


def create_submission_mapping(dbm, form_model):
    es = get_elasticsearch_handle()
    fields = _metadata_mapping(dbm)
    fields.extend(form_model.fields)
    mapping = get_fields_mapping(form_model.id, fields, 'code')
    es.put_mapping(dbm.database_name, form_model.id, mapping)


def update_submission_search_index(submission_doc, feed_dbm, refresh_index=True):
    es = get_elasticsearch_handle()
    dbm = get_db_manager(feed_dbm.database_name.replace("feed_", ""))
    form_model = get_form_model_by_code(dbm, submission_doc.form_code)
    search_dict = _meta_fields(submission_doc)
    _update_with_form_model_fields(submission_doc, search_dict)
    es.index(dbm.database_name, form_model.id, search_dict, id=submission_doc.id, refresh=refresh_index)


def _metadata_mapping(dbm):
    return [DateField("Submission Date", "date", "Submission Date", 'submission_date_format', DataDictType(dbm)),
            TextField("Status", "status", "Status", DataDictType(dbm)),
            TextField("Datasender Name", "ds_name", "Datasender Name", DataDictType(dbm)),
            TextField("Datasender Id", "ds_id", "Datasender Id", DataDictType(dbm)),
            TextField("Entity Short Code", "entity_short_code", "Entity short code", DataDictType(dbm)),
            TextField("Error message", "error_msg", "Error Message", DataDictType(dbm))]


def _meta_fields(submission_doc):
    search_dict = {}
    search_dict.update({"status": submission_doc.status.capitalize()})
    search_dict.update(
        {"date": format_datetime(submission_doc.survey_response_modified_time, "MMM. dd, yyyy, hh:mm a", locale="en")})
    search_dict.update({"ds_id": submission_doc.data_sender.get('id')})
    search_dict.update({"ds_name": submission_doc.data_sender.get('last_name')})
    search_dict.update({"error_msg": submission_doc.error_message})
    return search_dict


def _update_with_form_model_fields(submission_doc, search_dict):
    for key in submission_doc.values:
        field = submission_doc.values[key]
        value = field if submission_doc.status == 'error' else field.get("answer")
        if isinstance(value, dict):
            if field.get("is_entity_question"):
                search_dict.update({"entity_short_code": value.get("id")})
                value = value.get("name")
            else:
                value = ','.join(value.values())
        search_dict.update({key: value})
    search_dict.update({'void': submission_doc.void})
    return search_dict