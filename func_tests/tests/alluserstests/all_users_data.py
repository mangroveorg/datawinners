from tests.alldatasenderstests.all_data_sender_data import random_number, random_string


def url(path):
    full_path = "http://localhost:8000" + path
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
FIRST_NAME = "first_name"
LAST_NAME = "last_name"
USERNAME = "username"
MOBILE_PHONE = "mobile_phone"

NEW_USER_DATA = {
    TITLE: "Developer",
    FIRST_NAME: "kimi",
    LAST_NAME: "Raikonan",
    USERNAME: random_string(4)+"@mailinator.com",
    MOBILE_PHONE: random_number()
}
