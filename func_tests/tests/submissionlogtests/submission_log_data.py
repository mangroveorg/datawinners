# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

##Variables
from datetime import datetime, timedelta
from framework.utils.common_utils import random_number, random_string
from tests.addsubjecttests.add_subject_data import ENTITY_TYPE, SUB_UNIQUE_ID, SUB_FIRST_NAME, SUB_LAST_NAME, LOCATION, GEO_CODE
from testdata.constants import NAME, MOBILE_NUMBER, COMMUNE, EMAIL_ADDRESS, GPS, SUCCESS_MSG, SENDER, RECEIVER, SMS, SUCCESS_MESSAGE

SMS_SUBMISSION = "sms"
UNIQUE_VALUE = "unique_value"
FAILURE_MSG = "failure_msg"

PROJECT_NAME = "clinic2 test project"
SUBJECT_NAME = "subject_name"
SHORT_CODE = "short_code"
LAST_NAME = "last_name"

SMS_DATA_LOG = {
    SMS_SUBMISSION: "Success No cid005 Mr. Tessy 58 17.05.2011 O- Rapid weight loss, Memory loss, Neurological disorders 27.178057 -78.007789",
    UNIQUE_VALUE: "Mr. Tessy"}

PAGE_TITLE_IN_FRENCH = "Journal de Soumission"
FIRST_PROJECT_NAME = "clinic test project1"
DELETE_SUBMISSION_WARNING_MESSAGE = u'Your Submission(s) will be moved to Deleted Submissions.\nThis action cannot be undone.\n\nAre you sure you want to continue?'
EXPECTED_FA_LIST = ['89.0', '77', '77', '89.0', '77', '58', '27', '58', '98', '37', '28', '78', '28', '45', '56', '89',
                    '88', '88', '36', '69', '45', '91', '43', '32', '35']

EXPECTED_FA_SORTED = ['24', '27', '28', '28', '30', '32', '34', '34', '34', '34', '34', '35', '36', '37', '37', '38',
                      '38', '38', '43', '45', '45', '45', '47', '47', '48']

MOBILE_NUMBER_RANDOM = random_number(9)

DATASENDER_DETAILS = {NAME: "Dookudu",
                      MOBILE_NUMBER: MOBILE_NUMBER_RANDOM,
                      COMMUNE: "MAHAVELO,AMBOTAKA,MANAKARA ATSIMO,VATOVAVY FITOVINANY",
                      EMAIL_ADDRESS: random_string(5) + '@' + random_string(3) + '.com',
                      GPS: "-21.7622088847 48.0690991394",
                      SUCCESS_MSG: "Registration successful. ID is: rep"}

VALID_DATA = {SENDER: MOBILE_NUMBER_RANDOM,
              RECEIVER: '919880734937',
              SMS: "cli001 .EID cid003 .NA Mr. Tessy .FA 38 .RD 17.01.2012 .BG b .SY ade .GPS 27.178057 -78.007789 .RM a",
              SUCCESS_MESSAGE: "Thank you"}

EDITED_DATASENDER_DETAILS = {NAME: "edited Dookudu",
                             MOBILE_NUMBER: MOBILE_NUMBER_RANDOM,
                             COMMUNE: "MAHAVELO,AMBOTAKA,MANAKARA ATSIMO,VATOVAVY FITOVINANY",
                             EMAIL_ADDRESS: random_string(5) + '@' + random_string(3) + '.com',
                             GPS: "-21.7622088847 48.0690991394",
                             SUCCESS_MSG: "Registration successful. ID is: rep"}

MOBILE_NUMBER_FOR_SUBJECT = random_number(9)

VALID_DATA_FOR_EDIT = {ENTITY_TYPE: "Clinic",
                       SUB_UNIQUE_ID: None,
                       SUB_FIRST_NAME: "clinic FT",
                       SUB_LAST_NAME: "Test2",
                       LOCATION: "Monodovas",
                       GEO_CODE: "47.0 28.0",
                       MOBILE_NUMBER: MOBILE_NUMBER_FOR_SUBJECT,
                       SUCCESS_MESSAGE: "Your changes have been saved."}

