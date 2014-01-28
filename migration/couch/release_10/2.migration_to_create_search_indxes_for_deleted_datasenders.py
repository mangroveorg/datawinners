import sys
from datawinners.search.datasender_index import _create_datasender_dict
from mangrove.form_model.form_model import get_form_model_by_code, REGISTRATION_FORM_CODE, REPORTER
from mangrove.transport.repository.reporters import REPORTER_ENTITY_TYPE


if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, ".")

from mangrove.datastore.entity import get_all_entities_include_voided
from mangrove.errors.MangroveException import FormModelDoesNotExistsException

from datawinners.main.database import get_db_manager
from datawinners.search.index_utils import get_elasticsearch_handle

from datawinners.main.couchdb.utils import all_db_names

import logging
from migration.couch.utils import migrate, mark_as_completed as mark_as_successful


def create_search_indices_for_deleted_datasender(db_name):
    logger = logging.getLogger(db_name)
    try:
        logger.info('Starting indexing')
        dbm = get_db_manager(db_name)
        es = get_elasticsearch_handle()
        form_model = get_form_model_by_code(dbm, REGISTRATION_FORM_CODE)
        datasenders = []

        for entity in get_all_entities_include_voided(dbm, REPORTER_ENTITY_TYPE):
            if not entity.data:
                continue
            if entity.is_void() or entity.short_code == 'test':
                datasender_dict = _create_datasender_dict(dbm, entity, REPORTER, form_model)
                datasender_dict.update({'id': entity.id})
                datasenders.append(datasender_dict)
        if datasenders:
            es.bulk_index(dbm.database_name, REPORTER, datasenders)
            logger.info('Created index for datasenders with ids :'+str([a.get('id') for a in datasenders]))
        logger.info('Completed Indexing')
        mark_as_successful(db_name)
    except Exception as e:
        logger.exception(e.message)


es = get_elasticsearch_handle()
migrate(all_db_names(), create_search_indices_for_deleted_datasender, version=(10, 0, 2), threads=1)
