import logging
from mangrove.form_model.validators import UniqueIdExistsValidator
from datawinners.main.couchdb.utils import all_db_names
from datawinners.main.database import get_db_manager
from mangrove.form_model.field import ShortCodeField, UniqueIdField
from migration.couch.utils import migrate, mark_as_completed
from mangrove.datastore.documents import FormModelDocument, SurveyResponseDocument
from mangrove.form_model.form_model import FormModel
from mangrove.form_model.form_model import SHORT_CODE_FIELD

#This migration creates a ShortCodeField for entity registrations and UniqueIdField for individual projects.It removes the on behalf of
# question from the summary form models and the corresponding answer from its survey responses. This migration also removes 'test' field
# from survey response which was to indicate if the project was active or in test mode

list_all_form_models = """
function(doc) {
    if (doc.document_type == 'FormModel') {
            emit(doc._id, null);
    }
}
"""


def _save_form_model_doc(dbm, form_model):
    form_model._doc.json_fields = [f._to_json() for f in form_model._form_fields]
    form_model._doc.validators = [validator.to_json() for validator in form_model.validators]
    form_model.create_snapshot()
    json_snapshots = {}
    for key, value in form_model._snapshots.items():
        json_snapshots[key] = [each._to_json() for each in value]
    form_model._doc.snapshots = json_snapshots
    form_model._delete_form_model_from_cache()
    dbm._save_document(form_model._doc)


def add_unique_id_and_short_code_field(dbm, logger):
    for row in dbm.database.query(list_all_form_models, include_docs=True):
        try:
            document_data = row.doc
            json_data = document_data.get('json_fields')
            validator = None
            short_code_field = None
            short_code_dict = None
            index = 0
            if document_data.get('is_registration_model') or document_data.get("form_code") == "delete":
                for index, f in enumerate(json_data):
                    if f.get('name') == SHORT_CODE_FIELD:
                        short_code_field = ShortCodeField(f.get('name'), f.get('code'), f.get('label'),
                                                          defaultValue=f.get('defaultValue'),
                                                          instruction=f.get('instruction'), required=f.get('required'))
                        short_code_dict = f
                        break
            else:
                for index, f in enumerate(json_data):
                    if f.get('entity_question_flag'):
                        start_key = [document_data.get('form_code')]
                        end_key = [document_data.get('form_code'), {}]
                        survey_response_rows = dbm.database.iterview("surveyresponse/surveyresponse", 1000, reduce=False, include_docs=False, startkey=start_key, endkey=end_key)

                        if document_data.get('entity_type') != ['reporter']:
                            short_code_field = UniqueIdField(document_data.get('entity_type')[0], f.get('name'),
                                                             f.get('code'),
                                                             f.get('label'), defaultValue=f.get('defaultValue'),
                                                             instruction=f.get('instruction'),
                                                             required=f.get('required'))
                            validator = UniqueIdExistsValidator
                            #Remove test field from survey responses
                            for row in survey_response_rows:
                                if row.get('value').get('test'):
                                    row.get('value').pop('test')
                        else:
                            for row in survey_response_rows:
                                try:
                                    row.get('value').get('values').pop(f.get('code'))
                                    if row.get('value').get('test'):
                                        row.get('value').pop('test')
                                    survey_response = SurveyResponseDocument._wrap_row(row)
                                    dbm._save_document(survey_response)
                                except Exception as e:
                                    logger.error("Survey response update failed for database %s for id %s" %(dbm.database_name,row.get('id')))
                                    logger.error(e)
                        short_code_dict = f
                        break
                    #Remove event_time flag from reporting date question
                    elif f.get('type') == 'date' and 'event_time_field_flag' in f:
                        f.pop('event_time_field_flag')
                #Remove entity type from questionnaire form models.
                if document_data.get('entity_type'):
                    document_data.pop('entity_type')
            if short_code_dict:
                json_data.remove(short_code_dict)
                form_model = FormModel.new_from_doc(dbm, (FormModelDocument.wrap(document_data)))
                if short_code_field:
                    form_model._form_fields.insert(index, short_code_field)
                if validator:
                    form_model.add_validator(validator)
                _save_form_model_doc(dbm, form_model)
        except Exception as e:
            logger.error('Failed form model for database : %s, doc with id: %s', dbm.database_name,
                          row.id)
            logger.error(e)


def migrate_form_model_to_add_eid_fields(db_name):
    logger = logging.getLogger(db_name)
    try:
        logger.info('Starting migration')
        dbm = get_db_manager(db_name)
        add_unique_id_and_short_code_field(dbm, logger)
    except Exception as e:
        logger.exception(e.message)
    mark_as_completed(db_name)


migrate(all_db_names(), migrate_form_model_to_add_eid_fields, version=(11, 0, 3), threads=3)