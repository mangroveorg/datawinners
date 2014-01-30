import re
from datawinners.search import register_postsave_handlers
from datawinners.main.database import get_db_manager
from mangrove.datastore.entity import get_all_entities
from datawinners.main.couchdb.utils import all_db_names
from datawinners.entity.import_data import get_entity_types
import logging
from migration.couch.utils import migrate, mark_as_completed


def migration_to_convert_subject_ids_to_lowercase(db_name):
    try:
        logger = logging.getLogger(db_name)
        dbm = get_db_manager(db_name)
        entity_types = get_entity_types(dbm)
        for entity_type in entity_types:
            all_entities = get_all_entities(dbm, [entity_type])
            try:
                for entity in all_entities:
                    if 'short_code' in entity.data.keys():
                        short_code = entity.data['short_code']['value']
                        if re.search('[A-Z]', short_code):
                            entity.data['short_code']['value'] = short_code.lower()
                            entity.save()
                            logger.info('Migrated short_code:%s' % short_code)
            except Exception as e:
                logger.exception(e)
        logger.info('Completed Migration')
        mark_as_completed(db_name)
    except Exception as e:
        logger.exception(e)

register_postsave_handlers()

migrate(all_db_names(), migration_to_convert_subject_ids_to_lowercase, version=(10, 0, 4), threads=4)