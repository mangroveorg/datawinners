# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8


USERNAME = 'username'
PASSWORD = 'password'
WELCOME_MESSAGE = 'message'
ERROR_MESSAGE = 'message'

# valid credentials
VALID_CREDENTIALS = {USERNAME: "tester150411@gmail.com",
                     PASSWORD: "tester150411",
                     WELCOME_MESSAGE: "Welcome Tester!"}

TRIAL_CREDENTIALS_VALIDATES = {USERNAME: "chinatwu2@gmail.com",
                     PASSWORD: "chinatwu",
                     WELCOME_MESSAGE: "Welcome Trial Organisation Owner!"}

TRIAL_CREDENTIALS_THREE = {USERNAME: "chinatwu3@gmail.com",
                     PASSWORD: "chinatwu",
                     WELCOME_MESSAGE: "Welcome Trial Organisation Owner!"}

DATA_SENDER_CREDENTIALS = {USERNAME: "datasender@test.com",
                           PASSWORD: "111111"}

# invalid format email id
INVALID_EMAIL_ID_FORMAT = {USERNAME: "com.invalid@mail",
                           PASSWORD: "nogo123",
                           ERROR_MESSAGE: "Please enter a correct email and password."}
# invalid password
INVALID_PASSWORD = {USERNAME: "nogo@mail.com",
                    PASSWORD: "nogo124",
                    ERROR_MESSAGE: "Please enter a correct email and password."}

# Login without entering Email Address
BLANK_EMAIL_ADDRESS = {USERNAME: "",
                       PASSWORD: "nogo123",
                       ERROR_MESSAGE: "Email This field is required."}

BLANK_PASSWORD = {USERNAME: "nogo@mail.com",
                  PASSWORD: "",
                  ERROR_MESSAGE: "Password This field is required."}

# blank username and password
UNACTIVATED_ACCOUNT_CREDENTIALS = {USERNAME: "tester@gmail.com",
                                   PASSWORD: "nogo123",
                                   ERROR_MESSAGE: "This account is inactive."}

# blank username and password
BLANK_CREDENTIALS = {USERNAME: "",
                     PASSWORD: "",
                     ERROR_MESSAGE: "Email This field is required.Password This field is required."}

EXPIRED_TRIAL_ACCOUNT = {USERNAME: "chinatwu@gmail.com",
                     PASSWORD: "chinatwu",
                     ERROR_MESSAGE: "Your DataWinners account have been deactivated. Subscribe to a monthly subscription or contact your Project Manager to reactivate the account."}

NIGERIA_ACCOUNT_CREDENTIAL = {USERNAME: "gerard@mailinator.com",
                     PASSWORD: "gerard",
                     WELCOME_MESSAGE: "Welcome Gerard!"}

DEACTIVATED_ACCOUNT_CREDENTIALS = {USERNAME: "deactivated@mailinator.com",
                                   PASSWORD: "deactivated",
                                   ERROR_MESSAGE: "Your account has been deactivated. Please contact the datawinners support at support@datawinners.com for reactivation of the account."}