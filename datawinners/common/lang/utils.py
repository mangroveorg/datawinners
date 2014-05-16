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

languages = {"en": "English", "fr": "French"}
error_message_codes = ["reply_success_submission", "reply_incorrect_answers", "reply_incorrect_number_of_responses",
                       "reply_identification_number_not_registered", "reply_ds_not_authorized"]


def customized_message_details(dbm, language):
    reply_list = []
    customized_message_row = dbm.load_all_rows_in_view('all_languages', startkey=language, endkey=language, include_docs=True)[0]
    reply_messages_dict = customized_message_row["doc"]["messages"]
    for code, reply_message_title in TITLE_REPLY_MESSAGE_CODE_MAP.iteritems():
        details_dict = {"title": _(reply_message_title)}
        details_dict.update({"message": reply_messages_dict.get(code)})
        details_dict.update({"code": code})
        reply_list.append(details_dict)
    return reply_list


def create_custom_message_templates(dbm):
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