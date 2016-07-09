from datawinners.main.couchdb.utils import all_db_names
from migration.couch.utils import migrate, mark_as_completed
from datawinners.main.database import get_db_manager
from mangrove.datastore.documents import FormModelDocument

map_all_adv_qre = """function(doc) {
    if (doc.document_type == 'FormModel' && !doc.is_registration_model && doc.form_code != 'delete') {
        if (!doc.void && doc.xform  && Object.keys(doc.snapshots).length) {
            emit([doc.created,doc.name], doc);
        }
    }
}"""


def delete_snapshot_for_db(database_name):
    dbm = get_db_manager(database_name)
    advanced_qre = dbm.database.query(map_all_adv_qre, include_docs=True)

    for row in advanced_qre:
        doc = FormModelDocument.wrap(row.doc)
        doc.snapshots = {}
        doc.store(dbm.database)

    mark_as_completed(database_name)


migrate(all_db_names, delete_snapshot_for_db, version=(31, 3, 1), threads=5)
