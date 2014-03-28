import logging
from datawinners.main.couchdb.utils import all_db_names
from datawinners.main.database import get_db_manager
from mangrove.errors.MangroveException import DataObjectAlreadyExists
from mangrove.form_model.field import ShortCodeField
from migration.couch.utils import migrate, mark_as_completed
from mangrove.datastore.documents import FormModelDocument
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
            if document_data.get('is_registration_model'):
                for f in document_data.get('json_fields'):
                    if f.get('name')=='short_code':
                        short_code_field = ShortCodeField(f.name,f.code,f.label,f.constraints,f.defaultValue,f.instruction,f.required)
                        break

            form_model = FormModel.new_from_doc(dbm, (FormModelDocument.wrap(document_data)))
            if form_model.is_entity_registration_form():
                for f in form_model.fields:
                    if f.name == SHORT_CODE_FIELD:
                        short_code_field = ShortCodeField(f.name,f.code,f.label,f.constraints,f.defaultValue,f.instruction,f.required)
                        form_model.fields.append(short_code_field)
                        form_model.fields.remove(f)
                        break
            form_model.save()
        except DataObjectAlreadyExists as d:
            form_model.create_snapshot()
            json_snapshots = {}
            for key, value in form_model._snapshots.items():
                json_snapshots[key] = [each._to_json() for each in value]
            form_model._doc.snapshots = json_snapshots
            dbm._save_document(form_model._doc, process_post_update=False)
        except Exception as e:
            logging.error('Removing state in form model failed for database : %s, doc with id: %s', dbm.database_name, row.id)
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


migrate(all_db_names(), migrate_form_model_to_add_eid_fields, version=(11, 0, 4))