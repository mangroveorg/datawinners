import sys
from datawinners.main.database import get_db_manager
from datawinners.search.index_utils import get_elasticsearch_handle, subject_dict
from datawinners.search.subject_index import create_subject_mapping, entity_search_update
from mangrove.datastore.entity import get_all_entities
from mangrove.form_model.form_model import FormModel

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, ".")
from datawinners.main.couchdb.utils import all_db_names

import logging
from migration.couch.utils import migrate, mark_start_of_migration

map_form_model_for_subjects = """
function(doc) {
   if (doc.document_type == 'FormModel' && doc.is_registration_model == true && doc.form_code != 'reg') {
               emit(doc._id, null);
   }
}
"""


def recreate_subject_index(db_name):
    logger = logging.getLogger(db_name)
    try:
        mark_start_of_migration(db_name)
        logger.info('Starting indexing')
        dbm = get_db_manager(db_name)
        form_models = dbm.database.query(map_form_model_for_subjects)
        for row in form_models:
            form_model = FormModel.get(dbm, row.id)
            create_subject_mapping(dbm, form_model)
            entity_docs = []
            for entity_doc in get_all_entities(dbm, form_model.entity_type):
                if entity_doc.data:
                    subject = subject_dict(form_model.entity_type, entity_doc, dbm, form_model)
                    subject.update({'id': entity_doc.id})
                    entity_docs.append(subject)

            es = get_elasticsearch_handle()
            es.bulk_index(dbm.database_name, form_model.entity_type, entity_docs)
            es.refresh(dbm.database_name)
                #entity_search_update(subject, db_name)

            logger.info('Changed index for subject with codes '+str([a.get('id') for a in entity_docs]))
        logger.info('Completed Indexing')
    except Exception as e:
        logger.exception(e.message)


es = get_elasticsearch_handle()
migrate(all_db_names(), recreate_subject_index, version=(10, 0, 4), threads=1)