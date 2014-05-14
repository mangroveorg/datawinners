import logging
from django.utils import translation
from datawinners.common.lang.messages import CustomizedMessages
from datawinners.main.couchdb.utils import all_db_names
from datawinners.main.database import get_db_manager
from migration.couch.utils import migrate, mark_as_completed
from django.utils.translation import ugettext as _

error_message_codes = ["success_submission", "incorrect_answers", "incorrect_number_of_responses",
                       "identification_number_not_registered", "ds_not_authorized"]

languages = {"English": "English", "French": "French"}


def create_templates(dbm):
    for code, lang in languages.iteritems():
        translation.activate(code)
        messages = {}
        messages.update({error_message_codes[0]: _("Thank you we received your submission")})
        messages.update({error_message_codes[1]:
                             _("Error.Incorrect answer for questions.Please review printed Questionnaire and resend entire SMS")})
        messages.update({error_message_codes[2]: _("Error.Incorrect number of responses. Review printed Questionnaire and resend entire SMS.")})
        messages.update({error_message_codes[3]: _("This identification number is not registered")})
        messages.update(
            {error_message_codes[4]: _("You are not authorized to submit data to this Questionnaire. Please contact your project manager")})

        customized_message = CustomizedMessages(code, lang, messages)
        dbm._save_document(customized_message)


def create_language_template(dbm, logger):
    create_templates(dbm)

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