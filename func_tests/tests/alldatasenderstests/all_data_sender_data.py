# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8


##Variables
import random
from datawinners.messageprovider.tests.test_message_handler import THANKS


def random_string(length=6):
    return ''.join(random.sample('abcdefghijklmnopqrs', length))


def random_number(length=6):
    return ''.join(random.sample('1234567890', length))


NAME = "name"
MOBILE_NUMBER = "mobile_number"
LOCATION = "location"
GPS = "gps"
SUCCESS_MSG = "message"
ERROR_MSG = "message"
PROJECT_NAME = "project_name"
ASSOCIATE = "associate"
DISSOCIATE = "disassociate"
WEB_ACCESS = 'makewebuser'
UID = "uid"
DELETE = "delete"
EDIT = "edit"
SENDER = "from"
RECEIVER = "to"
SMS = "sms"
MESSAGE = "message"
COMMUNE = "commune"
SUCCESS_MESSAGE = "success_message"

ASSOCIATE_SUCCESS_TEXT = "Data Senders associated Successfully. Please Wait...."
DISSOCIATE_SUCCESS_TEXT = "Data Senders dissociated Successfully. Please Wait...."
ERROR_MSG_WITHOUT_SELECTING_DS = u"Please select atleast 1 data sender"
DELETE_SUCCESS_TEXT = "Data Sender(s) successfully deleted."
SMS_ERROR_MESSAGE = "Your telephone number is not yet registered in our system. Please contact your supervisor."

ASSOCIATE_DATA_SENDER = {PROJECT_NAME: "clinic test project1",
                         UID: "rep1",
                         MOBILE_NUMBER: "1234567890"}

DISSOCIATE_DATA_SENDER = {PROJECT_NAME: "clinic test project1",
                          UID: "rep1",
                          MOBILE_NUMBER: "1234567890"}

DELETE_DATA_SENDER = {PROJECT_NAME: "clinic test project1",
                      UID: u"rep8",
                      MOBILE_NUMBER: "919049008976"}

DISSOCIATE_DS_WITHOUT_SELECTING_PROJECT = {UID: "rep1", ERROR_MSG: "Please select atleast 1 Project"}

ASSOCIATE_DS_WITHOUT_SELECTING_PROJECT = {UID: "rep2", ERROR_MSG: "Please select atleast 1 Project"}

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

VALID_DATASENDER_WITHOUT_WEB_ACCESS = {NAME: "Kimi",
                                       MOBILE_NUMBER: random_number(6),
                                       COMMUNE: "MAHAVELO,AMBOTAKA,MANAKARA ATSIMO,VATOVAVY FITOVINANY",
                                       GPS: "-21.7622088847 48.0690991394",
                                       SUCCESS_MSG: "Registration successful. ID is: rep"}

EMAIL_ADDRESS = "email"

VALID_DATASENDER_WITH_EMAIL = {NAME: "Mickey Duck",
                               MOBILE_NUMBER: random_number(6),
                               COMMUNE: "MAHAVELO,AMBOTAKA,MANAKARA ATSIMO,VATOVAVY FITOVINANY",
                               EMAIL_ADDRESS: "mIcKeY",
                               GPS: "-21.7622088847 48.0690991394",
                               SUCCESS_MSG: "Registration successful. ID is: rep"}

INVALID_MOBILE_NUMBER_DATA = {NAME: "ReRegistered",
                              MOBILE_NUMBER: "abcdefgh",
                              COMMUNE: "MAHAVELO,AMBOTAKA,MANAKARA ATSIMO,VATOVAVY FITOVINANY",
                              GPS: "-21.7622088847 48.0690991394"}

DATA_SENDER_ID_WITH_WEB_ACCESS = "rep3"
DATA_SENDER_ID_WITHOUT_WEB_ACCESS = "rep5"


def generate_random_email_id():
    return random_string(5) + '@' + random_string(3) + '.com'


ALL_DS_TO_DELETE_ARE_USER_MSG = u'You cannot delete the following Data Senders as they are DataWinners users:'
NOTIFICATION_WHILE_DELETING_USER = "Note, the following Data Senders will not be deleted as they are DataWinners users"