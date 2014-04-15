# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from datawinners.messageprovider.tests.test_message_handler import THANKS
from framework.utils.common_utils import random_number
from mangrove.utils.test_utils.database_utils import uniq

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
UNIQUE_ID = "unique_id"
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
PROJECT_BACKGROUND = "project_background"
REPORT_TYPE = "report_type"
SUBJECT = "subject"
DEVICES = "devices"
NEW_UNIQUE_ID_TYPE = "new_unique_id_type"
EXISTING_UNIQUE_ID_TYPE = "existing_unique_id_type"

VALID_PROJECT_DATA = {PROJECT_NAME: "clinic5 test project"}

CLINIC_PROJECT_DATA = {PROJECT_NAME: "clinic5 test project project ", GEN_RANDOM: True}

WATERPOINT_PROJECT_DATA = {PROJECT_NAME: "new project ", GEN_RANDOM: True,
                           PROJECT_BACKGROUND: "This project is created by functional automation suite.",
                           SUBJECT: "waterpoint",
                           REPORT_TYPE: "other subject",
                           DEVICES: "sms",
                           PAGE_TITLE: "Questionnaires - Overview"}

VALID_SUMMARY_REPORT_DATA = {PROJECT_NAME: "Proj Reporter Activities ", GEN_RANDOM: True,
                             PROJECT_BACKGROUND: "This project is created by functional automation suite.",
                             SUBJECT: "",
                             REPORT_TYPE: "data sender work",
                             DEVICES: "sms",
                             PAGE_TITLE: "Questionnaires - Overview",
                             "warning_message":
                                 u"Translate or re-word this question if needed, but donʼt change its meaning. You can also delete the question if you donʼt need it for your project."}

LONG_DESCRIPTION_DATA = {PROJECT_NAME: "Proj Reporter Activities ", GEN_RANDOM: True,
                         PROJECT_BACKGROUND: u"Exemple: Collecter les données émanant de 100 écoles primaires situées à Antananarivo, dans le but de faire passer le taux d'assiduité des enseignantsExemple: Collecter les données émanant de 100 écoles primaires situées à Antananarivo, dans le but de faire passer le taux d'assiduité des enseignants12345",
                         SUBJECT: "",
                         REPORT_TYPE: "data sender work",
                         DEVICES: "sms",
                         PAGE_TITLE: "Questionnaires - Overview",
                         "warning_message":
                             u"Translate or re-word this question if needed, but donʼt change its meaning. You can also delete the question if you donʼt need it for your project."}

QUESTIONNAIRE_DATA_WITH_MANY_MC_QUSTIONS = {QUESTIONNAIRE_CODE: u"cli005", GEN_RANDOM: True,
                                            DEFAULT_QUESTION: {QUESTION: u"What is associatéd entity?", CODE: u"EID"},
                                            QUESTIONS: [
                                                {QUESTION: u"What is your namé?", CODE: u"q3", TYPE: WORD,
                                                 LIMIT: LIMITED, MAX: u"10"},
                                                {QUESTION: u"What is age öf father?", CODE: u"q4", TYPE: NUMBER,
                                                 MIN: u"18", MAX: u"100"},
                                                {QUESTION: u"What is réporting date?", CODE: u"q5", TYPE: DATE,
                                                 DATE_FORMAT: DD_MM_YYYY},
                                                {QUESTION: u"What is your blood group?", CODE: u"q6",
                                                 TYPE: LIST_OF_CHOICES,
                                                 CHOICE: [u"O+", u"O-", u"AB", u"B+"],
                                                 ALLOWED_CHOICE: ONLY_ONE_ANSWER},
                                                {QUESTION: u"What aré symptoms?", CODE: u"q7", TYPE: LIST_OF_CHOICES,
                                                 CHOICE: [u"Rapid weight loss", u"Dry cough", u"Pneumonia"],
                                                 ALLOWED_CHOICE: MULTIPLE_ANSWERS},
                                                {QUESTION: u"What is the GPS codé for clinic", CODE: u"q8", TYPE: GEO}
                                            ],
                                            CHARACTER_REMAINING: u"84 / 160 characters used"}

