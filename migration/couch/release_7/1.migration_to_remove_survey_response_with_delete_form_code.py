import logging
from mangrove.datastore.documents import SurveyResponseDocument
from datawinners.main.database import get_db_manager
from migration.couch.utils import DWThreadPool, should_not_skip, all_db_names, init_migrations
from mangrove.transport.contract.survey_response import SurveyResponse


NUMBER_OF_THREADS = 7

init_migrations('/var/log/datawinners/dbs_migrated_release_7_0_1.csv')
logging.basicConfig(filename='/var/log/datawinners/migration_release_7_0_1.log', level=logging.DEBUG,
                    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")

survey_responses_with_delete_form_code = """
function(doc) {
    if (doc.document_type == "SurveyResponse" && doc.form_code == 'delete') {
        emit(doc._id, doc);
    }
}"""


def migrate(db_name):
    logger = logging.getLogger(db_name)
    logger.info('Starting Migration %s' % db_name)

    manager = get_db_manager(db_name)
    for row in manager.database.query(survey_responses_with_delete_form_code):
        try:
            doc = SurveyResponseDocument.wrap(row['value'])
            survey_response = SurveyResponse.new_from_doc(manager, doc)
            logger.info("Database: %s : survey response id: %s" % (db_name, survey_response.id))
            survey_response.delete()
            logger.info("Database: %s : Deleted survey response id: %s" % (db_name, survey_response.id))
        except Exception as e:
            logger.exception("FAILED:%s " % db_name)
    logger.info('Completed Migration %s' % db_name)


def migrate_survey_response_with_form_code_as_delete(all_db_names):
    pool = DWThreadPool(NUMBER_OF_THREADS, NUMBER_OF_THREADS)
    for db_name in all_db_names:
        if should_not_skip(db_name):
            pool.submit(migrate, db_name)

    pool.wait_for_completion()
    print "Completed!"


migrate_survey_response_with_form_code_as_delete(all_db_names())
