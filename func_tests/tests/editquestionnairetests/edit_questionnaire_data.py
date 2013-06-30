# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8


##Variables
from datawinners.messageprovider.tests.test_message_handler import THANKS

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
MM_DD_YYYY = "mm.dd.yyyy"
MM_YYYY = "mm.yyyy"
ONLY_ONE_ANSWER = "only_one_answer"
MULTIPLE_ANSWERS = "multiple_answers"
ERROR_MSG = "message"
SUCCESS_MSG = "message"
CHARACTER_REMAINING = "character_remaining"
SENDER = "from"
RECEIVER = "to"
SMS = "sms"
SUCCESS_MESSAGE = "success_message"

VALID_PROJECT_DATA = {PROJECT_NAME: "clinic5 test project"}

QUESTIONNAIRE_DATA = {QUESTIONNAIRE_CODE: u"cli005",
                      DEFAULT_QUESTION: {QUESTION: u"What is associatéd entity?", CODE: u"EID"},
                      QUESTIONS: [{QUESTION: u"What is your namé?", CODE: u"NA", TYPE: WORD, LIMIT: LIMITED, MAX: u"10"},
                              {QUESTION: u"What is age öf father?", CODE: u"FA", TYPE: NUMBER, MIN: u"18", MAX: u"100"},
                              {QUESTION: u"What is réporting date?", CODE: u"RD", TYPE: DATE, DATE_FORMAT: DD_MM_YYYY},
                              {QUESTION: u"What is your blood group?", CODE: u"BG", TYPE: LIST_OF_CHOICES,
                               CHOICE: [u"O+", u"O-", u"AB", u"B+"],
                               ALLOWED_CHOICE: ONLY_ONE_ANSWER},
                              {QUESTION: u"What aré symptoms?", CODE: u"SY", TYPE: LIST_OF_CHOICES,
                               CHOICE: [u"Rapid weight loss", u"Dry cough", u"Pneumonia", u"Memory loss",
                                        u"Neurological disorders "],
                               ALLOWED_CHOICE: MULTIPLE_ANSWERS},
                              {QUESTION: u"What is the GPS codé for clinic", CODE: u"GPS", TYPE: GEO}],
                      CHARACTER_REMAINING: u"84 / 160 characters used"}

TITLE = "title"
MESSAGE = "message"

LIGHT_BOX_DATA = {TITLE: "Warning !!",
                  MESSAGE: "Warning: Changing the date format of report period will remove all your collected data. Are you sure you want to continue?"}

VALID_SMS = {SENDER: "919049008976",
                RECEIVER: '919880734937',
                SMS: "cli005 cid001 mino 90 25.12.2010 a d -18.1324,27.6547",
                SUCCESS_MESSAGE: (THANKS % "Ashwini") + u" for Clinic Bhopal Clinic (cid001): cid001; mino; 90; 25.12.2010; O+; Memory loss; -18.1324, 27.6547"}

DELETE_QUESTIONNAIRE_WITH_COLLECTED_DATA_WARNING = u'If you delete this question, any previously collected data will be lost.\nDo you want to delete this question?'
SAVE_QUESTIONNAIRE_WITH_NEWLY_COLLECTED_DATA_WARNING = u'If you modify this questionnaire, any previously collected data will be lost.\n\nDo you want to modify this questionnaire?'

VALID_SMS_SUBJECT_DATA = {SENDER: "919049008976",
                RECEIVER: '919880734937',
                SMS: "sub prenom anarana harbin 12,19 033143333 reg001",
                SUCCESS_MESSAGE: u"Thank you Ashwini, We registered your subject type: prenom; anarana; harbin; 12.0, 19.0; 033143333; reg001"}
SUBJECT_TYPE = "subject type"

CHANGE_QUESTION_TYPE_MSG = u'You have changed the Answer Type.\nIf you have previously collected data, it may be rendered incorrect.\n\nAre you sure you want to continue?'
REDISTRIBUTE_QUESTIONNAIRE_MSG = u'You have made changes to your Questionnaire.\n\nPlease make sure your Data Senders have the latest version:\nSMS: Print and distribute the updated SMS Questionnaire\nSmartphone: Remind them to download the updated version of the Questionnaire\nWeb: No action needed. We will display the updated version of the Registration Form automatically'