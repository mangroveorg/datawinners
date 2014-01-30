import sys
#from datawinners.main.database import get_db_manager
from mangrove.datastore.database import get_db_manager
from datawinners.search.index_utils import get_elasticsearch_handle, subject_dict
from datawinners.search.subject_index import create_subject_mapping
from mangrove.datastore.entity import get_all_entities_include_voided
from mangrove.form_model.form_model import FormModel

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, ".")
from datawinners.main.couchdb.utils import all_db_names

import logging
from migration.couch.utils import migrate, mark_as_completed

map_form_model_for_subjects = """
function(doc) {
   if (doc.document_type == 'FormModel' && doc.is_registration_model == true && doc.form_code != 'reg') {
               emit(doc._id, null);
   }
}
"""

# ~10min
def recreate_subject_index(db_name):
    logger = logging.getLogger(db_name)
    try:
        logger.info('Starting indexing')
        dbm = get_db_manager(db_name)
        form_models = dbm.database.query(map_form_model_for_subjects)
        es = get_elasticsearch_handle()
        for row in form_models:
            try:
                form_model = FormModel.get(dbm, row.id)
                entity_type = form_model.entity_type[0]
                try:
                    es.delete_all(db_name, entity_type)
                except Exception as ignore:
                    pass
                create_subject_mapping(dbm, form_model)
                entity_docs = []
                for entity_doc in get_all_entities_include_voided(dbm, [entity_type]):
                    try:
                        if entity_doc.data:
                            subject = subject_dict(entity_type, entity_doc, dbm, form_model)
                            subject.update({'id': entity_doc.id})
                            entity_docs.append(subject)
                    except Exception as e:
                        logger.error("Failed to index subject with id %s" % entity_doc.id)
                        logger.error(e.message)

                if entity_docs:
                    es.bulk_index(dbm.database_name, entity_type, entity_docs)
                    es.refresh(dbm.database_name)
                    logger.info('Changed index for subject with codes ' + str([a.get('id') for a in entity_docs]))
            except Exception as e:
                logger.error("Failed to create subject mapping for %s" % row.id)
                logger.error(e.message)

        logger.info('Completed Indexing')
        mark_as_completed(db_name)
    except Exception as e:
        logger.exception(e.message)


es = get_elasticsearch_handle()
migrate(all_db_names(), recreate_subject_index, version=(10, 0, 3), threads=1)
