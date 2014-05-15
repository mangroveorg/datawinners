from collections import OrderedDict
import logging
from django.utils import translation
from datawinners.common.lang.messages import CustomizedMessages
from datawinners.main.couchdb.utils import all_db_names
from datawinners.main.database import get_db_manager
from migration.couch.utils import migrate, mark_as_completed
from django.utils.translation import ugettext as _

error_message_codes = ["reply_success_submission", "reply_incorrect_answers", "reply_incorrect_number_of_responses",
                       "reply_identification_number_not_registered", "reply_ds_not_authorized"]

languages = {"en": "English", "fr": "French"}


def create_templates(dbm):
    for code, lang in languages.iteritems():
        translation.activate(code)
        messages = OrderedDict()
        messages.update({error_message_codes[0]: _("Thank you {Name of Data Sender}. We received your SMS: {List of Answers}")})
        messages.update({error_message_codes[1]:
                             _("Error. Incorrect answer for question {Question Numbers for Wrong Answer(s)}. Please review printed Questionnaire and resend entire SMS.")})
        messages.update({error_message_codes[2]: _("Error. Incorrect number of responses. Please review printed Questionnaire and resend entire SMS.")})
        messages.update({error_message_codes[3]: _("Error. {Submitted Identification Number} is not registered. Check the Identification Number and resend entire SMS or contact your supervisor.")})
        messages.update(
            {error_message_codes[4]: _("You are not authorized to submit data for this Questionnaire. Please contact your supervisor.")})

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