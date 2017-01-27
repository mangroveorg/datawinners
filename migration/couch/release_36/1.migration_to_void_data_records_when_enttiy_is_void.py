from datawinners.main.couchdb.utils import db_names_with_custom_apps
from datawinners.main.database import get_db_manager
from mangrove.datastore.documents import EntityDocument
from mangrove.datastore.entity import Entity
from migration.couch.utils import migrate


def void_data_records(database_name):
    dbm = get_db_manager(database_name)
    entities = dbm.load_all_rows_in_view('entity_by_short_code', include_docs=True)
    for entity in entities:
        if entity['doc']['document_type'] == 'Entity':
            entity = Entity.new_from_doc(dbm, EntityDocument.wrap(entity['doc']))
            if entity.is_void():
                data_records = dbm.load_all_rows_in_view('entity_data', key=entity.id)
                for record in data_records:
                    dbm.invalidate(record.id)


migrate(db_names_with_custom_apps(), void_data_records, version=(36, 0, 1))