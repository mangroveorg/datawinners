from datawinners import settings
import logging
from datawinners.main.initial_template_creation import create_questionnaire_templates
from datawinners.main.couchdb.utils import all_db_names


db_name = settings.QUESTIONNAIRE_TEMPLATE_DB_NAME
if not db_name in all_db_names():
    logging.basicConfig(filename='/var/log/datawinners/migration_release_11_0_1.log', level=logging.DEBUG)
    logger = logging.getLogger(db_name)
    try:
        created_template_doc_ids = create_questionnaire_templates()
        logger.info("created template docs are :" + str(created_template_doc_ids))
    except Exception as e:
        logger.exception(e.message)