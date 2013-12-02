from string import lower
from babel.dates import format_datetime
import elasticutils
from datawinners.feeds.database import get_feed_db_from_main_db_name
from datawinners.settings import ELASTIC_SEARCH_URL
from mangrove.errors.MangroveException import DataObjectNotFound
from mangrove.datastore.documents import SurveyResponseDocument, EnrichedSurveyResponseDocument
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


def submission_update_on_edit_DS(entity_doc, dbm):
    if entity_doc.entity_type != ['reporter']:
        update_submission_search_for_subjects(entity_doc, dbm)
    else:
        entity_uid = entity_doc.id
        feeds_dbm = get_feed_db_from_main_db_name(dbm.database_name)
        survey_responses = dbm.load_all_rows_in_view('survey_response_by_datasender', key=entity_uid,
                                                     include_docs=False)
        for survey_response in survey_responses:
            enriched_survey_response = feeds_dbm._load_document(survey_response.id, EnrichedSurveyResponseDocument)
            if enriched_survey_response is not None:
                update_submission_search_index(enriched_survey_response, feeds_dbm, refresh_index=False)


def update_submission_search_for_subjects(entity_doc, dbm):
    entity_short_code = entity_doc.short_code
    entity_type = entity_doc.entity_type
    projects = dbm.load_all_rows_in_view('projects_by_subject_type', key=entity_type[0], include_docs=True)
    form_model_ids = []
    for project in projects:
        form_model_ids.append(project.doc['qid'])

    es = elasticutils.S().es(urls=ELASTIC_SEARCH_URL).indexes(dbm.database_name)
    feeds_dbm = get_feed_db_from_main_db_name(dbm.database_name)

    for id in form_model_ids:
        query = es.doctypes(id)
        query_all = query[:query.count()]
        filtered_query = query_all.filter(entity_short_code=entity_short_code)
        for survey_response in filtered_query.all():
            enriched_survey_response = feeds_dbm._load_document(survey_response._id, EnrichedSurveyResponseDocument)
            if enriched_survey_response is not None:
                update_submission_search_index(enriched_survey_response, feeds_dbm, refresh_index=False)


def update_submission_search_index(feed_submission_doc, feed_dbm, refresh_index=True):
    es = get_elasticsearch_handle()
    dbm = get_db_manager(feed_dbm.database_name.replace("feed_", ""))
    form_model = get_form_model_by_code(dbm, feed_submission_doc.form_code)
    submission_doc = SurveyResponseDocument.load(dbm.database, feed_submission_doc.id)
    search_dict = _meta_fields(feed_submission_doc, submission_doc, dbm)
    _update_with_form_model_fields(dbm, feed_submission_doc, search_dict, form_model)
    es.index(dbm.database_name, form_model.id, search_dict, id=feed_submission_doc.id, refresh=refresh_index)


def _metadata_mapping(dbm):
    return [DateField("Submission Date", "date", "Submission Date", 'submission_date_format', DataDictType(dbm)),
            TextField("Status", "status", "Status", DataDictType(dbm)),
            TextField("Datasender Name", "ds_name", "Datasender Name", DataDictType(dbm)),
            TextField("Datasender Id", "ds_id", "Datasender Id", DataDictType(dbm)),
            TextField("Entity Short Code", "entity_short_code", "Entity short code", DataDictType(dbm)),
            TextField("Error message", "error_msg", "Error Message", DataDictType(dbm))]


def _meta_fields(feed_submission_doc, submission_doc, dbm):
    search_dict = {}
    datasender_id = feed_submission_doc.data_sender.get('id')
    search_dict.update({"status": feed_submission_doc.status.capitalize()})
    search_dict.update({"date": format_datetime(submission_doc.submitted_on, "MMM. dd, yyyy, hh:mm a", locale="en")})
    search_dict.update({"ds_id": datasender_id or "NA"})
    search_dict.update({"ds_name": lookup_entity_name(dbm, datasender_id, ["reporter"])})
    search_dict.update({"error_msg": feed_submission_doc.error_message})
    return search_dict


def lookup_entity_name(dbm, id, entity_type):
    try:
        if id:
            return get_by_short_code_include_voided(dbm, id, entity_type).value("name")
    except DataObjectNotFound:
        pass
    return id or "NA"


def _update_with_form_model_fields(dbm, submission_doc, search_dict, form_model):
    for key in submission_doc.values:
        field = submission_doc.values[key]
        entity_fields = [f for f in form_model.fields if f.is_entity_field and lower(f.code) == key]

        if entity_fields:
            id = field if submission_doc.status == 'error' else field.get("answer").get("id")
            value = lookup_entity_name(dbm, id, form_model.entity_type)
            search_dict.update({"entity_short_code": id})
        else:
            value = field.get("answer") if isinstance(field, dict) else field

        if isinstance(value, dict):
            value = ','.join(value.values())
        search_dict.update({key: value})

    search_dict.update({'void': submission_doc.void})
    return search_dict