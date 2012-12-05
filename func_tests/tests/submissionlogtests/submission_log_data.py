# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

##Variables
SMS_SUBMISSION = "sms"
UNIQUE_VALUE = "unique_value"
FAILURE_MSG = "failure_msg"

PROJECT_NAME = "clinic2 test project"

SMS_DATA_LOG = {SMS_SUBMISSION: "Success No cid005 Mr. Tessy 58 17.05.2011 O- Rapid weight loss, Memory loss, Neurological disorders 27.178057 -78.007789",
                UNIQUE_VALUE: "Mr. Tessy"}

EXCEED_WORD_LIMIT_LOG = {SMS_SUBMISSION: "Error Yes CID005 Mr. O'brain 58 17.05.2011 O- Rapid weight loss, Memory loss, Neurological disorders 27.178057 -78.007789",
                         UNIQUE_VALUE: "Mr. O'brain",
                         FAILURE_MSG: "Answer Mr. O'brain for question NA is longer than allowed."}

EXTRA_PLUS_IN_BTW_LOG = {SMS_SUBMISSION: "Success No cid002 Mr. Dessy 58 17.05.2011 O- Rapid weight loss, Memory loss, Neurological disorders 27.178057 -78.007789",
                         UNIQUE_VALUE: "Mr. Dessy"}

WITH_INVALID_GEO_CODE_FORMAT_LOG = {
    SMS_SUBMISSION: "Error Yes cid002 Mr. De`Melo 58 17.05.2011 O\+, O\- Rapid weight loss, Memory loss, Neurological disorders 127.178057 -78.007789 Hivid",
    UNIQUE_VALUE: "Mr. De`Melo",
    FAILURE_MSG: "Answer Mr. De`Melo for question NA is longer than allowed.,Answer ab for question BG contains more than one value.,The answer 127.178057 must be between -90 and 90"}
PAGE_TITLE_IN_FRENCH = "Journal de Soumission"
FIRST_PROJECT_NAME = "clinic test project"
DELETE_SUBMISSION_WARNING_MESSAGE = u'Your Submission(s) will be moved to Deleted Submissions. This action cannot be undone.\n\nAre you sure you want to continue?'