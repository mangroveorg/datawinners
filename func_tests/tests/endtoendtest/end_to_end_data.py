# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from datawinners.messageprovider.tests.test_message_handler import THANKS

WELCOME_MESSAGE = 'message'
SUCCESS_MESSAGE = 'message'
ERROR_MESSAGE = 'message'

ORGANIZATION_NAME = 'organization_name'
ORGANIZATION_SECTOR = 'organization_sector'
ORGANIZATION_ADDRESS_LINE = 'organization_addressline'
ORGANIZATION_CITY = 'organization_city'
ORGANIZATION_STATE = 'organization_state'
ORGANIZATION_COUNTRY = 'organization_country'
ORGANIZATION_ZIPCODE = 'organization_zipcode'
ORGANIZATION_OFFICE_PHONE = 'organization_office_phone'
ORGANIZATION_WEBSITE = 'organization_website'
TITLE = 'title'
FIRST_NAME = 'first_name'
LAST_NAME = 'last_name'
EMAIL = 'email'
ADMIN_OFFICE_NUMBER = "admin_office_number"
ADMIN_MOBILE_NUMBER = "admin_mobile_number"
ADMIN_SKYPE_ID = "admin_skype_id"
REGISTRATION_PASSWORD = 'registration_password'
REGISTRATION_CONFIRM_PASSWORD = 'registration_confirm_password'

ACTIVATION_CODE = "activation_code"

USERNAME = 'username'
PASSWORD = 'password'

DATA_SENDER_NAME = "name"
MOBILE_NUMBER = "mobile_number"
COMMUNE = "commune"
GPS = "gps"

ENTITY_TYPE = "entity_type"
SHORT_NAME = "short_name"
AUTO_GENERATE = "auto_generate"
NAME = "name"
LOCATION = "location"
GEO_CODE = "geo_code"
MOBILE_NUMBER = "mobile_number"
DESCRIPTION = "description"

PROJECT_NAME = "project_name"
PROJECT_BACKGROUND = "project_background"
PROJECT_TYPE = "project_type"
REPORT_TYPE = "report_type"
SUBJECT = "subject"
DEVICES = "devices"
ERROR_MSG = "message"
PAGE_TITLE = "page_title"
GEN_RANDOM = "gen_random"

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
CHARACTER_REMAINING = "character_remaining"

PROJECT_PROFILE = "project_profile"
SUBJECT_DETAILS = "subject_details"
SUBJECT_COUNT = "subject_count"
DATA_SENDER_COUNT = "data_sender_count"
QUESTIONNAIRE = "questionnaire"
REMINDERS = "reminders"

SENDER = "from"
RECEIVER = "to"
SMS = "sms"
MESSAGE = "message"

RESPONSE_MESSAGE = "message"

SUCCESS_MESSAGE_TEXT = THANKS #+ " q1: wat1 q2: 11.10.2011 q3: 98 q4: 12.04.2011 q5: 04.2011 q6: 04.12.2011 q7: DARK YELLOW q8: Mr.Tessy q9: Aquificae,Bacteroids q10: 27.178057, -78.007789"

SMS_SUBMISSION = "sms"
UNIQUE_VALUE = "unique_value"

REGISTRATION_PASSWORD = "ngo001"
SUB_UNIQUE_ID = "sub_unique_id"
SUB_FIRST_NAME = "sub_first_name"
SUB_LAST_NAME = "sub_last_name"

