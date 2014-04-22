import logging

from datawinners.main.couchdb.utils import all_db_names
from datawinners.main.database import get_db_manager
from migration.couch.utils import migrate

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

def delete_questionnaires_without_projects(db_name):
    dbm = get_db_manager(db_name)
    logger = logging.getLogger(db_name)

    for row in dbm.database.query(list_all_formmodels_of_projects, include_docs=True):
        try:
            form_model_doc = row.doc
            projects = dbm.database.query(get_project_from_qid, include_docs=True, key=row.id)
            if not projects:
                submissions = dbm.database.query(get_submissions_for_formmodel,include_docs=True, key=form_model_doc['form_code'])
                for submission in submissions:
                    logger.info("deleting submission with id:%s", submission.id)
                    dbm.database.delete(submission.doc)
                logger.info("deleting form_model with id:%s and code:%s", row.id, form_model_doc['form_code'])
                dbm.database.delete(form_model_doc)
        except Exception as e:
            logger.error(
                'something failed for for database : %s, project_doc with id: %s' % (dbm.database_name, row.id))
            logger.error(e)

migrate(all_db_names(), delete_questionnaires_without_projects, version=(11, 0, 2), threads=3)