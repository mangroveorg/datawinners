import logging
from datawinners.main.couchdb.utils import all_db_names
from datawinners.main.database import get_db_manager
from datawinners.project.models import Project
from migration.couch.utils import migrate, mark_as_completed
from mangrove.datastore.documents import ProjectDocument
from mangrove.form_model.form_model import FormModel


list_all_projects = """
function(doc) {
    if (doc.document_type == 'Project') {
            emit(doc._id, null);
    }
}
"""


def merge_project_and_form_model_for(dbm):
    for row in dbm.database.query(list_all_projects, include_docs=True):
        try:
            document_data = row.doc
            form_model = FormModel.get(dbm,document_data.get("qid"))
            form_model_doc = form_model._doc

            del form_model_doc['entity_type']

            form_model_doc['goals'] = document_data['goals']
            form_model_doc['name'] = document_data['name']
            form_model_doc['devices'] = document_data['devices']
            form_model_doc['data_senders'] = document_data['data_senders']
            form_model_doc['reminder_and_deadline'] = document_data['reminder_and_deadline']
            form_model_doc['sender_group'] = document_data['sender_group']
            # form_model_doc.pop('state')
            questionnaire = Project.new_from_doc(dbm, (ProjectDocument.wrap(form_model_doc)))
            super(Project, questionnaire).save()
            dbm.database.delete(row.doc)
        except Exception as e:
            logging.error('Merging project and form_model failed for database : %s, project_doc with id: %s', dbm.database_name, row.id)
            logging.error(e)


def migrate_to_merge_form_model_and_project(db_name):
    logger = logging.getLogger(db_name)
    try:
        logger.info('Starting migration')
        dbm = get_db_manager(db_name)
        merge_project_and_form_model_for(dbm)
        mark_as_completed(db_name)
    except Exception as e:
        logger.exception(e.message)


migrate(all_db_names(), migrate_to_merge_form_model_and_project, version=(11, 0, 4))