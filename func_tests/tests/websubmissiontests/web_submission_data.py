# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from datawinners.messageprovider.tests.test_message_handler import THANKS
from framework.utils.common_utils import by_css

PROJECT_NAME = "project_name"
QCODE = 'qcode'
ANSWER = 'answer'
TYPE = "type"

SELECT = "select"
TEXT = "text"
CHECKBOX = "checkbox"
SENDER = "from"
RECEIVER = "to"
SMS = "sms"
SUCCESS_MESSAGE = "success_message"
GEN_RANDOM = "gen_random"
QUESTIONNAIRE_CODE = "questionnaire_code"

NEW_PROJECT_DATA = {PROJECT_NAME: "SubmitDataOnBehalfOf", GEN_RANDOM: True}
QUESTION = "question"
QUESTIONS = "questions"
CODE = "code"
MIN = "min"
MAX = "max"
NUMBER = "number"

QUESTIONNAIRE_DATA = {QUESTIONNAIRE_CODE: "Sub", GEN_RANDOM: True,
                      QUESTIONS: [{QUESTION: "Number of Docs", TYPE: NUMBER, MIN: "1", MAX: "10"}]}


VALID_ANSWERS = [
    {QCODE: 'eid', ANSWER: 'Indore Clinic', TYPE: SELECT},
    {QCODE: 'NA', ANSWER: 'Bob', TYPE: TEXT},
    {QCODE: 'FA', ANSWER: '89', TYPE: TEXT},
    {QCODE: 'RD', ANSWER: '25.12.2011', TYPE: TEXT},
    {QCODE: 'BG', ANSWER: 'O-', TYPE: SELECT},
    {QCODE: 'SY', ANSWER: ['a', 'c'], TYPE: CHECKBOX},
    {QCODE: 'GPS', ANSWER: '-18.1324 27.6547', TYPE: TEXT},
    {QCODE: 'RM', ANSWER: ['c'], TYPE: CHECKBOX},
]


VALID_SMS = {SENDER: "919049008976",
             RECEIVER: '919880734937',
             SMS: "cli001 cid001 mino 90 25.12.2010 a d -18.1324,27.6547 a",
             'message': THANKS + u" q1: cid001 q2: mino q3: 90 q4: 25.12.2010 q5: O+ q6: Memory loss q7: -18.1324, 27.6547 q8: Hivid"}

DEFAULT_ORG_DATA = {
    PROJECT_NAME: 'clinic test project1'
}

TRIAL_ORG_DATA = {
    PROJECT_NAME: 'FILL ME IN!'
}

VALID_ANSWER = [
    {QCODE: 'q2', ANSWER: '5', TYPE: TEXT}]

EDIT_BUTTON = by_css(".edit")

EDITED_ANSWERS = [
    {QCODE: 'q2', ANSWER: '4', TYPE: TEXT}]

