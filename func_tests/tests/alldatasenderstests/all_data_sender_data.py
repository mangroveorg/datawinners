# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from datawinners.messageprovider.tests.test_message_handler import THANKS
from framework.utils.common_utils import random_number, random_string, generate_random_email_id
from testdata.test_data import url
from testdata.constants import *


ASSOCIATE_SUCCESS_TEXT = "Data Senders associated Successfully. Please Wait...."
DISSOCIATE_SUCCESS_TEXT = "Data Senders dissociated Successfully. Please Wait...."
ERROR_MSG_WITHOUT_SELECTING_DS = u"Please select atleast 1 data sender"
DELETE_SUCCESS_TEXT = "Data Sender(s) successfully deleted."
SMS_ERROR_MESSAGE = "Your telephone number is not yet registered in our system. Please contact your supervisor."
REGISTRATION_SUCCESS_MESSAGE_TEXT = "Registration successful. ID is: rep"
ASSOCIATE_DATA_SENDER = {PROJECT_NAME: "clinic test project1",
                         UID: "rep1",
                         MOBILE_NUMBER: "1234567890"}

DISSOCIATE_DATA_SENDER = {PROJECT_NAME: "clinic test project1",
                          UID: "rep1",
                          MOBILE_NUMBER: "1234567890"}

DELETE_DATA_SENDER = {PROJECT_NAME: "clinic test project1",
                      UID: u"rep8",
                      MOBILE_NUMBER: "919049008976"}

ERROR_MSG_FOR_NOT_SELECTING_PROJECT = "Please select atleast 1 Project"

# ASSOCIATE_DS_WITHOUT_SELECTING_PROJECT = {UID: "rep2", ERROR_MSG: "Please select atleast 1 Project"}

DISSOCIATE_DS_WITHOUT_SELECTING_DS = {PROJECT_NAME: "clinic test project1", ERROR_MSG: ERROR_MSG_WITHOUT_SELECTING_DS}

ASSOCIATE_DS_WITHOUT_SELECTING_DS = {PROJECT_NAME: "clinic test project1", ERROR_MSG: ERROR_MSG_WITHOUT_SELECTING_DS}

DELETE_DS_WITHOUT_SELECTING_DS = {PROJECT_NAME: "clinic test project1", ERROR_MSG: ERROR_MSG_WITHOUT_SELECTING_DS}

VALID_SMS = {SENDER: "919049008976",
             RECEIVER: '919880734937',
             SMS: "cli001 .EID cid003 .NA Mr. Pitt .FA 77 .RD 12.03.2007 .BG b .SY ade .GPS 27.178057 -78.007789 .RM ac",
             SUCCESS_MESSAGE: THANKS}#+ u" EID: cid003 NA: Mr. Pitt FA: 77 RD: 12.03.2007 BG: O- SY: Rapid weight loss,Memory loss,Neurological disorders GPS: 27.178057, -78.007789 RM: Hivid,Vidéx EC"}

VALID_DATA = {NAME: "ReRegistered",
              MOBILE_NUMBER: "919049008976",
              COMMUNE: "MAHAVELO,AMBOTAKA,MANAKARA ATSIMO,VATOVAVY FITOVINANY",
              GPS: "-21.7622088847 48.0690991394",
              SUCCESS_MSG: "Registration successful. ID is: rep"}

VALID_DATASENDER_WITHOUT_WEB_ACCESS = {NAME: "aaa Kimi",
                                       MOBILE_NUMBER: random_number(9),
                                       EMAIL_ADDRESS: generate_random_email_id(),
                                       COMMUNE: "MAHAVELO,AMBOTAKA,MANAKARA ATSIMO,VATOVAVY FITOVINANY",
                                       GPS: "-21.7622088847 48.0690991394",
                                       SUCCESS_MSG: "Registration successful. ID is: rep"}

DATA_SENDER_TO_DELETE = {NAME: "ALLDSDelete",
                         MOBILE_NUMBER: random_number(9),
                         COMMUNE: "MAHAVELO,AMBOTAKA,MANAKARA ATSIMO,VATOVAVY FITOVINANY",
                         GPS: "-21.7622088847 48.0690991394",
                         SUCCESS_MSG: "Registration successful. ID is: rep"}

DATA_SENDER_FOR_MULTIPLE_DELETE = {NAME: "ALLDSDelete",
                                   MOBILE_NUMBER: random_number(9),
                                   COMMUNE: "MAHAVELO,AMBOTAKA,MANAKARA ATSIMO,VATOVAVY FITOVINANY",
                                   GPS: "-21.7622088847 48.0690991394",
                                   SUCCESS_MSG: "Registration successful. ID is: rep"}

VALID_DATASENDER_WITH_WEB_ACCESS = {NAME: "aaa Mickey Duck",
                                    MOBILE_NUMBER: random_number(9),
                                    COMMUNE: "MAHAVELO,AMBOTAKA,MANAKARA ATSIMO,VATOVAVY FITOVINANY",
                                    EMAIL_ADDRESS: "mIcKeY",
                                    GPS: "-21.7622088847 48.0690991394",
                                    SUCCESS_MSG: "Registration successful. ID is: rep"}

EDITED_DATA_SENDER = {NAME: "aaa Mickey Goose",
                      MOBILE_NUMBER: random_number(9),
                      COMMUNE: "Pakistan",
                      EMAIL_ADDRESS: "goose",
                      GPS: "3.33, 1.11",
                      SUCCESS_MSG: "Your changes have been saved."}

INVALID_MOBILE_NUMBER_DATA = {NAME: "ReRegistered",
                              MOBILE_NUMBER: "abcdefgh",
                              COMMUNE: "MAHAVELO,AMBOTAKA,MANAKARA ATSIMO,VATOVAVY FITOVINANY",
                              GPS: "-21.7622088847 48.0690991394"}

ALL_DS_TO_DELETE_ARE_USER_MSG = u'You cannot delete the following Data Senders as they are DataWinners users:'
NOTIFICATION_WHILE_DELETING_USER = "Note, the following Data Senders will not be deleted as they are DataWinners users"

ALL_USERS_URL = url("/account/users/")
TITLE = "title"
FIRST_NAME = "full_name"
USERNAME = "username"
MOBILE_PHONE = "mobile_phone"

NEW_USER_DATA = {
    TITLE: "Developer",
    FIRST_NAME: "AllDSDelete user",
    USERNAME: random_string(4) + "@mailinator.com",
    MOBILE_PHONE: random_number(9)
}


QUESTIONNAIRE_CODE = "questionnaire_code"
GEN_RANDOM = "gen_random"
DEFAULT_QUESTION = "default_question"
QUESTION = "question"
QUESTIONS = "questions"
CODE = "code"
TYPE = "type"
DATE = "date"
DD_MM_YYYY = "dd.mm.yyyy"
DATE_FORMAT = "date_format"

NEW_PROJECT = {PROJECT_NAME: "testing project", GEN_RANDOM: True}

QUESTIONNAIRE_DATA = {QUESTIONNAIRE_CODE: "WPS01", GEN_RANDOM: True,
                      QUESTIONS: [
                                {QUESTION: u"Date of report in DD.MM.YYY format", CODE: u"q3", TYPE: DATE,
                                   DATE_FORMAT: DD_MM_YYYY}]}


