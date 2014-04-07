import logging

from mangrove.form_model.form_model import FormModel

from datawinners.main.couchdb.utils import all_db_names
from datawinners.main.database import get_db_manager


logging.basicConfig(filename='/var/log/datawinners/migration_check_name_mismatch.log', level=logging.DEBUG,
                        format="%(asctime)s | %(thread)d | %(levelname)s | %(name)s | %(message)s")


list_all_projects = """
function(doc) {
    if (doc.document_type == 'Project') {
            emit(doc._id, null);
    }
}
"""


def check_for_name_mismatch(dbm):
    for row in dbm.database.query(list_all_projects, include_docs=True):
        try:
            project_data = row.doc
            form_model = FormModel.get(dbm, project_data.get("qid"))
            form_model_doc = form_model._doc

            if form_model_doc['name'] != project_data['name']:
                logging.debug("name mismatch for database %s, project with_id %s" %(dbm.database_name, row.id))
        except Exception as e:
            logging.error('something failed for for database : %s, project_doc with id: %s' %(dbm.database_name, row.id))
            logging.error(e)


def check_project_and_formmodel_name_mismatch(db_name):
    try:
        logging.info('Starting checking for database %s' %db_name)
        dbm = get_db_manager(db_name)
        check_for_name_mismatch(dbm)
    except Exception as e:
        logging.exception(e.message)

for db_name in all_db_names():
    check_project_and_formmodel_name_mismatch(db_name)