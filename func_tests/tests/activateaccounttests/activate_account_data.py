from framework.utils.common_utils import random_number
from testdata.constants import *


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

VALID_DATASENDER = {
                    NAME: "aaa Mickey Duck",
                    MOBILE_NUMBER: random_number(9),
                    COMMUNE: "MAHAVELO,AMBOTAKA,MANAKARA ATSIMO,VATOVAVY FITOVINANY",
                    EMAIL_ADDRESS: "mIcKeY",
                    GPS: "-21.7622088847 48.0690991394",
                    SUCCESS_MSG: "Your contact(s) have been added. ID is: rep"
                   }
