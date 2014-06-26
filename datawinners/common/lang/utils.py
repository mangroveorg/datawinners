from collections import OrderedDict
from django.utils import translation
from django.utils.translation import ugettext as _, ugettext
from mangrove.datastore.cache_manager import get_cache_manager
from datawinners.common.lang.custom_message_static_codes import TITLE_QUESTIONNAIRE_REPLY_MESSAGE_CODE_MAP, QUESTIONNAIRE_CUSTOM_MESSAGE_CODES, ACCOUNT_WIDE_CUSTOM_MESSAGE_CODES, DEFAULT_LANGUAGES, TITLE_ACCOUNT_WIDE_REPLY_MESSAGE_CODE_MAP
from datawinners.common.lang.messages import QuestionnaireCustomizedMessages, AccountWideSMSMessage, ACCOUNT_MESSAGE_DOC_ID, \
    get_language_cache_key, LANGUAGE_EXPIRY_TIME_IN_SEC
from datawinners.utils import get_organization_language

ERROR_MSG_MISMATCHED_SYS_VARIABLE = _('Oops, something went wrong. You deleted a personalized response (gray box). Please edit the text without deleting the personalized response and save again.')

def questionnaire_customized_message_details(dbm, language_code):
    cache_manger = get_cache_manager()
    key_as_str = get_language_cache_key(dbm, language_code)
    messages_dict = cache_manger.get(key_as_str)

    if messages_dict is None:
        customized_message_row = dbm.load_all_rows_in_view('all_languages', startkey=language_code, endkey=language_code, include_docs=True)[0]
        reply_messages_dict = customized_message_row["doc"]["messages"]
        messages_dict = _build_message_details(reply_messages_dict, TITLE_QUESTIONNAIRE_REPLY_MESSAGE_CODE_MAP)
        cache_manger.set(key_as_str, messages_dict, time=LANGUAGE_EXPIRY_TIME_IN_SEC)

    return messages_dict

def account_wide_customized_message_details(dbm):
    cache_manger = get_cache_manager()
    key_as_str = get_language_cache_key(dbm, ACCOUNT_MESSAGE_DOC_ID)
    messages_dict = cache_manger.get(key_as_str)

    if messages_dict is None:
        account_wide_message = dbm.database.get(ACCOUNT_MESSAGE_DOC_ID)
        messages_dict = _build_message_details(account_wide_message["messages"], TITLE_ACCOUNT_WIDE_REPLY_MESSAGE_CODE_MAP)
        cache_manger.set(key_as_str, messages_dict, time=LANGUAGE_EXPIRY_TIME_IN_SEC)

    return messages_dict


def _build_message_details(reply_messages_dict, reply_message_code_map):
    reply_list = []
    for code, reply_message_title in reply_message_code_map.iteritems():
        details_dict = {"title": reply_message_title}
        details_dict.update({"message": reply_messages_dict.get(code)})
        details_dict.update({"code": code})
        reply_list.append(details_dict)
    return reply_list

def questionnaire_reply_default_messages(lang_code=None):
    if lang_code and lang_code in ["en", "fr", "pt", "mg"]:
        translation.activate(lang_code)
    default_messages = OrderedDict()
    default_messages.update(
        {QUESTIONNAIRE_CUSTOM_MESSAGE_CODES[0]: _("Thank you {Name of Data Sender}. We received your SMS: {List of Answers}")})
    default_messages.update({QUESTIONNAIRE_CUSTOM_MESSAGE_CODES[1]:
                         _("Error. Incorrect answer for question {Question Numbers for Wrong Answer(s)}. Please review printed Questionnaire and resend entire SMS.")})
    default_messages.update({QUESTIONNAIRE_CUSTOM_MESSAGE_CODES[2]:
                         _("Error. Incorrect number of responses. Please review printed Questionnaire and resend entire SMS.")})
    default_messages.update({QUESTIONNAIRE_CUSTOM_MESSAGE_CODES[3]:
                         _("Error. {Submitted Identification Number} is not registered. Check the Identification Number and resend entire SMS or contact your supervisor.")})
    default_messages.update({QUESTIONNAIRE_CUSTOM_MESSAGE_CODES[4]:
             _("Error. You are not authorized to submit data for this Questionnaire. Please contact your supervisor.")})
    return default_messages

def account_wide_sms_default_messages(account_language=None):
    if account_language:
        translation.activate(account_language)
    default_messages = OrderedDict()
    default_messages.update(
        {ACCOUNT_WIDE_CUSTOM_MESSAGE_CODES[0]: _("Error. You are not registered as a Data Sender. Please contact your supervisor.")})
    default_messages.update({ACCOUNT_WIDE_CUSTOM_MESSAGE_CODES[1]:
                         _("Error. Questionnaire Code {Submitted Questionnaire Code} is incorrect. Find the Code on the top of the printed Questionnaire and resend SMS starting with this Code.")})
    default_messages.update({ACCOUNT_WIDE_CUSTOM_MESSAGE_CODES[2]:
                         _("Thank you {Name of Data Sender}.We registered your {Identification Number Type} {Name of Identification Number} {Submitted Identification Number}.")})
    default_messages.update({ACCOUNT_WIDE_CUSTOM_MESSAGE_CODES[3]:
                         _("Error. Incorrect answer for question {Question Numbers for Wrong Answer(s)}. Please review printed Questionnaire and resend entire SMS.")})
    default_messages.update({ACCOUNT_WIDE_CUSTOM_MESSAGE_CODES[4]:
                         _("Error. Incorrect number of responses. Please review printed Questionnaire and resend entire SMS.")})
    default_messages.update({ACCOUNT_WIDE_CUSTOM_MESSAGE_CODES[5]:
                        _("Error. {Submitted Identification Number} already exists. Register your {Identification Number Type} with a different Identification Number.")})
    return default_messages

def save_questionnaire_reply_message_template(code, dbm, lang):
    customized_message = QuestionnaireCustomizedMessages(code, lang, questionnaire_reply_default_messages())
    return dbm._save_document(customized_message)


def save_account_wide_reply_message_template(dbm):
    account_message = AccountWideSMSMessage(account_wide_sms_default_messages())
    return dbm._save_document(account_message)


def create_custom_message_templates(dbm):
    account_language = get_organization_language(dbm)
    for code, lang in DEFAULT_LANGUAGES.iteritems():
        translation.activate(code)
        save_questionnaire_reply_message_template(code, dbm, lang)
        if code == account_language:
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
        languages_list.append({'code': code, 'name': _(language_name)})
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

