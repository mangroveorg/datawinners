from datawinners.messageprovider.tests.test_message_handler import THANKS
from tests.smstestertests.sms_tester_data import SENDER, RECEIVER, SMS

QCODE = 'qcode'
ANSWER = 'answer'
TYPE = "type"
SELECT = "select"
TEXT = "text"
CHECKBOX = "checkbox"

EDITED_ANSWERS = [
    {QCODE: 'q1', ANSWER: 'Test (wp02)', TYPE: SELECT},
    {QCODE: 'q2', ANSWER: '25.12.2013', TYPE: TEXT},
    {QCODE: 'q3', ANSWER: '8', TYPE: TEXT},
    {QCODE: 'q4', ANSWER: '24.12.2012', TYPE: TEXT},
    {QCODE: 'q5', ANSWER: 'LIGHT YELLOW', TYPE: SELECT},
    {QCODE: 'q6', ANSWER: 'admin1', TYPE: TEXT},
    {QCODE: 'q7', ANSWER: ['a'], TYPE: CHECKBOX},
    {QCODE: 'q8', ANSWER: '-18,27', TYPE: TEXT},
]

ANSWERS_TO_BE_SUBMITTED = [
    {QCODE: 'q1', ANSWER: 'Test (wp01)', TYPE: SELECT},
    {QCODE: 'q2', ANSWER: '25.12.2010', TYPE: TEXT},
    {QCODE: 'q3', ANSWER: '5', TYPE: TEXT},
    {QCODE: 'q4', ANSWER: '24.12.2010', TYPE: TEXT},
    {QCODE: 'q5', ANSWER: 'LIGHT RED', TYPE: SELECT},
    {QCODE: 'q6', ANSWER: 'admin', TYPE: TEXT},
    {QCODE: 'q7', ANSWER: ['b'], TYPE: CHECKBOX},
    {QCODE: 'q8', ANSWER: '12.0,12.0', TYPE: TEXT},
]


def get_sms_data_with_questionnaire_code(questionnaire_code):
    return {SENDER: "919049008976",
            RECEIVER: '919880734937',
            SMS: questionnaire_code + " wp01 25.12.2010 5 24.12.2010 a admin c 12,12",
            'message': (THANKS % "Ashwini") + u" for Waterpoint Ahmedabad Waterpoint (wp01): wp01; 25.12.2010; 5; 24.12.2010; LIGHT RED; admin; Chlorobia; 12.0, 12.0"}


def get_errorred_sms_data_with_questionnaire_code(questionnaire_code):
    return {SENDER: "919049008976",
            RECEIVER: '919880734937',
            SMS: questionnaire_code + " wp01 25.12.2010 5 24.12.2010 a admin f 12,12",
            'message': "Error. Incorrect answer for question 7."}
