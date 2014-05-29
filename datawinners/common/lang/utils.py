from collections import OrderedDict
from django.utils import translation
from django.utils.translation import ugettext as _, ugettext
from datawinners.common.lang.custom_message_static_codes import TITLE_QUESTIONNAIRE_REPLY_MESSAGE_CODE_MAP, QUESTIONNAIRE_CUSTOM_MESSAGE_CODES, ACCOUNT_WIDE_CUSTOM_MESSAGE_CODES, DEFAULT_LANGUAGES, TITLE_ACCOUNT_WIDE_REPLY_MESSAGE_CODE_MAP
from datawinners.common.lang.messages import QuestionnaireCustomizedMessages, AccountWideSMSMessage, ACCOUNT_MESSAGE_DOC_ID


def questionnaire_customized_message_details(dbm, language_code):
    customized_message_row = dbm.load_all_rows_in_view('all_languages', startkey=language_code, endkey=language_code, include_docs=True)[0]
    reply_messages_dict = customized_message_row["doc"]["messages"]
    return _build_message_details(reply_messages_dict, TITLE_QUESTIONNAIRE_REPLY_MESSAGE_CODE_MAP)


def account_wide_customized_message_details(dbm):
    account_wide_message = dbm.database.get(ACCOUNT_MESSAGE_DOC_ID)
    return _build_message_details(account_wide_message["messages"],TITLE_ACCOUNT_WIDE_REPLY_MESSAGE_CODE_MAP)


def _build_message_details(reply_messages_dict, reply_message_code_map):
    reply_list = []
    for code, reply_message_title in reply_message_code_map.iteritems():
        details_dict = {"title": _(reply_message_title)}
        details_dict.update({"message": reply_messages_dict.get(code)})
        details_dict.update({"code": code})
        reply_list.append(details_dict)
    return reply_list


def save_questionnaire_reply_message_template(code, dbm, lang):
    messages = OrderedDict()
    messages.update(
        {QUESTIONNAIRE_CUSTOM_MESSAGE_CODES[0]: _("Thank you {Name of Data Sender}. We received your SMS: {List of Answers}")})
    messages.update({QUESTIONNAIRE_CUSTOM_MESSAGE_CODES[1]:
                         _("Error. Incorrect answer for question {Question Numbers for Wrong Answer(s)}. Please review printed Questionnaire and resend entire SMS.")})
    messages.update({QUESTIONNAIRE_CUSTOM_MESSAGE_CODES[2]:
                         _("Error. Incorrect number of responses. Please review printed Questionnaire and resend entire SMS.")})
    messages.update({QUESTIONNAIRE_CUSTOM_MESSAGE_CODES[3]:
                         _("Error. {Submitted Identification Number} is not registered. Check the Identification Number and resend entire SMS or contact your supervisor.")})
    messages.update({QUESTIONNAIRE_CUSTOM_MESSAGE_CODES[4]:
             _("Error. You are not authorized to submit data for this Questionnaire. Please contact your supervisor.")})
    customized_message = QuestionnaireCustomizedMessages(code, lang, messages)
    return dbm._save_document(customized_message)


def save_account_wide_reply_message_template(dbm):
    messages = OrderedDict()
    messages.update(
        {ACCOUNT_WIDE_CUSTOM_MESSAGE_CODES[0]: "Error. You are not registered as a Data Sender. Please contact your supervisor."})
    messages.update({ACCOUNT_WIDE_CUSTOM_MESSAGE_CODES[1]:
                         "Error.Questionnaire Code {Submitted Questionnaire Code} is incorrect. Find the Code on the top of the printed Questionnaire and resend SMS starting with this Code."})
    messages.update({ACCOUNT_WIDE_CUSTOM_MESSAGE_CODES[2]:
                         "Thank you {Name of Data Sender}.We registered {Identification Number Type} {Name of Identification Number} {Submitted Identification Number}"})
    messages.update({ACCOUNT_WIDE_CUSTOM_MESSAGE_CODES[3]:
                         "Error.{Submitted Identification Number} already exists. Register your {Identification Number Type} with a different Identification Number"})
    account_message = AccountWideSMSMessage(messages)
    return dbm._save_document(account_message)


def create_custom_message_templates(dbm):
    for code, lang in DEFAULT_LANGUAGES.iteritems():
        translation.activate(code)
        save_questionnaire_reply_message_template(code, dbm, lang)
    save_account_wide_reply_message_template(dbm)


def get_available_project_languages(dbm):
    lang_dict = {}
    for row in dbm.load_all_rows_in_view("all_languages", include_docs=False):
        lang_dict.update({row.key: row.value})
    languages_list = _get_languages_sorted_by_name(lang_dict)
    return languages_list


def _get_languages_sorted_by_name(lang_dict):
    languages_list = []
    sorted_language_dict = OrderedDict(sorted(lang_dict.items(), key=lambda x: x[1].lower()))
    for code, language_name in sorted_language_dict.iteritems():
        languages_list.append({'code': code, 'name': language_name})
    return languages_list


class DuplicateLanguageException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


def create_new_questionnaire_reply_message_template(dbm, language_name):
    rows = dbm.load_all_rows_in_view("by_language_name", key=language_name.lower())
    if len(rows) > 0:
        raise DuplicateLanguageException(ugettext("%s already exists.") % language_name)
    return save_questionnaire_reply_message_template(None, dbm, language_name)

