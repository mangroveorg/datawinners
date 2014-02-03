import sys
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, ".")

from datawinners.main.couchdb.utils import all_db_names
from mangrove.form_model.form_model import FormModel
from mangrove.form_model.validation import ShortCodeRegexConstraint, TextLengthConstraint


import logging
from mangrove.datastore.documents import FormModelDocument
from datawinners.main.database import get_db_manager
from migration.couch.utils import migrate, mark_as_completed

map_subject_form_model = """
function(doc) {
   if (doc.document_type == 'FormModel' && doc.form_code != 'reg'
       && doc.form_code != 'delete' && doc.is_registration_model == true
       && !doc.void) {
            emit(doc.form_code,doc)
   }
}"""


def add_regex_constraint_to_short_code(form_model, logger):
    form_model.entity_question.set_constraints(
        [TextLengthConstraint(max=20)._to_json(), ShortCodeRegexConstraint("^[a-zA-Z0-9]+$")._to_json()])
    form_model.save()
    logger.info("migrated form code: %s" % form_model.form_code)


def migrate_subject_form_code_to_add_regex_validator_in_short_code(db_name):
    logger = logging.getLogger(db_name)
    logger.info('Starting Migration')
    mark_as_completed(db_name)

    manager = get_db_manager(db_name)
    for row in manager.database.query(map_subject_form_model):
        try:
            doc = FormModelDocument.wrap(row['value'])
            form_model = FormModel.new_from_doc(manager, doc)
            add_regex_constraint_to_short_code(form_model, logger)
        except Exception as e:
            logger.exception("FAILED to migrate:%s " % row['value']['_id'])
    logger.info('Completed Migration')


migrate(all_db_names(), migrate_subject_form_code_to_add_regex_validator_in_short_code, version=(8, 1, 0))