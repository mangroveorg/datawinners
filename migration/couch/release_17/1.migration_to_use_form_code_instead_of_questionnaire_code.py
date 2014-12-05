import logging

from datawinners.feeds.database import get_feed_db_from_main_db_name
from datawinners.main.couchdb.utils import all_db_names
from datawinners.main.database import get_db_manager
from mangrove.datastore.documents import EnrichedSurveyResponseDocument
from migration.couch.utils import migrate, mark_as_completed

def make_feed_document_use_form_code_instead_of_form_model_id(db_name):
    dbm = get_db_manager(db_name)
    logger = logging.getLogger(db_name)
    feed_dbm = get_feed_db_from_main_db_name(db_name)
    questionnaires = dbm.load_all_rows_in_view('all_projects')
    for questionnaire in questionnaires:
        try:
            feeds = feed_dbm.database.iterview("questionnaire_feed/questionnaire_feed", 1000, startkey=[questionnaire.id], endkey=[questionnaire.id,{}], include_docs=True)
            for feed in feeds:
                try:
                    enriched_survey_response = EnrichedSurveyResponseDocument.wrap(feed.doc)
                    enriched_survey_response.form_code = questionnaire['value']['form_code']
                    feed_dbm._save_document(enriched_survey_response, modified=enriched_survey_response.modified)
                except Exception as e:
                    logger.exception("failed for feed:"+feed.id)
        except Exception as e:
            logger.exception("failed for questionnaire:"+questionnaire.id)
    mark_as_completed(db_name)

migrate(all_db_names(), make_feed_document_use_form_code_instead_of_form_model_id, version=(17, 1, 1), threads=3)