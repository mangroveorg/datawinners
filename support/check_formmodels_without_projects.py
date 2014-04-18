import logging

from datawinners.main.couchdb.utils import all_db_names
from datawinners.main.database import get_db_manager


logging.basicConfig(filename='/var/log/datawinners/migration_formmodels_without_projects.log', level=logging.DEBUG,
                    format="%(asctime)s | %(thread)d | %(levelname)s | %(name)s | %(message)s")

list_all_formmodels_of_projects = """
function(doc) {
    if (doc.document_type == 'FormModel' && !doc.is_registration_model && doc.form_code != 'delete') {
            emit(doc._id, null);
    }
}
"""
get_project_from_qid = """
function(doc) {
    if (doc.document_type == 'Project') {
            emit(doc.qid, null);
    }
}
"""

get_submissions_for_formmodel = """
function(doc) {
 if (doc.document_type == 'SurveyResponse') {
        emit(doc.form_code, doc);
    }
}
"""


def check_for_name_mismatch(dbm):
    for row in dbm.database.query(list_all_formmodels_of_projects, include_docs=True):
        try:
            form_model_doc = row.doc
            projects = dbm.database.query(get_project_from_qid, include_docs=True, key=row.id)
            if not projects:
                submissions = dbm.database.query(get_submissions_for_formmodel, key=form_model_doc['form_code'])
                logging.debug(
                    "project not found for database %s, form model with_id %s and code: %s, submission_count:%s" % (
                        dbm.database_name, form_model_doc['form_code'], row.id, len(submissions)))
        except Exception as e:
            logging.error(
                'something failed for for database : %s, project_doc with id: %s' % (dbm.database_name, row.id))
            logging.error(e)


def check_project_and_formmodel_name_mismatch(db_name):
    try:
        logging.info('Starting checking for database %s' % db_name)
        dbm = get_db_manager(db_name)
        check_for_name_mismatch(dbm)
    except Exception as e:
        logging.exception(e.message)


for db_name in all_db_names():
    check_project_and_formmodel_name_mismatch(db_name)