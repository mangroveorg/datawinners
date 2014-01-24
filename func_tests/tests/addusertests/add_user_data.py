from framework.utils.common_utils import random_number, random_string

TITLE = "title"
FIRST_NAME = "first_name"
LAST_NAME = "last_name"
USERNAME = "username"
MOBILE_PHONE = "mobile_phone"
ADD_USER_DATA = {
    TITLE: "Developer",
    FIRST_NAME: "Mino",
    LAST_NAME: "Rakoto",
    USERNAME: random_string(7)+"@mailinator.com",
    MOBILE_PHONE: random_number(9)
}
ADDED_USER_SUCCESS_MSG = u'User has been added successfully'
DASHBOARD_PAGE_TITLE = u'Dashboard'
DEFAULT_PASSWORD = "test123"