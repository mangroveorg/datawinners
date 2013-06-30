# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8


EMAIL = 'email'
ACTIVATION_CODE = "activation_code"
SUCCESS_MESSAGE = 'message'
ERROR_MESSAGE = 'message'

# valid credentials
VALID_ACTIVATION_DETAILS = {ACTIVATION_CODE: "",
                            SUCCESS_MESSAGE: "You have successfully activated your account"}

INVALID_ACTIVATION_CODE = {ACTIVATION_CODE: "8ff48d7a0fc70919c5d0812283d021dbac660",
                           ERROR_MESSAGE: "Account activation failed"}
DS_ACTIVATION_URL = "/datasender/activate/%s-%s"
NEW_PASSWORD = "dstest!123"