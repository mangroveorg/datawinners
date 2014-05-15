from collections import OrderedDict
from django.utils.translation import ugettext as _


TITLE_REPLY_MESSAGE_CODE_MAP = OrderedDict([("reply_success_submission", "Successful Submission"),
                                            ("reply_incorrect_answers", "Submission with an Error"),
                                            ("reply_incorrect_number_of_responses", "Incorrect Number of Responses"),
                                            ("reply_identification_number_not_registered",
                                             "Identification Number not Registered"),
                                            ("reply_ds_not_authorized",
                                             "Data Sender not Authorized to Submit Data to this Questionnaire")])


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

