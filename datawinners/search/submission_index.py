from string import lower
from babel.dates import format_datetime
from mangrove.datastore.documents import SurveyResponseDocument
from datawinners.main.database import get_db_manager
from datawinners.search.index_utils import get_fields_mapping, get_elasticsearch_handle
from mangrove.datastore.datadict import DataDictType
from mangrove.datastore.entity import get_by_short_code_include_voided
from mangrove.form_model.field import TextField, DateField
from mangrove.form_model.form_model import get_form_model_by_code


def create_submission_mapping(dbm, form_model):
    es = get_elasticsearch_handle()
    fields = _metadata_mapping(dbm)
    fields.extend(form_model.fields)
    mapping = get_fields_mapping(form_model.id, fields, 'code')
    es.put_mapping(dbm.database_name, form_model.id, mapping)


def update_submission_search_index(feed_submission_doc, feed_dbm, refresh_index=True):
    es = get_elasticsearch_handle()
    dbm = get_db_manager(feed_dbm.database_name.replace("feed_", ""))
    form_model = get_form_model_by_code(dbm, feed_submission_doc.form_code)
    submission_doc = SurveyResponseDocument.load(dbm.database, feed_submission_doc.id)
    search_dict = _meta_fields(feed_submission_doc, submission_doc)
    _update_with_form_model_fields(dbm, feed_submission_doc, search_dict, form_model)
    es.index(dbm.database_name, form_model.id, search_dict, id=feed_submission_doc.id, refresh=refresh_index)



def _metadata_mapping(dbm):
    return [DateField("Submission Date", "date", "Submission Date", 'submission_date_format', DataDictType(dbm)),
            TextField("Status", "status", "Status", DataDictType(dbm)),
            TextField("Datasender Name", "ds_name", "Datasender Name", DataDictType(dbm)),
            TextField("Datasender Id", "ds_id", "Datasender Id", DataDictType(dbm)),
            TextField("Entity Short Code", "entity_short_code", "Entity short code", DataDictType(dbm)),
            TextField("Error message", "error_msg", "Error Message", DataDictType(dbm))]


def _meta_fields(feed_submission_doc, submission_doc):
    search_dict = {}
    search_dict.update({"status": feed_submission_doc.status.capitalize()})
    search_dict.update({"date": format_datetime(submission_doc.created, "MMM. dd, yyyy, hh:mm a", locale="en")})
    search_dict.update({"ds_id": feed_submission_doc.data_sender.get('id')})
    search_dict.update({"ds_name": feed_submission_doc.data_sender.get('last_name')})
    search_dict.update({"error_msg": feed_submission_doc.error_message})
    return search_dict


def lookup_entity_name(dbm, id, entity_type):
    return get_by_short_code_include_voided(dbm, id, entity_type).value("name")

def _update_with_form_model_fields(dbm, submission_doc, search_dict, form_model):
    for key in submission_doc.values:
        field = submission_doc.values[key]
        entity_fields = [f for f in form_model.fields if f.is_entity_field and lower(f.code) == key]

        if entity_fields:
            id = field if submission_doc.status == 'error' else field.get("answer").get("id")
            value = field.get("answer").get("name")if isinstance(field, dict) else lookup_entity_name(dbm, id, form_model.entity_type)
            search_dict.update({"entity_short_code": id})
        else:
            value = field.get("answer") if isinstance(field, dict) else field

        if isinstance(value, dict):
            value = ','.join(value.values())
        search_dict.update({key: value})

    search_dict.update({'void': submission_doc.void})
    return search_dict