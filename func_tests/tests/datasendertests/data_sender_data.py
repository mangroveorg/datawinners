from framework.utils.common_utils import random_number
from testdata.constants import MOBILE_NUMBER, SUCCESS_MSG

PAGE_TITLE = "Data Submission"

SECTION_TITLE = "Data Submission"

SUBJECT_TYPE = "Register a new clinic"


VALID_CONTACTS_WITH_WEB_ACCESS = {
    MOBILE_NUMBER: random_number(9),
    SUCCESS_MSG: "Registration successful. ID is: rep"
}