QUESTIONNAIRE_DATA_CLINIC_PROJECT = {QUESTIONNAIRE_CODE: u"cli005", GEN_RANDOM: True,
                                     DEFAULT_QUESTION: {QUESTION: u"What is associatéd entity?", CODE: u"EID"},
                                     QUESTIONS: [
                                         {QUESTION: u"What is your namé?", CODE: u"q2", TYPE: WORD, LIMIT: LIMITED,
                                          MAX: u"10"},
                                         {QUESTION: u"What is age öf father?", CODE: u"q3", TYPE: NUMBER, MIN: u"18",
                                          MAX: u"100"},
                                         {QUESTION: u"What is réporting date?", CODE: u"q4", TYPE: DATE,
                                          DATE_FORMAT: DD_MM_YYYY},
                                         {QUESTION: u"What is your blood group?", CODE: u"q5", TYPE: LIST_OF_CHOICES,
                                          CHOICE: [u"O+", u"O-", u"AB", u"B+"],
                                          ALLOWED_CHOICE: ONLY_ONE_ANSWER},
                                         {QUESTION: u"What aré symptoms?", CODE: u"q6", TYPE: LIST_OF_CHOICES,
                                          CHOICE: [u"Rapid weight loss", u"Dry cough", u"Pneumonia", u"Memory loss",
                                                   u"Neurological disorders "],
                                          ALLOWED_CHOICE: MULTIPLE_ANSWERS},
                                         {QUESTION: u"What is the GPS codé for clinic", CODE: u"q7", TYPE: GEO},
                                     ],
                                     CHARACTER_REMAINING: u"84 / 160 characters used"}

TITLE = "title"
MESSAGE = "message"

LIGHT_BOX_DATA = {TITLE: "Warning !!",
                  MESSAGE: "Warning: Changing the date format of report period will remove all your collected data. Are you sure you want to continue?"}

VALID_SMS = {SENDER: "919049008976",
             RECEIVER: '919880734937',
             SMS: "cli005 cid001 mino 90 25.12.2010 a d -18.1324,27.6547",
             SUCCESS_MESSAGE: THANKS % "Ashwini"}

DELETE_QUESTIONNAIRE_WITH_COLLECTED_DATA_WARNING = u'If you delete this question, any previously collected data will be lost.\nDo you want to delete this question?'
SAVE_QUESTIONNAIRE_WITH_NEWLY_COLLECTED_DATA_WARNING = u'If you modify this questionnaire, any previously collected data will be lost.\n\nDo you want to modify this questionnaire?'

VALID_SMS_SUBJECT_DATA = {SENDER: "919049008976",
                          RECEIVER: '919880734937',
                          SMS: "sub prenom anarana harbin 12,19 033143333 reg001",
                          SUCCESS_MESSAGE: u"Thank you Ashwini, We registered your subject type: prenom; anarana; harbin; 12.0, 19.0; 033143333; reg001"}
SUBJECT_TYPE = "subject type"

CHANGE_QUESTION_TYPE_MSG = u'You have changed the Answer Type.\nIf you have previously collected data, it may be rendered incorrect.\n\nAre you sure you want to continue?'
REDISTRIBUTE_QUESTIONNAIRE_MSG = u'You have made changes to your Questionnaire.\n\nPlease make sure your Data Senders have the latest version:\nSMS: Print and distribute the updated SMS Questionnaire\nSmartphone: Remind them to download the updated version of the Questionnaire\nWeb: Remind them to download the updated version of the Import Submission template'
DELETE_QUESTION_MSG = 'If you delete this question, any previously collected data will be lost.\nDo you want to delete this question?'
EMPTY_QUESTIONNAIRE_MSG = 'Please add at least one question'

