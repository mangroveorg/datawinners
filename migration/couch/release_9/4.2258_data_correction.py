import logging
import traceback
import sys

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, ".")

from datawinners.main.database import get_db_manager
from datawinners.main.couchdb.utils import all_db_names
from datawinners.project.models import Project
from migration.couch.utils import mark_start_of_migration, migrate


def is_void(d, ds):
    rows = d.view("entity_by_short_code/entity_by_short_code", key=[["reporter"], ds], include_docs=True)
    return rows.rows[0]["doc"]["void"]


def get_all_active_data_senders(dbm):
    return [row.key[1] for row in
            dbm.view.by_short_codes(reduce=False, start_key=[["reporter"]], end_key=[["reporter"], {}])]


def remove_deleted_ds_from_project(db_name):
    logger = logging.getLogger(db_name)
    try:
        dbm = get_db_manager(db_name)
        logger.info("starting data fix for " + db_name)
        all_data_senders = set(get_all_active_data_senders(dbm))
        for project_doc in dbm.database.view("project_names/project_names", include_docs=True):
            try:
                project_data_senders = set(project_doc["doc"]["data_senders"])

                invalid_ds = project_data_senders.difference(all_data_senders)

                project_doc = Project._wrap_row(project_doc)
                for ds in invalid_ds:
                    logger.info("Found invalid data senders in project : " + str(project_doc) + " " + str(invalid_ds))
                    project_doc.delete_datasender(dbm, ds)

            except Exception as e:
                print "Error : " + db_name + " : " + str(project_doc) + e.message
                traceback.print_exc(file=sys.stdout)
        logger.info("done:" + db_name)
        mark_start_of_migration(db_name)
    except Exception as e :
        logger.exception("Failed Database : %s , with error :%s " % (db_name, e.message))

migrate(all_db_names(), remove_deleted_ds_from_project, version=(9, 0, 4))