VALID_DATA_FOR_SUBJECT = {ENTITY_TYPE: "Clinic",
                          SUB_UNIQUE_ID: None,
                          SUB_FIRST_NAME: "Clinic FT",
                          SUB_LAST_NAME: "Test",
                          LOCATION: "Monodova",
                          GEO_CODE: "47.411631 28.369885",
                          MOBILE_NUMBER: MOBILE_NUMBER_FOR_SUBJECT,
                          SUCCESS_MESSAGE: "Successfully submitted. Unique identification number(ID) is: "}

VALID_SMS_FOR_EDIT_SUBJECT = {SENDER: '1234567890',
                              RECEIVER: '919880734937',
                              SMS: "cli001 .EID short_code .NA Mr. Tessy .FA 38 .RD 17.01.2012 .BG b .SY ade .GPS 27.178057 -78.007789 .RM a",
                              SUCCESS_MESSAGE: "Thank you"}

QCODE = "qcode"
ANSWER = 'answer'
TYPE = "type"
SELECT = "select"
TEXT = "text"
CHECKBOX = "checkbox"

VALID_SUBMISSION = [
    {QCODE: 'EID', ANSWER: 'Indore Clinic', TYPE: SELECT},
    {QCODE: 'NA', ANSWER: 'My name', TYPE: TEXT},
    {QCODE: 'FA', ANSWER: '90', TYPE: TEXT},
    {QCODE: 'RD', ANSWER: '09.12.2013', TYPE: TEXT},
    {QCODE: 'BG', ANSWER: 'O-', TYPE: SELECT},
    {QCODE: 'SY', ANSWER: ['a', 'c'], TYPE: CHECKBOX},
    {QCODE: 'GPS', ANSWER: '-18.1324 27.6547', TYPE: TEXT},
    {QCODE: 'RM', ANSWER: ['c'], TYPE: CHECKBOX},
]

SMS_REGISTER_SUBJECT = {SENDER: '1234567890',
                        RECEIVER: '919880734937',
                        SMS: "cli first test_subject loc 2,2 1231231213 cid111",
                        SUCCESS_MESSAGE: "Thank you"}

SUBJECT_DATA = {
    LAST_NAME: 'test_subject',
    SHORT_CODE: 'cid111'
}

SMS_WEB_SUBMISSION = {SENDER: '1234123413',
                      RECEIVER: '919880734937',
                      SMS: "cli001 .EID cid111 .NA Mr. Tessy .FA 38 .RD 17.01.2012 .BG b .SY ade .GPS 27.178057 -78.007789 .RM a",
                      SUCCESS_MESSAGE: "Thank you"}

GEN_RANDOM = "gen_random"
PROJECT_BACKGROUND = "project_background"
PROJECT_TYPE = "project_type"
SUBJECT = "subject"
REPORT_TYPE = "report_type"
DEVICES = "devices"
PAGE_TITLE = "page_title"

NEW_PROJECT_DATA = {PROJECT_NAME: "new project ", GEN_RANDOM: True,
                           PROJECT_BACKGROUND: "This project is created by functional automation suite.",
                           PROJECT_TYPE: "survey",
                           SUBJECT: "waterpoint",
                           REPORT_TYPE: "other subject",
                           DEVICES: "sms",
                           PAGE_TITLE: "Projects - Overview"}

def get_sms_data_with_questionnaire_code(questionnaire_code):
    return {SENDER: "919049008976",
            RECEIVER: '919880734937',
            SMS: questionnaire_code + " wp01 10.12.2013",
            'message': 'Thanks'}


def get_reporting_date_values():
    today = datetime.now()
    first_day_of_month = datetime(today.year, today.month, 1)
    previous_month = first_day_of_month - timedelta(days=1)
    first_day_of_year = datetime(today.year,1,1)
    dates = []
    for i in [today, first_day_of_month, previous_month, first_day_of_year]:
        dates.append(i.strftime('%d.%m.%Y'))
    return dates