WATERPOINT_QUESTIONNAIRE_DATA = {QUESTIONNAIRE_CODE: "WPS", GEN_RANDOM: True,
                                 DEFAULT_QUESTION: {QUESTION: "What are you reporting on?", CODE: "WID"},
                                 QUESTIONS: [{QUESTION: "Water point", CODE: "Wp", TYPE: UNIQUE_ID, NEW_UNIQUE_ID_TYPE: "", EXISTING_UNIQUE_ID_TYPE: "Waterpoint"},
                                             {QUESTION: "Water Level", CODE: "WL", TYPE: NUMBER, MIN: "1", MAX: "10"},
                                             {QUESTION: "Date of report", CODE: "DR", TYPE: DATE,
                                              DATE_FORMAT: DD_MM_YYYY},
                                             {QUESTION: "Color of Water", CODE: "WC", TYPE: LIST_OF_CHOICES,
                                              CHOICE: ["LIGHT RED", "LIGHT YELLOW", "DARK YELLOW"],
                                              ALLOWED_CHOICE: ONLY_ONE_ANSWER},
                                             {QUESTION: "Water point admin name", CODE: "WAN", TYPE: WORD,
                                              LIMIT: LIMITED, MAX: "10"},
                                             {QUESTION: "Bacterias in water", CODE: "WB", TYPE: LIST_OF_CHOICES,
                                              CHOICE: ["Aquificae", "Bacteroids", "Chlorobia"],
                                              ALLOWED_CHOICE: MULTIPLE_ANSWERS},
                                             {QUESTION: "Geo points of water point", CODE: "GPS", TYPE: GEO}],
                                 CHARACTER_REMAINING: "73 / 160 characters used (1 SMS)",
                                 SUCCESS_MSG: "Your questionnaire has been saved",
                                 PAGE_TITLE: "Data Senders"}

QUESTIONS_WITH_INVALID_ANSWER_DETAILS =[
                                         {QUESTION: u"What is your namé?", CODE: u"q2", TYPE: WORD, LIMIT: LIMITED,
                                          MAX: u"AB"},
                                         {QUESTION: u"What is age öf father?", CODE: u"q3", TYPE: NUMBER, MIN: u"A",
                                          MAX: u"B"},
                                         {QUESTION: u"What is réporting date?", CODE: u"q4", TYPE: DATE,
                                          DATE_FORMAT: DD_MM_YYYY},
                                         {QUESTION: u"What is your blood group?", CODE: u"q5", TYPE: LIST_OF_CHOICES,
                                          CHOICE: [u"", u"", u""],
                                          ALLOWED_CHOICE: ONLY_ONE_ANSWER},
                                         {QUESTION: u"What aré symptoms?", CODE: u"q6", TYPE: LIST_OF_CHOICES,
                                          CHOICE: [u"Rapid weight loss", u"Dry cough", u"Pneumonia", u"Memory loss",
                                                   u"Neurological disorders "],
                                          ALLOWED_CHOICE: MULTIPLE_ANSWERS},
                                         {QUESTION: u"What is the GPS codé for clinic", CODE: u"q7", TYPE: GEO},
                                         {QUESTION: u"Unique Id question", CODE: u"q8", TYPE: UNIQUE_ID,
                                          NEW_UNIQUE_ID_TYPE: '', EXISTING_UNIQUE_ID_TYPE: ''},
                                         {QUESTION: u"Unique Id question", CODE: u"q8", TYPE: UNIQUE_ID,
                                          NEW_UNIQUE_ID_TYPE: 'new type'+random_number(3), EXISTING_UNIQUE_ID_TYPE: ''},
                                     ]

EDIT_PROJECT_DATA = {
                      PROJECT_NAME: "ft-edit project", GEN_RANDOM: True,
                    }

EDIT_PROJECT_QUESTIONNAIRE_DATA = {
                      QUESTIONNAIRE_CODE: None, GEN_RANDOM: False,
                      #DEFAULT_QUESTION: {QUESTION: "What are you reporting on?", CODE: "q1"},
                      QUESTIONS: [{QUESTION: u"Date of report in DD.MM.YYY format", CODE: u"q3", TYPE: DATE,
                                   DATE_FORMAT: DD_MM_YYYY},
                                  {QUESTION: u"Water Level", CODE: u"q4", TYPE: NUMBER, MIN: u"1", MAX: u"1000"},
                                  {QUESTION: u"Date of report in MM.YYY format", CODE: u"q5", TYPE: DATE,
                                   DATE_FORMAT: MM_YYYY},
                                  {QUESTION: u"Date of report in MM.DD.YYY format", CODE: u"q6", TYPE: DATE,
                                   DATE_FORMAT: MM_DD_YYYY},
                                  {QUESTION: u"Color of Water", CODE: u"q7", TYPE: LIST_OF_CHOICES,
                                   CHOICE: ["LIGHT RED", "LIGHT YELLOW", "DARK YELLOW"],
                                   ALLOWED_CHOICE: ONLY_ONE_ANSWER},
                                  {QUESTION: u"Water point admin name", CODE: u"q8", TYPE: WORD, LIMIT: LIMITED,
                                   MAX: u"10"},
                                  {QUESTION: u"Bacterias in water", CODE: u"q9", TYPE: LIST_OF_CHOICES,
                                   CHOICE: ["Aquificae", "Bacteroids", "Chlorobia"],
                                   ALLOWED_CHOICE: MULTIPLE_ANSWERS},
                                  {QUESTION: u"Geo points of Well", CODE: u"q10", TYPE: GEO},
                                 {QUESTION: u"Unique Id question", CODE: u"q11", TYPE: UNIQUE_ID,
                                  NEW_UNIQUE_ID_TYPE: 'new type'+random_number(3), EXISTING_UNIQUE_ID_TYPE: ''},
                                  ],
                      CHARACTER_REMAINING: "69 / 160 characters used (1 SMS)",
                      PAGE_TITLE: "Data Senders"
                     }

