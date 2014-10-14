import logging
from datawinners.feeds.database import get_feed_db_from_main_db_name
from datawinners.main.database import get_db_manager
from mangrove.datastore.documents import EnrichedSurveyResponseDocument
from migration.couch.utils import migrate, mark_as_completed

db_names = [
    "hni_psi-madagascar_qmx864597",
    "hni_usaid-mikolo_lei526034",
    "hni_pnncseecaline_bpn692977",
    "hni_unite-de-lutte-contre-le-sida_nps932546",
    "hni_msanp_ubl254585",
    "hni_palme_flm546389",
    "hni_ingc-zambezia_gkg847094",
    "hni_ingc-pemba_nlt434261",
    "hni_chemonics-mozambique_ehh942480"]


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

migrate(db_names, make_feed_document_use_form_code_instead_of_form_model_id, version=(13, 1, 3), threads=3)