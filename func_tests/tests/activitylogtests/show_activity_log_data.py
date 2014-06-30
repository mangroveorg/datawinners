# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8


##Variables
ACTIVITY_LOG_PAGE_TITLE = "Activity Log"
TESTER_NAME = "Tester Pune"
CREATED_PROJECT_ACTION = "Created Questionnaire"

PROJECT_NAME = "project_name"
PAGE_TITLE = "page_title"
QUESTIONNAIRE_CODE = "questionnaire_code"
GEN_RANDOM = "gen_random"
DEFAULT_QUESTION = "default_question"
QUESTION = "question"
QUESTIONS = "questions"
CODE = "code"
TYPE = "type"
LIMIT = "limit"
NO_LIMIT = "no_limit"
LIMITED = "limited"
MIN = "min"
MAX = "max"
DATE_FORMAT = "date_format"
CHOICE = "choice"
ALLOWED_CHOICE = "allowed_choice"
NUMBER = "number"
WORD = "word"
DATE = "date"
LIST_OF_CHOICES = "list_of_choices"
GEO = "geo"
DD_MM_YYYY = "dd.mm.yyyy"
ONLY_ONE_ANSWER = "only_one_answer"
MULTIPLE_ANSWERS = "multiple_answers"
CHARACTER_REMAINING = "character_remaining"

PROJECT_BACKGROUND = "project_background"
REPORT_TYPE = "report_type"
SUBJECT = "subject"
DEVICES = "devices"
WARNING_MESSAGE = "warning_message"
SUCCESS_MSG = "message"
QCODE = 'qcode'
ANSWER = 'answer'
TYPE = "type"

SELECT = "select"
TEXT = "text"
CHECKBOX = "checkbox"

QUESTIONNAIRE_DATA = {QUESTIONNAIRE_CODE: "WPS", GEN_RANDOM: True,
                      DEFAULT_QUESTION: {QUESTION: "What are you reporting on?"},
                      QUESTIONS: [{QUESTION: "Number of Docs", TYPE: NUMBER, MIN: "1", MAX: "10"},
                                  {QUESTION: "Date of report", TYPE: DATE, DATE_FORMAT: DD_MM_YYYY},
                                  {QUESTION: "Color of Eyes", TYPE: LIST_OF_CHOICES,
                                   CHOICE: ["LIGHT RED", "LIGHT YELLOW", "DARK YELLOW"],
                                   ALLOWED_CHOICE: ONLY_ONE_ANSWER},
                                  {QUESTION: "Clinic admin name", TYPE: WORD, LIMIT: LIMITED,
                                   MAX: "10"},
                                  {QUESTION: "Bacterias in water", TYPE: LIST_OF_CHOICES,
                                   CHOICE: ["Aquificae", "Bacteroids", "Chlorobia"],
                                   ALLOWED_CHOICE: MULTIPLE_ANSWERS},
                                  {QUESTION: "Geo points of Clinic", TYPE: GEO}],
                      CHARACTER_REMAINING: "65 / 160 characters used (1 SMS)",
                      SUCCESS_MSG: "Your questionnaire has been saved",
                      PAGE_TITLE: "Data Senders"}

QUESTIONNAIRE_DATA_SIMPLE = {QUESTIONNAIRE_CODE: "SIM", GEN_RANDOM: True,
                      DEFAULT_QUESTION: {QUESTION: "What are you reporting on?"},
                      QUESTIONS: [],
                      CHARACTER_REMAINING: "65 / 160 characters used (1 SMS)",
                      SUCCESS_MSG: "Your questionnaire has been saved",
                      PAGE_TITLE: "Data Senders"}

NEW_PROJECT_DATA = {PROJECT_NAME: "Reporter Activities ", GEN_RANDOM: True,
                    PROJECT_BACKGROUND: "This project is created by functional automation suite.",
                    SUBJECT: "clinic",
                    REPORT_TYPE: "other subject",
                    DEVICES: ["sms", "web"],
                    PAGE_TITLE: "Questionnaires - Overview",
                    WARNING_MESSAGE:
                        u"Translate or re-word this question if needed, but donʼt change its meaning. You can also delete the question if you donʼt need it for your project."}

VALID_ANSWERS = [
    {QCODE: 'q2', ANSWER: '5', TYPE: TEXT},
    {QCODE: 'q3', ANSWER: '12.01.2013', TYPE: TEXT},
    {QCODE: 'q4', ANSWER: 'LIGHT RED', TYPE: SELECT},
    {QCODE: 'q5', ANSWER: 'something', TYPE: TEXT},
    {QCODE: 'q6', ANSWER: 'b', TYPE: CHECKBOX},
    {QCODE: 'q7', ANSWER: '-1,-1', TYPE: TEXT},
]

EDITED_ANSWERS = [
    {QCODE: 'q2', ANSWER: '4', TYPE: TEXT},
    {QCODE: 'q3', ANSWER: '11.01.2013', TYPE: TEXT},
    {QCODE: 'q4', ANSWER: 'LIGHT YELLOW', TYPE: SELECT},
    {QCODE: 'q5', ANSWER: 'nothing', TYPE: TEXT},
    {QCODE: 'q6', ANSWER: ['a', 'c'], TYPE: CHECKBOX},
    {QCODE: 'q7', ANSWER: '1,1', TYPE: TEXT},
]
