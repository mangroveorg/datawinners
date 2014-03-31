import logging
from mangrove.form_model.validators import UniqueIdExistsValidator
from datawinners.main.couchdb.utils import all_db_names
from datawinners.main.database import get_db_manager
from mangrove.errors.MangroveException import DataObjectAlreadyExists
from mangrove.form_model.field import ShortCodeField, UniqueIdField
from migration.couch.utils import migrate, mark_as_completed
from mangrove.datastore.documents import FormModelDocument, SurveyResponseDocument
from mangrove.form_model.form_model import FormModel
from mangrove.form_model.form_model import SHORT_CODE_FIELD


list_all_form_models = """
function(doc) {
    if (doc.document_type == 'FormModel') {
            emit(doc._id, null);
    }
}
"""


def add_unique_id_and_short_code_field(dbm):
    for row in dbm.database.query(list_all_form_models, include_docs=True):
        try:
            document_data = row.doc
            json_data = document_data.get('json_fields')
            validator = None
            short_code_field = None
            if document_data.get('is_registration_model'):
                for f in json_data:
                    if f.get('name') == 'short_code':
                        short_code_field = ShortCodeField(f.get('name'), f.get('code'), f.get('label'),
                                                          defaultValue=f.get('defaultValue'),
                                                          instruction=f.get('instruction'), required=f.get('required'))
                        short_code_dict = f
                        break
            else:
                for f in json_data:
                    if f.get('entity_question_flag'):
                        if document_data.get('entity_type') != ['reporter']:
                            short_code_field = UniqueIdField(document_data.get('entity_type')[0], f.get('name'),
                                                             f.get('code'),
                                                             f.get('label'), defaultValue=f.get('defaultValue'),
                                                             instruction=f.get('instruction'),
                                                             required=f.get('required'))
                            validator = UniqueIdExistsValidator
                        else:
                            start_key = [document_data.get('form_code')]
                            end_key = [document_data.get('form_code'), {}]
                            survey_response_rows = dbm.database.iterview("surveyresponse/surveyresponse", 1000, reduce=False, include_docs=False, startkey=start_key, endkey=end_key)
                            for row in survey_response_rows:
                                row.get('value').get('values').pop(f.get('code'))
                                survey_response = SurveyResponseDocument._wrap_row(row)
                                dbm._save_document(survey_response)
                        short_code_dict = f
                        break

            json_data.remove(short_code_dict)
            form_model = FormModel.new_from_doc(dbm, (FormModelDocument.wrap(document_data)))
            if short_code_field:
                form_model.add_field(short_code_field)
            if validator:
                form_model.add_validator(validator)
            form_model.save()

        except DataObjectAlreadyExists as d:
            form_model.create_snapshot()
            json_snapshots = {}
            for key, value in form_model._snapshots.items():
                json_snapshots[key] = [each._to_json() for each in value]
            form_model._doc.snapshots = json_snapshots
            dbm._save_document(form_model._doc, process_post_update=False)
        except Exception as e:
            logging.error('Removing state in form model failed for database : %s, doc with id: %s', dbm.database_name,
                          row.id)
            logging.error(e)


def migrate_form_model_to_add_eid_fields(db_name):
    logger = logging.getLogger(db_name)
    try:
        logger.info('Starting migration')
        dbm = get_db_manager(db_name)
        add_unique_id_and_short_code_field(dbm)
        mark_as_completed(db_name)
    except Exception as e:
        logger.exception(e.message)


migrate(all_db_names(), migrate_form_model_to_add_eid_fields, version=(11, 0, 3))