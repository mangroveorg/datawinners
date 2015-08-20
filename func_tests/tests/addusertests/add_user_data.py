from framework.utils.common_utils import random_number, random_string

def generate_user():
    return {
        TITLE: "Developer",
        NAME: "Mino Rakoto",
        USERNAME: random_string(7)+"@mailinator.com",
        MOBILE_PHONE: random_number(9)
    }

def get_existing_username_user():
    return {
        TITLE: "DT",
        NAME: "Existing Username",
        USERNAME: "tester150411@gmail.com",
        MOBILE_PHONE: random_number(9)
    }

def generate_user_with_existing_phone_number():
    return {
        TITLE: "Developer",
        NAME: "Mino Rakoto",
        USERNAME: random_string(7)+"@mailinator.com",
        MOBILE_PHONE: 2619875
    }


TITLE = "title"
NAME = "full_name"
USERNAME = "username"
MOBILE_PHONE = "mobile_phone"
ADDED_USER_SUCCESS_MSG = u'User has been added successfully'
DASHBOARD_PAGE_TITLE = u'Dashboard'
DEFAULT_PASSWORD = "test123"