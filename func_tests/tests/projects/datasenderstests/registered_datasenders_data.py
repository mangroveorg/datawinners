# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

##Variables
NAME = "name"
MOBILE_NUMBER = "mobile_number"
MOBILE_NUMBER_WITHOUT_HYPHENS = "mobile_number_without_hyphens"
COMMUNE = "commune"
GPS = "gps"
WEB_CHANNEL = False
EMAIL_ADDRESS = ""
SUCCESS_MSG = "message"
ERROR_MESSAGE = "error_message"

TITLE = "title"
MESSAGE = "message"
PROJECT_NAME = "project_name"
PROJECT_BACKGROUND = "project_background"
PROJECT_TYPE = "project_type"
REPORT_TYPE = "report_type"
SUBJECT = "subject"
DEVICES = "devices"
ERROR_MSG = "message"
PAGE_TITLE = "page_title"
GEN_RANDOM = "gen_random"
DATA_SENDER_WORK = "data sender work"
OTHER_SUBJECT = "other subject"
DEFAULT_QUESTION = "default_question"
GIVE_WEB_ACCESS = "makewebuser"

VALID_DATA_FOR_ADDING_DATASENDER = {NAME: "Mickey Duck",
                                    MOBILE_NUMBER: "98865432101",
                                    COMMUNE: "MAHAVELO,AMBOTAKA,MANAKARA ATSIMO,VATOVAVY FITOVINANY",
                                    GPS: "-21.7622088847 48.0690991394",
                                    SUCCESS_MSG: "Registration successful. ID is: rep"}

VALID_DATA = {PROJECT_NAME: u"clinic test project",
              PROJECT_BACKGROUND: u"This project is for automation",
              #PROJECT_TYPE: "survey",
              SUBJECT: u"clinic",
              REPORT_TYPE: OTHER_SUBJECT,
              #DEVICES: "sms"
}

ERROR_MSG_FOR_GIVING_WEB_ACCESS_WITHOUT_SELECTING_DATA_SENDER = "Please select atleast 1 data sender"

IMPORT_DATA_SENDER_TEMPLATE_FILENAME_EN = "DataWinners_ImportDataSenders.xls"
IMPORT_DATA_SENDER_TEMPLATE_FILENAME_FR = "DataWinners_ImporterLesEnvoyeursDeDonnees.xls"

SUCCESS_MSG_ADDED_DS = u"Registration successful. ID is: abcd93843."
UNIQUE_ID = "abcd93843"

VALID_DATASENDER_DATA = {NAME: "Donald Duck",
                         MOBILE_NUMBER: "9876-543-2102",
                         MOBILE_NUMBER_WITHOUT_HYPHENS: "98765432102",
                         COMMUNE: "MAHAVELO,AMBOTAKA,MANAKARA ATSIMO,VATOVAVY FITOVINANY",
                         GPS: "-21.7622088847 48.0690991394",
                         SUCCESS_MSG: "Registration successful. ID is: rep"}
VALID_EDIT_DATASENDER_DATA = {NAME: "EDIT Mickey Duck",
                              MOBILE_NUMBER: "9876-543-2108",
                              COMMUNE: "PUNE",
                              GPS: "",
                              SUCCESS_MSG: "Your changes have been saved."}
VALID_DATASENDER_DATA_FOR_DUPLICATE_UNIQUE_ID = {NAME: "Mickey Mouse",
                                                 MOBILE_NUMBER: "9876-543-2103",
                                                 MOBILE_NUMBER_WITHOUT_HYPHENS: "98765432103",
                                                 COMMUNE: "MAHAVELO,AMBOTAKA,MANAKARA ATSIMO,VATOVAVY FITOVINANY",
                                                 GPS: "-21.7622088847 48.0690991394",
                                                 ERROR_MSG: "Data Sender with Unique Identification Number"}
CLINIC_PROJECT1_NAME = "clinic test project"