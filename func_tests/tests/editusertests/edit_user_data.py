from framework.utils.common_utils import random_number, random_string

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