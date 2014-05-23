from collections import OrderedDict
from django.utils import translation
from django.utils.translation import ugettext as _
from datawinners.common.lang.messages import CustomizedMessages


TITLE_REPLY_MESSAGE_CODE_MAP = OrderedDict([("reply_success_submission", "Successful Submission"),
                                            ("reply_incorrect_answers", "Submission with an Error"),
                                            ("reply_incorrect_number_of_responses", "Incorrect Number of Responses"),
                                            ("reply_identification_number_not_registered",
                                             "Identification Number not Registered"),
                                            ("reply_ds_not_authorized",
                                             "Data Sender not Authorized to Submit Data to this Questionnaire")])

languages = {"en": "English", "fr": "French","mg":"Malagasy","pt":"Portuguese"}

error_message_codes = ["reply_success_submission", "reply_incorrect_answers", "reply_incorrect_number_of_responses",
                       "reply_identification_number_not_registered", "reply_ds_not_authorized"]


def customized_message_details(dbm, language_code):
    reply_list = []
    customized_message_row = dbm.load_all_rows_in_view('all_languages', startkey=language_code, endkey=language_code, include_docs=True)[0]
    reply_messages_dict = customized_message_row["doc"]["messages"]
    for code, reply_message_title in TITLE_REPLY_MESSAGE_CODE_MAP.iteritems():
        details_dict = {"title": _(reply_message_title)}
        details_dict.update({"message": reply_messages_dict.get(code)})
        details_dict.update({"code": code})
        reply_list.append(details_dict)
    return reply_list


def save_reply_message_template(code, dbm, lang):
    messages = OrderedDict()
    messages.update(
        {error_message_codes[0]: "Thank you {Name of Data Sender}. We received your SMS: {List of Answers}"})
    messages.update({error_message_codes[1]:
                         "Error. Incorrect answer for question {Question Numbers for Wrong Answer(s)}. Please review printed Questionnaire and resend entire SMS."})
    messages.update({error_message_codes[2]:
        "Error. Incorrect number of responses. Please review printed Questionnaire and resend entire SMS."})
    messages.update({error_message_codes[3]:
        "Error. {Submitted Identification Number} is not registered. Check the Identification Number and resend entire SMS or contact your supervisor."})
    messages.update(
        {error_message_codes[4]:
            "Error. You are not authorized to submit data for this Questionnaire. Please contact your supervisor."})
    customized_message = CustomizedMessages(code, lang, messages)
    return dbm._save_document(customized_message)


def create_custom_message_templates(dbm):
    for code, lang in languages.iteritems():
        save_reply_message_template(code, dbm, lang)


def get_available_project_languages(dbm):
    lang_dict = []
    for row in dbm.load_all_rows_in_view("all_languages", include_docs=False):
        lang_dict.append({'code':row.key,'name': row.value})
    return lang_dict


class DuplicateLanguageException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message



def create_new_reply_message_template(dbm, language_name):
    rows = dbm.load_all_rows_in_view("by_language_name", key=language_name)
    if len(rows)>0:
        raise DuplicateLanguageException("This language already exists.")
    return save_reply_message_template(None, dbm, language_name)

