USERNAME = 'username'
PASSWORD = 'password'
WELCOME_MESSAGE = 'message'

VALID_CREDENTIALS = {USERNAME: "tester150411@gmail.com",
                     PASSWORD: "tester150411",
                     WELCOME_MESSAGE: "Welcome Tester!"}

SUBJECT_TYPE = "student"
SUBJECT_TYPE_NAME = "subject_type"
SHORT_NAME = "short_name"
AUTO_GENERATE = "auto_generate"
NAME = "name"
LOCATION = "location"
GPS = "geo_code"
DESCRIPTION = "description"
MOBILE_NUMBER = "mobile_number"
SUCCESS_MSG = "message"
ERROR_MSG = "message"

SUB_FIRST_NAME = "sub_first_name"
SUB_LAST_NAME = "sub_last_name"
SUB_UNIQUE_ID = "sub_unique_id"

VALID_DATA = {SUBJECT_TYPE_NAME: SUBJECT_TYPE,
              SUB_FIRST_NAME: "jon",
              SUB_LAST_NAME: "he",
              LOCATION: "Monodova",
              GPS: "47.411631 28.369885",
              MOBILE_NUMBER: "345-678-90",
              SUB_UNIQUE_ID: "sch01"}

PROJECT_NAME = "project_name"
PROJECT_BACKGROUND = "project_background"
PROJECT_TYPE = "project_type"
REPORT_TYPE = "report_type"
SUBJECT = "subject"
DEVICES = "devices"
ERROR_MSG = "message"
PAGE_TITLE = "page_title"
GEN_RANDOM = "gen_random"
SURVEY = "survey"
PUBLIC_INFO = "public information"
DATA_SENDER_WORK = "data sender work"
OTHER_SUBJECT = "other subject"

VALID_PROJECT_DATA = {PROJECT_NAME: "Reporter Activities ", GEN_RANDOM: True,
                      PROJECT_BACKGROUND: "This project is created by functional automation suite.",
                      PROJECT_TYPE: SURVEY,
                      SUBJECT: "",
                      REPORT_TYPE: OTHER_SUBJECT,
                      DEVICES: "sms",
                      PAGE_TITLE: "Projects - Overview"}

CODE = "code"
TYPE = "type"
MIN = "min"
MAX = "max"
NUMBER = "number"

QUESTIONNAIRE_CODE = "questionnaire_code"
QUESTION = "question"
QUESTIONS = "questions"

QUESTIONNAIRE_DATA = {QUESTIONNAIRE_CODE: u"cli005", GEN_RANDOM: True,
                                            QUESTIONS: [{QUESTION: "How many grades did you get last year?", CODE: "GRADES",
                                                 TYPE: NUMBER, MIN: "1", MAX: "100"}]}
QUESTION_NAME = QUESTIONNAIRE_DATA[QUESTIONS][0][QUESTION]

QCODE = 'qcode'
ANSWER = 'answer'
SELECT = "select"
TEXT = "text"

VALID_ANSWERS = [
    [
        #{QCODE: 'q2', ANSWER: '3.8.2012', TYPE: TEXT},
        {QCODE: 'q2', ANSWER: 89, TYPE: TEXT},
    ],
    [
        #{QCODE: 'q2', ANSWER: '4.8.2012', TYPE: TEXT},
        {QCODE: 'q2', ANSWER: 90, TYPE: TEXT},
    ],
    [
        #{QCODE: 'q2', ANSWER: '5.8.2012', TYPE: TEXT},
        {QCODE: 'q2', ANSWER: 91, TYPE: TEXT},
    ],
    [
        #{QCODE: 'q2', ANSWER: '6.8.2012', TYPE: TEXT},
        {QCODE: 'q2', ANSWER: 92, TYPE: TEXT},
    ],
]

NOT_EXIST_SUBJECT_TYPE_ERROR_MESSAGE_PATTERN = "Subject type [%s] is not defined."

NOT_EXIST_SUBJECT_ID_ERROR_MESSAGE_PATTERN = "Subject [%s] is not registered."

DOES_NOT_EXISTED_FORM_ERROR_MESSAGE_PATTERN = "Questionnaire code [%s] does not existed."

DATA_FORMAT_ERROR_MESSAGE = "The format of start and end date should be DD-MM-YYYY. Example: 25-12-2011"

DATE_WRONG_ORDER_ERROR_MESSAGE = "Start date must before end date."

NO_DATA_SUCCESS_MESSAGE_FOR_SUBJECT = "No submission under this subject during this period."

NO_DATA_SUCCESS_MESSAGE_FOR_QUESTIONNAIRE = "No submission under this questionnaire during this period."

SUCCESS_MESSAGE = "You can access the data in submissions field."
