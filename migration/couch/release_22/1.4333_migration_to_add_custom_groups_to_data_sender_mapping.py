import sys

from datawinners.main.couchdb.utils import all_db_names
from datawinners.search.index_utils import get_elasticsearch_handle, get_fields_mapping
from mangrove.form_model.field import TextField


if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, ".")

import logging
from migration.couch.utils import migrate, mark_as_completed


datasender_document = """
function(doc) {
    if (doc.document_type == "Entity" && doc.aggregation_paths['_type'] == "reporter") {
        emit(doc.short_code, doc);
    }
}"""


def add_custom_group_field_to_data_sender_mapping(db_name):
    logger = logging.getLogger(db_name)
    logger.info('Starting Migration')

    es = get_elasticsearch_handle()
    fields = [TextField(name="customgroups", code='customgroups', label='Custom groups')]
    es.put_mapping(db_name, 'reporter', get_fields_mapping('reg', fields))

    logger.info('Completed Migration')
    mark_as_completed(db_name)


migrate(all_db_names(), add_custom_group_field_to_data_sender_mapping, version=(22, 0, 1), threads=3)
