from framework.utils.common_utils import random_number, random_string
from testdata.test_data import get_test_port, get_target_test_host, get_target_test_scheme


def url(path):
    full_path = get_target_test_scheme() + "://" + get_target_test_host() + ":" + get_test_port() + path
    if not full_path.endswith("/"):
        full_path += "/"
    return full_path
ALL_USERS_URL = url("/account/users/")
DELETE = "delete"
SELECT_ATLEAST_1_USER_MSG = u'Please select at least 1 user'
ADMIN_CANT_BE_DELETED = u"Your organization's account Administrator Tester Pune cannot be deleted"
SUCCESSFULLY_DELETED_USER_MSG = u"User(s) successfully deleted."
N_A_TEXT = "N/A"
NA_DATASENDER_TEXT = "Deleted Data Sender"
NA_USER_TEXT = "Deleted User"
TITLE = "title"
NAME = "full_name"
USERNAME = "username"
MOBILE_PHONE = "mobile_phone"

NEW_USER_DATA = {
    TITLE: "Developer",
    NAME: "kimi Raikonan",
    USERNAME: random_string(4)+"@mailinator.com",
    MOBILE_PHONE: random_number()
}

EDIT_USER_DATA = {
    TITLE: "Developer",
    NAME: "testUser",
    USERNAME: random_string(4)+"@mailinator.com",
    MOBILE_PHONE: random_number()
}

NAME_COLUMN = "//div[@id='users_list']/table/tbody/tr/td[3][contains(text(),'%s')]//parent::tr/td[2]"

