import sys

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, ".")

import logging
from mangrove.datastore.documents import SurveyResponseDocument
from datawinners.main.database import get_db_manager
from migration.couch.utils import all_db_names, migrate
from mangrove.transport.contract.survey_response import SurveyResponse


survey_responses_with_delete_form_code = """
function(doc) {
    if (doc.document_type == "SurveyResponse" && doc.form_code == 'delete') {
        emit(doc._id, doc);
    }
}"""


def migrate_survey_response_with_form_code_as_delete(db_name):
    logger = logging.getLogger(db_name)
    logger.info('Starting Migration')

    manager = get_db_manager(db_name)
    for row in manager.database.query(survey_responses_with_delete_form_code):
        try:
            doc = SurveyResponseDocument.wrap(row['value'])
            survey_response = SurveyResponse.new_from_doc(manager, doc)
            logger.info("survey response id: %s" % survey_response.id)
            survey_response.delete()
            logger.info("Deleted survey response id: %s" % survey_response.id)
        except Exception as e:
            logger.exception("FAILED to delete:%s " % row['value']['_id'])
    logger.info('Completed Migration')


migrate(all_db_names(), migrate_survey_response_with_form_code_as_delete, version=(7, 0, 1))

