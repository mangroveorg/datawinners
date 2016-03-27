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

QUESTIONNAIRE_FORM_ID = 'questionnaire_form_id'
FIELD_INPUT_NAME = 'input_name'
FIELD_INPUT_VALUE = 'input_value'
FIELD_SELECT1_NAME = 'select1_name'
FIELD_SELECT1_VALUE = 'select1_value'
FIELD_SELECT1_MINIMAL_NAME = 'select1_minimal_name'
FIELD_SELECT1_MINIMAL_VALUE = 'select1_minimal_value'
FIELD_SELECT1_MINIMAL_NUMBER = 'select1_minimal_number'
FIELD_SELECT1_AUTOCOMPLETE_NAME = 'select1_autocomplete_name'
FIELD_SELECT1_AUTOCOMPLETE_INPUT_VALUE = 'select1_autocomplete_input_value'
FIELD_SELECT1_AUTOCOMPLETE_ASSERT = 'select1_autocomplete_assert'
FIELD_SELECT1_AUTOCOMPLETE_VALUE = 'select1_autocomplete_value'
FIELD_SELECT1_AUTOCOMPLETE_NUMBER = 'select1_autocomplete_number'
FIELD_SELECT1_IDNR_AUTOCOMPLETE_NAME = 'select1_idnr_autocomplete_name'
FIELD_SELECT1_IDNR_AUTOCOMPLETE_INPUT_VALUE = 'select1_idnr_autocomplete_input_value'
FIELD_SELECT1_IDNR_AUTOCOMPLETE_ASSERT = 'select1_idnr_autocomplete_assert'
FIELD_SELECT1_IDNR_AUTOCOMPLETE_VALUE = 'select1_idnr_autocomplete_value'
FIELD_SELECT1_IDNR_AUTOCOMPLETE_NUMBER = 'select1_idnr_autocomplete_number'
SECTION_REPEAT_NAME = 'questionnaire_test_autocomplete_repeat_name'
SECTION_REPEAT_NUMBER = 'questionnaire_test_autocomplete_repeat_number'
FIELD_SELECT1_IDNR_AUTOCOMPLETE_IN_REPEAT_NAME = 'select1_idnr_autocomplete_in_repeat_name'
FIELD_SELECT1_IDNR_AUTOCOMPLETE_IN_REPEAT_INPUT_VALUE = 'select1_idnr_autocomplete_in_repeat_input_value'
FIELD_SELECT1_IDNR_AUTOCOMPLETE_IN_REPEAT_ASSERT = 'select1_idnr_autocomplete_in_repeat_assert'
FIELD_SELECT1_IDNR_AUTOCOMPLETE_IN_REPEAT_VALUE = 'select1_idnr_autocomplete_in_repeat_value'
FIELD_INPUT_IN_REPEAT_NAME = 'input_in_repeat_name'
FIELD_INPUT_IN_REPEAT_VALUE = 'input_in_repeat_value'


QUESTIONNAIRE_AUTOCOMPLETE_DATA = {
    PROJECT_NAME : 'Test auto complete',
    QUESTIONNAIRE_FORM_ID : "questionnaire_for_functional_test_autocomplete",
    FIELD_INPUT_NAME : 'respondent_name',
    FIELD_INPUT_VALUE : 'Safidison',
    FIELD_SELECT1_NAME : 'issue_type',
    FIELD_SELECT1_VALUE : 'Functionality',
    FIELD_SELECT1_MINIMAL_NAME : 'priority_min',
    FIELD_SELECT1_MINIMAL_VALUE : '',
    FIELD_SELECT1_MINIMAL_NUMBER : 1,
    FIELD_SELECT1_AUTOCOMPLETE_NAME : 'priority',
    FIELD_SELECT1_AUTOCOMPLETE_INPUT_VALUE : 'sho',
    FIELD_SELECT1_AUTOCOMPLETE_ASSERT : ["Showstopper"],
    FIELD_SELECT1_AUTOCOMPLETE_VALUE : 'Showstopper',
    FIELD_SELECT1_AUTOCOMPLETE_NUMBER : 1,
    FIELD_SELECT1_IDNR_AUTOCOMPLETE_NAME : 'select1_idnr_comp',
    FIELD_SELECT1_IDNR_AUTOCOMPLETE_INPUT_VALUE : 'ana',
    FIELD_SELECT1_IDNR_AUTOCOMPLETE_ASSERT : ['ANALAMANGA (cli11)','TSIMANARIRAZANA (cli12)',
                                              'Farafangana (cli15)','Fianarantsoa-I (cli16)',
                                              'Analalava (cli8)'],
    FIELD_SELECT1_IDNR_AUTOCOMPLETE_VALUE : 'Farafangana (cli15)',
    FIELD_SELECT1_IDNR_AUTOCOMPLETE_NUMBER : 1,
    SECTION_REPEAT_NAME : 'section_address',
    SECTION_REPEAT_NUMBER : 3,
    FIELD_SELECT1_IDNR_AUTOCOMPLETE_IN_REPEAT_NAME : 'clinic_repeat',
    FIELD_SELECT1_IDNR_AUTOCOMPLETE_IN_REPEAT_INPUT_VALUE : 'ra',
    FIELD_SELECT1_IDNR_AUTOCOMPLETE_IN_REPEAT_ASSERT : ['TSIMANARIRAZANA (cli12)','Antsirabe (cli13)',
                                                        'Farafangana (cli15)','Fianarantsoa-I (cli16)'
                                                        ],
    FIELD_SELECT1_IDNR_AUTOCOMPLETE_IN_REPEAT_VALUE : 'Antsirabe (cli13)',
    FIELD_INPUT_IN_REPEAT_NAME : 'house_number',
    FIELD_INPUT_IN_REPEAT_VALUE : 'DISTR006',

}