QUESTIONNAIRE_TAB_PROJECT_DATA = {
                      PROJECT_NAME: "ft-edit simple project", GEN_RANDOM: True,
                    }

QUESTIONNAIRE_TAB_QUESTIONNAIRE_DATA = {
                      QUESTIONNAIRE_CODE: None, GEN_RANDOM: False,
                      DEFAULT_QUESTION: {QUESTION: "What are you reporting on?", CODE: "q1"},
                      QUESTIONS: [{QUESTION: u"Some other Water Level", CODE: u"q1", TYPE: NUMBER, MIN: u"1", MAX: u"1000"}],
                      CHARACTER_REMAINING: "69 / 160 characters used (1 SMS)",
                      PAGE_TITLE: "Data Senders"
                     }

ADDITIONAL_TAB_QUESTIONNAIRE_DATA = {QUESTIONS: [{QUESTION: u"Date of report in DD.MM.YYY format", CODE: u"q3", TYPE: DATE,
                                   DATE_FORMAT: DD_MM_YYYY},
                                  {QUESTION: u"Water Level", CODE: u"q4", TYPE: NUMBER, MIN: u"1", MAX: u"1000"},
                                  {QUESTION: u"Date of report in MM.YYY format", CODE: u"q5", TYPE: DATE,
                                   DATE_FORMAT: MM_YYYY},
                                  {QUESTION: u"Date of report in MM.DD.YYY format", CODE: u"q6", TYPE: DATE,
                                   DATE_FORMAT: MM_DD_YYYY},
                                  {QUESTION: u"Color of Water", CODE: u"q7", TYPE: LIST_OF_CHOICES,
                                   CHOICE: ["LIGHT RED", "LIGHT YELLOW", "DARK YELLOW"],
                                   ALLOWED_CHOICE: ONLY_ONE_ANSWER},
                                  {QUESTION: u"Water point admin name", CODE: u"q8", TYPE: WORD, LIMIT: LIMITED,
                                   MAX: u"10"},
                                  {QUESTION: u"Bacterias in water", CODE: u"q9", TYPE: LIST_OF_CHOICES,
                                   CHOICE: ["Aquificae", "Bacteroids", "Chlorobia"],
                                   ALLOWED_CHOICE: MULTIPLE_ANSWERS},
                                  {QUESTION: u"Geo points of Well", CODE: u"q10", TYPE: GEO}]}


QUESTIONNAIRE_TAB_SUBMISSION_SMS = {SENDER: "1234123413",
             RECEIVER: '+919880734937',
             SMS: "%s 20",
             SUCCESS_MESSAGE: THANKS % "Tester"}


DIALOG_PROJECT_DATA = {PROJECT_NAME: "Some Dialog project", GEN_RANDOM: True}

COPY_PROJECT_DATA = {
                      PROJECT_NAME: "simple project", GEN_RANDOM: True,
                    }

COPY_PROJECT_QUESTIONNAIRE_DATA = {
                      QUESTIONNAIRE_CODE: None, GEN_RANDOM: False,
                      DEFAULT_QUESTION: {QUESTION: "What are you reporting on?", CODE: "q1"},
                      QUESTIONS: [{QUESTION: u"Some dummy question", CODE: u"q1", TYPE: NUMBER, MIN: u"1", MAX: u"1000"}],
                      CHARACTER_REMAINING: "69 / 160 characters used (1 SMS)",
                      PAGE_TITLE: "Data Senders"
                     }
