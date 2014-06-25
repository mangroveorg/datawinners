from collections import OrderedDict

TITLE_QUESTIONNAIRE_REPLY_MESSAGE_CODE_MAP = OrderedDict([("reply_success_submission", "Successful Submission"),
                                                          ("reply_incorrect_answers", "Submission with an Error"),
                                                          ("reply_incorrect_number_of_responses",
                                                           "Incorrect Number of Responses"),
                                                          ("reply_identification_number_not_registered",
                                                           "Identification Number not Registered"),
                                                          ("reply_ds_not_authorized",
                                                           "Data Sender not Authorized to Submit Data to this Questionnaire")])


QUESTIONNAIRE_CUSTOM_MESSAGE_CODES = ["reply_success_submission", "reply_incorrect_answers", "reply_incorrect_number_of_responses",
                       "reply_identification_number_not_registered", "reply_ds_not_authorized"]


TITLE_ACCOUNT_WIDE_REPLY_MESSAGE_CODE_MAP = OrderedDict([("reply_ds_not_registered", "Data Sender not Registered"),
                                                          ("reply_incorrect_questionnaire_code", "Questionnaire Code is Wrong"),
                                                          ("reply_success_identification_number_registration",
                                                           "Successful Identification Number Registration"),
                                                          ("reply_incorrect_answers",
                                                           "Identification Number Registration with an Error"),
                                                          ("reply_incorrect_number_of_responses",
                                                           "Identification Number Registration with Incorrect number of Responses"),
                                                          ("reply_identification_number_already_exists",
                                                           "Identification Number ID Already Exists"),
                                                          ])
ACCOUNT_WIDE_CUSTOM_MESSAGE_CODES = ["reply_ds_not_registered", "reply_incorrect_questionnaire_code",
                                      "reply_success_identification_number_registration", "reply_incorrect_answers","reply_incorrect_number_of_responses","reply_identification_number_already_exists"]

DEFAULT_LANGUAGES = {"en": "English", "fr": "French", "mg": "Malagasy", "pt": "Portuguese"}

