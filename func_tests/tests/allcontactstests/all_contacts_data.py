from framework.utils.common_utils import random_number, by_xpath
from testdata.constants import NAME, MOBILE_NUMBER, COMMUNE, EMAIL_ADDRESS, GPS, SUCCESS_MSG


VALID_CONTACTS_WITH_WEB_ACCESS = {
    MOBILE_NUMBER: random_number(9),
    SUCCESS_MSG: "Registration successful. ID is: rep"
}