#Registration Page Data for Successful Registration Page
REGISTRATION_DATA_FOR_SUCCESSFUL_REGISTRATION = {ORGANIZATION_NAME: "Automation NGO",
                                                 ORGANIZATION_SECTOR: "PublicHealth",
                                                 ORGANIZATION_ADDRESS_LINE: "Panchshil Tech Park, Near Don Bosco School, Yerwada",
                                                 ORGANIZATION_CITY: "Pune",
                                                 ORGANIZATION_STATE: "Maharashtra",
                                                 ORGANIZATION_COUNTRY: "IN",
                                                 ORGANIZATION_ZIPCODE: "411006",
                                                 ORGANIZATION_OFFICE_PHONE: "9876543210",
                                                 ORGANIZATION_WEBSITE: "http://ngo001.com",
                                                 TITLE: "Mr.",
                                                 FIRST_NAME: "Mickey",
                                                 LAST_NAME: "Jackson",
                                                 EMAIL: "ngo",
                                                 ADMIN_MOBILE_NUMBER: "23-45-678-567",
                                                 ADMIN_OFFICE_NUMBER: "23-45-678-567",
                                                 ADMIN_SKYPE_ID: "tty01",
                                                 REGISTRATION_PASSWORD: REGISTRATION_PASSWORD,
                                                 REGISTRATION_CONFIRM_PASSWORD: REGISTRATION_PASSWORD,
                                                 SUCCESS_MESSAGE: "You have successfully registered!!\nAn activation email has been sent to your email address. Please activate before login."}

VALID_ACTIVATION_DETAILS = {ACTIVATION_CODE: "",
                            SUCCESS_MESSAGE: "You have successfully activated your account"}

VALID_DATA_FOR_DATA_SENDER = {DATA_SENDER_NAME: "Donald Mouse",
                              MOBILE_NUMBER: "1234567890",
                              COMMUNE: "urbaine",
                              GPS: "48.955267  1.816013",
                              SUCCESS_MESSAGE: u"Registration successful. ID is: rep3."}

VALID_DATA_FOR_DATA_SENDER1 = {DATA_SENDER_NAME: "Donald Mouse",
                               MOBILE_NUMBER: "12345678901",
                               COMMUNE: "urbaine",
                               GPS: "48.955267  1.816013",
                               SUCCESS_MESSAGE: u"Registration successful. ID is: rep3."}

# valid entity data
VALID_SUBJECT_TYPE1 = {ENTITY_TYPE: "Waterpoint", SUCCESS_MESSAGE: "Entity definition successful"}
VALID_SUBJECT_TYPE2 = {ENTITY_TYPE: "Well", SUCCESS_MESSAGE: "Entity definition successful"}

VALID_DATA_FOR_SUBJECT = {ENTITY_TYPE: "waterpoint",
                          SUB_UNIQUE_ID: None,
                          SUB_FIRST_NAME: "Waterpoint Monodova",
                          SUB_LAST_NAME: "wat",
                          LOCATION: "Monodova",
                          GEO_CODE: "47.411631 28.369885",
                          MOBILE_NUMBER: "3456789012",
                          SUCCESS_MESSAGE: "Successfully submitted. Unique identification number(ID) is: wat1"}

VALID_DATA_FOR_PROJECT = {PROJECT_NAME: "Waterpoint morondava", GEN_RANDOM: True,
                          PROJECT_BACKGROUND: "This project is created by functional automation suite.",
                          PROJECT_TYPE: "survey",
                          SUBJECT: "waterpoint",
                          REPORT_TYPE: 'data sender work',
                          DEVICES: "sms",
                          PAGE_TITLE: "Subjects"}

VALID_DATA_FOR_SUBJECT_QUESTIONNAIRE = {PAGE_TITLE: "Questionnaire"}

VALID_DATA_FOR_DATA_SENDER_QUESTIONNAIRE = {PAGE_TITLE: "Reminders"}

VALID_DATA_FOR_REMINDER = {PAGE_TITLE: "Review & Test"}

QUESTIONNAIRE_DATA = {QUESTIONNAIRE_CODE: "WPS01", GEN_RANDOM: False,
                      DEFAULT_QUESTION: {QUESTION: "What are you reporting on?", CODE: "q1"},
                      QUESTIONS: [{QUESTION: u"Water Level", CODE: u"q3", TYPE: NUMBER, MIN: u"1", MAX: u"1000"},
                                  {QUESTION: u"Date of report in DD.MM.YYY format", CODE: u"q4", TYPE: DATE,
                                   DATE_FORMAT: DD_MM_YYYY},
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
                                  {QUESTION: u"Geo points of Well", CODE: u"q10", TYPE: GEO}],
                      CHARACTER_REMAINING: "82 / 160 characters used (1 SMS)",
                      PAGE_TITLE: "Data Senders"}

