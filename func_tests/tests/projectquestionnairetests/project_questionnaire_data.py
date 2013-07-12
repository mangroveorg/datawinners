# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
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
PROJECT_BACKGROUND = "project_background"
PROJECT_TYPE = "project_type"
REPORT_TYPE = "report_type"
SUBJECT = "subject"
DEVICES = "devices"
SURVEY = "survey"

VALID_PROJECT_DATA = {PROJECT_NAME: "clinic5 test project"}

CLINIC_PROJECT_DATA = {PROJECT_NAME: "clinic5 test project project ", GEN_RANDOM: True,
                       PROJECT_BACKGROUND: "This project is created by functional automation suite.",
                       PROJECT_TYPE: "survey",
                       SUBJECT: "clinic",
                       REPORT_TYPE: "other subject",
                       DEVICES: "sms",
                       PAGE_TITLE: "Projects - Overview"}

WATERPOINT_PROJECT_DATA = {PROJECT_NAME: "new project ", GEN_RANDOM: True,
                           PROJECT_BACKGROUND: "This project is created by functional automation suite.",
                           PROJECT_TYPE: "survey",
                           SUBJECT: "waterpoint",
                           REPORT_TYPE: "other subject",
                           DEVICES: "sms",
                           PAGE_TITLE: "Projects - Overview"}

VALID_SUMMARY_REPORT_DATA = {PROJECT_NAME: "Reporter Activities ", GEN_RANDOM: True,
                             PROJECT_BACKGROUND: "This project is created by functional automation suite.",
                             PROJECT_TYPE: SURVEY,
                             SUBJECT: "",
                             REPORT_TYPE: "data sender work",
                             DEVICES: "sms",
                             PAGE_TITLE: "Projects - Overview",
                             "warning_message":
                                 u"Translate or re-word this question if needed, but donʼt change its meaning. You can also delete the question if you donʼt need it for your project."}

LONG_DESCRIPTION_DATA = {PROJECT_NAME: "Reporter Activities ", GEN_RANDOM: True,
                         PROJECT_BACKGROUND: u"Exemple: Collecter les données émanant de 100 écoles primaires situées à Antananarivo, dans le but de faire passer le taux d'assiduité des enseignantsExemple: Collecter les données émanant de 100 écoles primaires situées à Antananarivo, dans le but de faire passer le taux d'assiduité des enseignants12345",
                         PROJECT_TYPE: "survey",
                         SUBJECT: "",
                         REPORT_TYPE: "data sender work",
                         DEVICES: "sms",
                         PAGE_TITLE: "Projects - Overview",
                         "warning_message":
                             u"Translate or re-word this question if needed, but donʼt change its meaning. You can also delete the question if you donʼt need it for your project."}

QUESTIONNAIRE_DATA = {QUESTIONNAIRE_CODE: u"cli005", GEN_RANDOM: True,
                      DEFAULT_QUESTION: {QUESTION: u"What is associatéd entity?", CODE: u"EID"},
                      QUESTIONS: [
                          {QUESTION: u"What is your namé?", CODE: u"q3", TYPE: WORD, LIMIT: LIMITED, MAX: u"10"},
                          {QUESTION: u"What is age öf father?", CODE: u"q4", TYPE: NUMBER, MIN: u"18", MAX: u"100"},
                          {QUESTION: u"What is réporting date?", CODE: u"q5", TYPE: DATE, DATE_FORMAT: DD_MM_YYYY},
                          {QUESTION: u"What is your blood group?", CODE: u"q6", TYPE: LIST_OF_CHOICES,
                           CHOICE: [u"O+", u"O-", u"AB", u"B+"],
                           ALLOWED_CHOICE: ONLY_ONE_ANSWER},
                          {QUESTION: u"What aré symptoms?", CODE: u"q7", TYPE: LIST_OF_CHOICES,
                           CHOICE: [u"Rapid weight loss", u"Dry cough", u"Pneumonia", u"Memory loss",
                                    u"Neurological disorders "],
                           ALLOWED_CHOICE: MULTIPLE_ANSWERS},
                          {QUESTION: u"What is the GPS codé for clinic", CODE: u"q8", TYPE: GEO},
                          {QUESTION: "What kink of car to you want?", CODE: "WB", TYPE: LIST_OF_CHOICES,
                           CHOICE: ["Alpha romeo", "BMW", "Citroen", "DAF", "EXCALIBUR", "FIAT", "GMC", "Hummer",
                                    "INFINITI", "JAGUAR", "KIA", "LEXUS", "MAHINDRA", "NISSAN", "OPEL", "PORSCHE",
                                    "Q5 audi", "ROVER", "SEAT", "TALBOT", "UMM", "VOLVO", "WESTFIELD", "X5 BM",
                                    "Yaris toyota", "Z06 Corvette", "1 Audi", "1 BUGATTI", "1 Cadillac", "1 DATSUN",
                                    "1 Eclipse Mazda", "1 Ford", "1 GUMPERT", "1 HONDA", "1 ISUZU", "1 JEEP",
                                    "1 KTM",
                                    "1 LANCIA", "1 Mercedes", "1 Navigator LINCOLN", "1 OLDSMOBILE", "1 Peugeot",
                                    "1 Quattro audi", "1 Renault", "1 Smart", "1 Toyota", "1 Uno fiat",
                                    "1 VolksWagen", "1 Willys", "1 Xantia citroen", "1 Yeti Skoda", "1 Zeta Lancia",
                                    "2 Austin", "2 Bellier", "2 Chevrolet", "2 Datsun", "2 Elandra hyundai",
                                    "2 Fisker", "2 Grecav", "2 Hyundai"],
                           ALLOWED_CHOICE: MULTIPLE_ANSWERS}
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
REDISTRIBUTE_QUESTIONNAIRE_MSG = u'You have made changes to your Questionnaire.\n\nPlease make sure your Data Senders have the latest version:\nSMS: Print and distribute the updated SMS Questionnaire\nSmartphone: Remind them to download the updated version of the Questionnaire\nWeb: No action needed. We will display the updated version of the Registration Form automatically'

WATERPOINT_QUESTIONNAIRE_DATA = {QUESTIONNAIRE_CODE: "WPS", GEN_RANDOM: True,
                                 DEFAULT_QUESTION: {QUESTION: "What are you reporting on?", CODE: "WID"},
                                 QUESTIONS: [{QUESTION: "Water Level", CODE: "WL", TYPE: NUMBER, MIN: "1", MAX: "10"},
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

