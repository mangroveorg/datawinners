def url(path):
    full_path = "http://localhost:8000" + path
    if not full_path.endswith("/"):
        full_path += "/"
    return full_path
ALL_USERS_URL = url("/account/users/")
DELETE = "delete"
SELECT_ATLEAST_1_USER_MSG = u'Please select atleast 1 user'
ADMIN_CANT_BE_DELETED = u"Your organization's account Administrator Tester Pune cannot be deleted"
SMS_SUBMISSION_SUCCESS_MSG = u'Thank you Mino Rakoto. We received'
SUCCESSFULLY_DELETED_USER_MSG = u"User(s) successfully deleted."
N_A_TEXT = "N/A"