NEW_QUESTIONNAIRE_DATA = {QUESTIONS: [{QUESTION: "Water Level", CODE: "q3", TYPE: NUMBER, MIN: "100", MAX: "1000"},
                                      {QUESTION: "What is water point name?", CODE: "q11", TYPE: WORD, LIMIT: LIMITED,
                                       MAX: ""}],
                          CHARACTER_REMAINING: "83 / 160 characters used (1 SMS)",
                          PAGE_TITLE: "Data Senders"}

VALID_DATA_REVIEW_AND_TEST = {PROJECT_PROFILE: {PROJECT_NAME: "waterpoint morondava",
                                                PROJECT_BACKGROUND: "This project is created by functional automation suite.",
                                                #PROJECT_TYPE: "survey",
                                                #DEVICES: "sms,web"
},
                              SUBJECT_DETAILS: {SUBJECT: "waterpoint"},
                              DATA_SENDER_COUNT: "1",
                              QUESTIONNAIRE: [u'What are you reporting on?',
                                              u'What is the reporting period for the activity?', u'Water Level',
                                              u'Date of report in DD.MM.YYY format', u'Date of report in MM.YYY format',
                                              u'Date of report in MM.DD.YYY format', u'Color of Water',
                                              u'Water point admin name', u'Bacterias in water', u'Geo points of Well'],
                              REMINDERS: "disabled"
}

VALID_DATA_FOR_SMS_LIGHT_BOX = {
    SMS: "WPS01  wat1  11.10.2011  98  12.04.2011  04.2011  04.12.2011   c  Mr.Tessy  ab  27.178057,-78.007789",
    RESPONSE_MESSAGE: THANKS}# + " q1: wat1 q2: 11.10.2011 q3: 98 q4: 12.04.2011 q5: 04.2011 q6: 04.12.2011 q7: DARK YELLOW q8: Mr.Tessy q9: Aquificae,Bacteroids q10: 27.178057,-78.007789"}

VALID_DATA_FOR_SMS = {SENDER: "1234567890",
                      RECEIVER: "",
                      SMS: "WPS01 wat1 11.10.2011  98  12.04.2011  04.2011  04.12.2011   c  Mr.Tessy  ab  27.178057,-78.007789",
                      SUCCESS_MESSAGE: SUCCESS_MESSAGE_TEXT}

SMS_DATA_LOG = {
SMS_SUBMISSION: "Success No wat1 11.10.2011 98 12.04.2011 04.2011 04.12.2011 DARK YELLOW Mr.Tessy Aquificae, Bacteroids 27.178057,-78.007789",
UNIQUE_VALUE: "Mr.Tessy"}

NEW_VALID_DATA_FOR_SMS = {SENDER: "1234567890",
                          RECEIVER: "",
                          SMS: "WPS01  wat1  12.10.2011  98  12.04.2011  04.2011  04.12.2011   c  Mr.Jessy  ab  27.178057,-78.007789  Water_Point_1",
                          ERROR_MESSAGE: "Error. Incorrect answer for q3. Please resend entire message."}

NEW_SMS_DATA_LOG = {
    SMS_SUBMISSION: "Error Yes wat1 12.10.2011 98 12.04.2011 04.2011 04.12.2011 DARK YELLOW Mr.Jessy Aquificae, Bacteroids 27.178057,-78.007789 Water_Point_1",
    UNIQUE_VALUE: "Mr.Jessy"}

INVALID_DATA_FOR_DATA_SENDER = {DATA_SENDER_NAME: "Donald Mouse",
                                MOBILE_NUMBER: "",
                                COMMUNE: "urbaine",
                                GPS: "48.955267  1.816013",
                                SUCCESS_MESSAGE: u"Registration successful. ID is: rep3."}