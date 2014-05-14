import logging
from datawinners.common.lang.messages import CustomizedMessages
from datawinners.main.couchdb.utils import all_db_names
from datawinners.main.database import get_db_manager
from migration.couch.utils import migrate, mark_as_completed


error_message_codes = ["success_submission", "incorrect_answers", "incorrect_number_of_responses",
                       "identification_number_not_registered", "ds_not_authorized"]


def create_english_template(dbm):
    english_messages = {}
    english_messages.update({error_message_codes[0]: "Thank you we received your submission"})
    english_messages.update({error_message_codes[1]:
                                 "Error.Incorrect answer for questions.Please review printed Questionnaire and resend entire SMS"})
    english_messages.update({error_message_codes[2]: "Error.Incorrect number of responses. Review printed Questionnaire and resend entire SMS."})
    english_messages.update({error_message_codes[3]: "This identification number is not registered"})
    english_messages.update({error_message_codes[4]: "You are not authorized to submit data to this Questionnaire. Please contact your project manager"})

    english_message = CustomizedMessages("en", "English", english_messages)

    dbm._save_document(english_message)


def create_french_template(dbm):
    french_messages = {}
    french_messages.update({error_message_codes[0]: "Thank you we received your submission"})
    french_messages.update({error_message_codes[1]:
                                 "Error.Incorrect answer for questions.Please review printed Questionnaire and resend entire SMS"})
    french_messages.update({error_message_codes[2]: "Error.Incorrect number of responses. Review printed Questionnaire and resend entire SMS."})
    french_messages.update({error_message_codes[3]: "This identification number is not registered"})
    french_messages.update({error_message_codes[4]: "You are not authorized to submit data to this Questionnaire. Please contact your project manager"})

    french_message = CustomizedMessages("fr", "French", french_messages)

    dbm._save_document(french_message)



def create_language_template(dbm, logger):
    create_english_template(dbm)
    create_french_template(dbm)


def migrate_to_create_language_templates(db_name):
    logger = logging.getLogger(db_name)
    try:
        logger.info('Starting migration')
        dbm = get_db_manager(db_name)
        create_language_template(dbm, logger)
    except Exception as e:
        logger.exception(e.message)
    mark_as_completed(db_name)


migrate(all_db_names(), migrate_to_create_language_templates, version=(12, 0, 1), threads=3)