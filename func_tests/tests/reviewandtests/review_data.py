# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8


##Variables
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
PROJECT_PROFILE = "project_profile"
SUBJECT_DETAILS = "subject_details"
SUBJECT_COUNT = "subject_count"
DATA_SENDER_COUNT = "data_sender_count"
QUESTIONNAIRE = "questionnaire"
REMINDERS = "reminders"
DEADLINE = "deadline"
FREQUENCY = "frequency"
TYPE = "type"
WEEK = "Week"
DAY = "day"
WEEK_DAY = [' ', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
SAME_WEEK = "Same week"
EXAMPLE_TEXT = "example_text"
MESSAGE = "message"
BEFORE_DEADLINE = u"before_deadline"
REMINDER_DEADLINE = "reminder_mode"
WHOM_TO_SEND = "whom_to_send"
ALL = "all"

VALID_DATA = {PROJECT_PROFILE: {PROJECT_NAME: "clinic5 test project",
                                PROJECT_BACKGROUND: "This project is for automation",
                                PROJECT_TYPE: SURVEY,
                                DEVICES: "sms"},
              SUBJECT_DETAILS: {SUBJECT: "clinic"},
              DATA_SENDER_COUNT: "3",
              QUESTIONNAIRE: [u"What is associatéd entity?", u"What is your namé?", u"What is age öf father?",
                              u"What is réporting date?", u"What is your blood group?", u"What aré symptoms?",
                              u"What is the GPS codé for clinic"],
              REMINDERS: "disabled"
}
DEADLINE_FIRST_DAY_OF_SAME_WEEK_NEW_PROJECT = {PROJECT_NAME: "reminder project",
                                               DEADLINE: {FREQUENCY: WEEK, DAY: WEEK_DAY[1], TYPE: SAME_WEEK,
                                                          EXAMPLE_TEXT: "Example: Monday of the reporting week"},
                                               REMINDERS: {DAY: 1,
                                                           MESSAGE: u"One day remaining, please submit the data",
                                                           REMINDER_DEADLINE: BEFORE_DEADLINE},
                                               WHOM_TO_SEND: ALL}

VALID_PROJECT_DATA = {PROJECT_NAME: "Review Reporter Activities ", GEN_RANDOM: True,
                      PROJECT_BACKGROUND: "This project is created by functional automation suite.",
                      PROJECT_TYPE: SURVEY,
                      SUBJECT: "",
                      REPORT_TYPE: OTHER_SUBJECT,
                      DEVICES: "sms",
                      PAGE_TITLE: "Projects - Overview"}

REMINDER_PROJECT_DATA = {PROJECT_NAME: "reminder project", GEN_RANDOM: False,
                       PROJECT_BACKGROUND: "This project is created by functional automation suite.",
                       PROJECT_TYPE: "survey",
                       SUBJECT: "clinic",
                       REPORT_TYPE: "other subject",
                       DEVICES: "sms",
                       PAGE_TITLE: "Projects - Overview"}

CODE = "code"
TYPE = "type"
MIN = "min"
MAX = "max"
NUMBER = "number"
QUESTION_NAME = "question"

QUESTION = {QUESTION_NAME: "How many grades did you get last year?", CODE: "GRADES", TYPE: NUMBER, MIN: "1", MAX: "100"}

NAME = "name"
MOBILE_NUMBER = "mobile_number"
COMMUNE = "commune"
GPS = "gps"
WEB_CHANNEL = False

VALID_DATA_FOR_ADDING_DATASENDER = {NAME: "Mickey",
                                    MOBILE_NUMBER: "98865431111",
                                    COMMUNE: "MAHAVELO,AMBOTAKA,MANAKARA ATSIMO,VATOVAVY FITOVINANY",
                                    GPS: "-21.7622088847 48.0690991394"}
