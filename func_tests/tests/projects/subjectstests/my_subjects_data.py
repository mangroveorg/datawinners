from framework.utils.common_utils import random_string

PROJECT_NAME = "project_name"
PROJECT_BACKGROUND = "project_background"
REPORT_TYPE = "report_type"
SUBJECT = "subject"
DEVICES = "devices"
ERROR_MSG = "message"
PAGE_TITLE = "page_title"

GEN_RANDOM = "gen_random"
QUESTIONNAIRE_CODE = "questionnaire_code"
QUESTION = "question"
QUESTIONS = "questions"
CODE = "code"
TYPE = "type"

NEW_UNIQUE_ID_TYPE = "new_unique_id_type"
EXISTING_UNIQUE_ID_TYPE = "existing_unique_id_type"
UNIQUE_ID = "unique_id"

CLINIC_PROJECT1_NAME = "clinic test project1"
PROJECT_DETAILS = {PROJECT_NAME: "Waterpoint morondava", GEN_RANDOM: True,
                          PROJECT_BACKGROUND: "This project is created by functional automation suite.",
                          SUBJECT: "waterpoint",
                          REPORT_TYPE: 'other subject',
                          DEVICES: "sms",
                          PAGE_TITLE: "Subjects"}

QUESTIONNAIRE_DATA_WITH_MULTIPLE_SUBJECTS = {QUESTIONNAIRE_CODE: random_string(5), GEN_RANDOM: False,
                      QUESTIONS: [
                                 {QUESTION: u"Unique Id question", TYPE: UNIQUE_ID,
                                      NEW_UNIQUE_ID_TYPE: 'gaming '+random_string(3), EXISTING_UNIQUE_ID_TYPE: ''},
                                 {QUESTION: u"Unique Id question 2", TYPE: UNIQUE_ID,
                                      NEW_UNIQUE_ID_TYPE: 'school '+random_string(3), EXISTING_UNIQUE_ID_TYPE: ''},
                      ]}
QUESTIONNAIRE_DATA_WITH_ONE_SUBJECT = {QUESTIONNAIRE_CODE: random_string(5), GEN_RANDOM: False,
                      QUESTIONS: [
                                 {QUESTION: u"Unique Id question", TYPE: UNIQUE_ID,
                                      NEW_UNIQUE_ID_TYPE: 'firestation '+random_string(3), EXISTING_UNIQUE_ID_TYPE: ''},
                      ]}