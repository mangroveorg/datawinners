# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

ACTIVATE = "activate"
CANCEL = "cancel"


def url(path):
    full_path = "http://localhost:8000" + path
    if not full_path.endswith("/"):
        full_path += "/"
    return full_path


DATA_WINNER_HOME_PAGE = "/home"
DATA_WINNER_LOGIN_PAGE = url("/login")
DATASENDER_HOME_PAGE = url("/alldata")
LOGOUT = url('/logout')
DATA_WINNER_DASHBOARD_PAGE = url("/dashboard")
DATA_WINNER_REGISTER_PAGE = url("/register")
DATA_WINNER_REGISTER_TRIAL_PAGE = url("/register/trial")
DATA_WINNER_SMS_TESTER_PAGE = url("/smstester")
DATA_WINNER_SUBMISSION_LOG_PAGE = url("/project/results/cli002/")
DATA_WINNER_ADD_SUBJECT = url("/entity/subject/create/")
DATA_WINNER_ADD_SUBJECT_WATERPOINT = url("/entity/subject/create/waterpoint")
DATA_WINNER_ALL_SUBJECT = url("/entity/subjects/")
DATA_WINNER_ACTIVATE_ACCOUNT = url("/activate/")
DATA_WINNER_CREATE_DATA_SENDERS = url("/entity/datasender/create")
DATA_WINNER_HOMEPAGE = url("/home/")
DATA_WINNER_EN_PRICING_PAGE = url("/en/pricing/")
DATA_WINNER_REGISTRATION_COMPLETE_PAGE = url("/registration_complete#")
DATA_WINNER_TRIAL_ACCOUNT_EXPIRED_PAGE = url("/trial/expired/")
DATA_WINNER_ALL_DATA_SENDERS_PAGE = url("/entity/datasenders/")
DATA_WINNER_USER_ACTIVITY_LOG_PAGE = url("/useractivity/log/")
