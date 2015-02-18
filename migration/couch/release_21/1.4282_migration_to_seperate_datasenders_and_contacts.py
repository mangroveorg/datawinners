import sys

from datawinners.main.couchdb.utils import all_db_names


if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, ".")

import logging
from datawinners.main.database import get_db_manager
from migration.couch.utils import migrate, mark_as_completed


datasender_document = """
function(doc) {
    if (doc.document_type == "Entity" && doc.aggregation_paths['_type'] == "reporter") {
        emit(doc.short_code, doc);
    }
}"""


def seperate_datasender_and_contact_document(db_name):
    logger = logging.getLogger(db_name)
    logger.info('Starting Migration')

    manager = get_db_manager(db_name)
    for row in manager.database.query(datasender_document):
        try:
            row['value']['document_type'] = 'Contact'
            manager.database.save(row['value'], process_post_update=False)
        except Exception as e:
            logger.error("Failed to update document with id:%s" % row['value']['_id'])
    logger.info('Completed Migration')
    mark_as_completed(db_name)


migrate(all_db_names(), seperate_datasender_and_contact_document, version=(21, 0, 1), threads=3)
