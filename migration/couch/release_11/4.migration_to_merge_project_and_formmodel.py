import logging
from datawinners.main.couchdb.utils import all_db_names
from datawinners.main.database import get_db_manager
from datawinners.project.models import Reminder, ReminderLog
from migration.couch.utils import migrate, mark_as_completed
from mangrove.form_model.form_model import FormModel

#This migration removes state in form model, copies over project details into form model and updates
# reminders to have form model ID rather than project id

list_all_projects = """
function(doc) {
    if (doc.document_type == 'Project') {
            emit(doc._id, null);
    }
}
"""


def update_reminders(dbm, project_data, logger):
    project_id = project_data.get('_id')
    for reminder in (Reminder.objects.filter(project_id=project_id)):
        try:
            form_model_id = project_data.get("qid")
            reminder.project_id = form_model_id
            reminder.save()
            rows = dbm.view.reminder_log(startkey=project_id, endkey=project_id, include_docs=True)
            for row in rows:
                doc = ReminderLog.__document_class__.wrap(row['doc'])
                doc.project_id = form_model_id
                dbm._save_document(doc)
        except Exception as e:
            logger.error("Reminder save failed for database %s for project id %s" % (dbm.database_name, project_id))
            logger.error(e)


def merge_project_and_form_model_for(dbm, logger):
    for row in dbm.database.query(list_all_projects, include_docs=True):
        try:
            project_data = row.doc
            form_model = FormModel.get(dbm, project_data.get("qid"))
            form_model_doc = form_model._doc

            form_model_doc['goals'] = project_data['goals']
            form_model_doc['name'] = project_data['name']
            form_model_doc['devices'] = project_data['devices']
            form_model_doc['data_senders'] = project_data['data_senders']
            form_model_doc['reminder_and_deadline'] = project_data['reminder_and_deadline']
            form_model_doc['sender_group'] = project_data['sender_group']
            try:
                del form_model_doc['state']
            except KeyError as e:
                logger.warn(e)
            dbm._save_document(form_model_doc)

            update_reminders(dbm, project_data, logger)
            logger.info("Deleting project with id: %s", row.id)
            dbm.database.delete(row.doc)
        except Exception as e:
            logger.error('Merging project and form_model failed for database : %s, project_doc with id: %s',
                          dbm.database_name, row.id)
            logger.error(e)


def migrate_to_merge_form_model_and_project(db_name):
    logger = logging.getLogger(db_name)
    try:
        logger.info('Starting migration')
        dbm = get_db_manager(db_name)
        merge_project_and_form_model_for(dbm, logger)
    except Exception as e:
        logger.exception(e.message)
    mark_as_completed(db_name)


migrate(all_db_names(), migrate_to_merge_form_model_and_project, version=(11, 0, 4), threads=3)