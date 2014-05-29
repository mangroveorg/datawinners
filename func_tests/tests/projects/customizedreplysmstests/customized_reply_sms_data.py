# coding=utf-8
PROJECT_NAME = "project_name"
PAGE_TITLE = "page_title"
QUESTIONNAIRE_CODE = "questionnaire_code"
GEN_RANDOM = "gen_random"
DEFAULT_QUESTION = "default_question"
QUESTION = "question"
QUESTIONS = "questions"
CODE = "code"
TYPE = "type"
NUMBER = "number"
WORD = "word"
LIMIT = "limit"
NO_LIMIT = "no_limit"
LIMITED = "limited"
MIN = "min"
MAX = "max"
EXISTING_UNIQUE_ID_TYPE = "existing_unique_id_type"
UNIQUE_ID = "unique_id"

PROJECT_DATA = {
                      PROJECT_NAME: "ft-project sms reply", GEN_RANDOM: True,
                    }

PROJECT_QUESTIONNAIRE_DATA = {
                      QUESTIONNAIRE_CODE: None, GEN_RANDOM: False,
                      QUESTIONS: [
                          {QUESTION: u"What is your namé?", CODE: u"q3", TYPE: WORD, LIMIT: LIMITED, MAX: u"20"},
                          {QUESTION: u"What is age öf father?", CODE: u"q4", TYPE: NUMBER, MIN: u"18", MAX: u"100"},
                          {QUESTION: u"Unique Id question", CODE: u"q11", TYPE: UNIQUE_ID,
                                  EXISTING_UNIQUE_ID_TYPE: 'Clinic'},

                      ],
                      PAGE_TITLE: "Data Senders"
                     }
SENDER = "from"
RECEIVER = "to"
SMS = "sms"
ERROR_MSG = "message"
SUCCESS_MESSAGE = "message"
MESSAGE = "message"

def get_success_sms_data_with_questionnaire_code(questionnaire_code):
    return {SENDER: "1234123413",
            RECEIVER: '919880734937',
            SMS: questionnaire_code + " sender_name 45 cid001"
            }

def get_error_sms_data_with_questionnaire_code(questionnaire_code):
    return {SENDER: "1234123413",
            RECEIVER: '919880734937',
            SMS: questionnaire_code + " sender_name 455 cid001"
            }

def get_error_sms_data_with_incorrect_number_of_answers(questionnaire_code):
    return {SENDER: "1234123413",
            RECEIVER: '919880734937',
            SMS: questionnaire_code + " sender_name 455 another cid001"
            }

def get_error_sms_data_with_incorrect_unique_id(questionnaire_code):
    return {SENDER: "1234123413",
            RECEIVER: '919880734937',
            SMS: questionnaire_code + " sender_name 455 cld001"
            }

def get_error_message_from_unauthorized_source(questionnaire_code):
    return {SENDER: "919049008976",
            RECEIVER: '919880734937',
            SMS: questionnaire_code + " sender_name 45 cid001"
            }


