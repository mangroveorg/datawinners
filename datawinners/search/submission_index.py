from babel.dates import format_datetime
import elasticutils
from datawinners.main.database import get_db_manager
from datawinners.search.index_utils import get_fields_mapping
from datawinners.settings import ELASTIC_SEARCH_URL
from mangrove.datastore.datadict import DataDictType
from mangrove.form_model.field import TextField, DateField
from mangrove.form_model.form_model import get_form_model_by_code


def create_submission_mapping(dbm, form_model):
    es = elasticutils.get_es(urls=ELASTIC_SEARCH_URL)
    fields = _metadata_mapping(dbm)
    fields.extend(form_model.fields)
    mapping = get_fields_mapping(form_model.id, fields, 'code')
    es.put_mapping(dbm.database_name, form_model.id, mapping)


def update_submission_search_index(submission_doc, feed_dbm):
    es = elasticutils.get_es(urls=ELASTIC_SEARCH_URL)
    dbm = get_db_manager(feed_dbm.database_name.replace("feed_",""))
    form_model = get_form_model_by_code(dbm, submission_doc.form_code)
    search_dict = _meta_fields(submission_doc)
    _update_with_form_model_fields(submission_doc,search_dict)
    es.index(dbm.database_name, form_model.id, search_dict, id=submission_doc.id)


def _metadata_mapping(dbm):
    return [DateField("Submission Date", "date", "Submission Date", 'submission_date_format', DataDictType(dbm)),
            TextField("Status", "status", "Status", DataDictType(dbm)),
            TextField("Datasender Name", "ds_name", "Datasender Name", DataDictType(dbm)),
            TextField("Datasender Id", "ds_id", "Datasender Id", DataDictType(dbm)),
            TextField("Error message", "error_msg", "Error Message", DataDictType(dbm))]

def _meta_fields(submission_doc):
    search_dict = {}
    search_dict.update({"status": submission_doc.status})
    search_dict.update(
        {"date": format_datetime(submission_doc.survey_response_modified_time, "MMM. dd, yyyy, hh:mm a", locale="en")})
    search_dict.update({"ds_id": submission_doc.data_sender.get('id')})
    search_dict.update({"ds_name": submission_doc.data_sender.get('last_name')})
    search_dict.update({"error_msg": submission_doc.error_message})
    return search_dict

def _update_with_form_model_fields(submission_doc,search_dict):
    for key in submission_doc.values:
        field = submission_doc.values[key]
        value = field if submission_doc.status == 'error' else field.get("answer")
        if (isinstance(value, dict)):
            value = value.get("name") if field.get("is_entity_question") else ','.join(value.values())
        search_dict.update({key: value})
    return search_dict