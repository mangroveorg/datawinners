# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

##Variables
from framework.utils.common_utils import random_number, random_string
from testdata.constants import NAME, MOBILE_NUMBER, COMMUNE, EMAIL_ADDRESS, GPS, SUCCESS_MSG, SENDER, RECEIVER, SMS, SUCCESS_MESSAGE
from tests.addsubjecttests.add_subject_data import *

SMS_SUBMISSION = "sms"
UNIQUE_VALUE = "unique_value"
FAILURE_MSG = "failure_msg"

PROJECT_NAME = "clinic2 test project"

SMS_DATA_LOG = {SMS_SUBMISSION: "Success No cid005 Mr. Tessy 58 17.05.2011 O- Rapid weight loss, Memory loss, Neurological disorders 27.178057 -78.007789",
                UNIQUE_VALUE: "Mr. Tessy"}

PAGE_TITLE_IN_FRENCH = "Journal de Soumission"
FIRST_PROJECT_NAME = "clinic test project1"
DELETE_SUBMISSION_WARNING_MESSAGE = u'Your Submission(s) will be moved to Deleted Submissions.\nThis action cannot be undone.\n\nAre you sure you want to continue?'
EXPECTED_FA_LIST = ['89.0', '77', '77', '89.0', '77', '58', '27', '58', '98', '37', '28', '78', '28', '45', '56', '89', '88', '88', '36', '69', '45', '91', '43', '32', '35']

EXPECTED_FA_SORTED = ['24', '27', '28', '28', '30', '32', '34', '34', '34', '34', '34', '35', '36', '37', '37', '38', '38', '38', '43', '45', '45', '45', '47', '47', '48']

MOBILE_NUMBER_RANDOM = random_number(9)

DATASENDER_DETAILS = {NAME: "Dookudu",
                      MOBILE_NUMBER: MOBILE_NUMBER_RANDOM,
                      COMMUNE: "MAHAVELO,AMBOTAKA,MANAKARA ATSIMO,VATOVAVY FITOVINANY",
                      EMAIL_ADDRESS: random_string(5)+'@'+random_string(3)+'.com',
                      GPS: "-21.7622088847 48.0690991394",
                      SUCCESS_MSG: "Registration successful. ID is: rep"}

VALID_DATA = {SENDER: MOBILE_NUMBER_RANDOM,
              RECEIVER: '919880734937',
              SMS: "cli001 .EID cid003 .NA Mr. Tessy .FA 38 .RD 17.01.2012 .BG b .SY ade .GPS 27.178057 -78.007789 .RM a",
              SUCCESS_MESSAGE: "Thank you"}

EDITED_DATASENDER_DETAILS = {NAME: "edited Dookudu",
                      MOBILE_NUMBER: MOBILE_NUMBER_RANDOM,
                      COMMUNE: "MAHAVELO,AMBOTAKA,MANAKARA ATSIMO,VATOVAVY FITOVINANY",
                      EMAIL_ADDRESS: random_string(5)+'@'+random_string(3)+'.com',
                      GPS: "-21.7622088847 48.0690991394",
                      SUCCESS_MSG: "Registration successful. ID is: rep"}

MOBILE_NUMBER_FOR_SUBJECT = random_number(9)

VALID_DATA_FOR_EDIT = {ENTITY_TYPE: "Clinic",
                       SUB_UNIQUE_ID: None,
                       SUB_FIRST_NAME: "clinic FT",
                       SUB_LAST_NAME: "Test2",
                       LOCATION: "Monodovas",
                       GPS: "47.0 28.0",
                       MOBILE_NUMBER: MOBILE_NUMBER_FOR_SUBJECT,
                       SUCCESS_MESSAGE: "Your changes have been saved."}


VALID_DATA_FOR_SUBJECT = {ENTITY_TYPE: "Clinic",
                          SUB_UNIQUE_ID: None,
                          SUB_FIRST_NAME: "Clinic FT",
                          SUB_LAST_NAME: "Test",
                          LOCATION: "Monodova",
                          GPS: "47.411631 28.369885",
                          MOBILE_NUMBER: MOBILE_NUMBER_FOR_SUBJECT,
                          SUCCESS_MESSAGE: "Successfully submitted. Unique identification number(ID) is: "}

VALID_SMS_FOR_EDIT_SUBJECT = {SENDER: '1234567890',
                               RECEIVER: '919880734937',
                               SMS: "cli001 .EID short_code .NA Mr. Tessy .FA 38 .RD 17.01.2012 .BG b .SY ade .GPS 27.178057 -78.007789 .RM a",
                               SUCCESS_MESSAGE: "Thank you"}

