from framework.utils.common_utils import random_number, random_string
from tests.smstestertests.sms_tester_data import SENDER, RECEIVER, SMS, ERROR_MSG

def generate_user():
    return {
        TITLE: "Developer",
        NAME: "Mino Rakoto",
        USERNAME: random_string(7)+"@mailinator.com",
        MOBILE_PHONE: random_number(9)
    }

TITLE = "title"
NAME = "full_name"
USERNAME = "username"
MOBILE_PHONE = "mobile_phone"
USER_EDITED_SUCCESS_MESSAGE = u'User has been updated successfully'
DASHBOARD_PAGE_TITLE = u'Dashboard'
DEFAULT_PASSWORD = "test123"


SMS_TO_TEST_PERMISSION = {SENDER: "2619876",
                      RECEIVER: "919880734937",
                      SMS: "cli001 cli10 myname 28 25.12.2010 a ca 12.34,45.67 a",
                      ERROR_MSG: "Error. Incorrect answer for question 2. Please review printed Questionnaire and resend entire SMS."}
SUCCESS_MESSAGE = "Thank you Stefan. We received your SMS: Clinic(cli10); myname; 28; 25.12.2010; O+; Pneumonia,Rapid weight loss; 12.34, 45.67; Hivid"
ERROR_MESSAGE = "Error. You are not authorized to submit data for this Questionnaire. Please contact your supervisor."