import sys
from datawinners.main.database import get_db_manager
from datawinners.search.index_utils import get_elasticsearch_handle
from datawinners.search.subject_index import create_subject_mapping, entity_search_update
from mangrove.datastore.entity import get_all_entities
from mangrove.errors.MangroveException import FormModelDoesNotExistsException

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, ".")
from datawinners.main.couchdb.utils import all_db_names
from datawinners.search.datasender_index import create_datasender_index

import logging
from migration.couch.utils import migrate, mark_start_of_migration

map_form_model_for_subjects = """
function(doc) {
   if (doc.document_type == 'form_model' && doc.is_registration_model == 'true') {
               emit( doc.form_code, null);
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
        for form_model in form_models:
            if form_model.is_global_registration_form():
                continue
            create_subject_mapping(dbm, form_model)
            for subject in get_all_entities(dbm, form_model.entity_type):
                entity_search_update(subject, db_name)
                logger.info('Changed index for subject with code '+subject.short_code)
        logger.info('Completed Indexing')
    except Exception as e:
        logger.exception(e.message)


es = get_elasticsearch_handle()
migrate(all_db_names(), recreate_subject_index, version=(10, 0, 4), threads=1)
