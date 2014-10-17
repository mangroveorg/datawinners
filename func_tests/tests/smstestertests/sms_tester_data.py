# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8


##Variables
from datawinners.messageprovider.tests.test_message_handler import THANKS
from datawinners.tests.data import TRIAL_ACCOUNT_DATA_SENDER_MOBILE_NO
from framework.utils.common_utils import random_number

SENDER = "from"
RECEIVER = "to"
SMS = "sms"
ERROR_MSG = "message"
SUCCESS_MESSAGE = "message"
MESSAGE = "message"

SUCCESS_MESSAGE_TEXT = "Thank you Shweta for your data record. We successfully received your submission."

VALID_DATA = {SENDER: "1234567890",
              RECEIVER: "919880734937",
              SMS: "cli009 .EID cid003 .NA Mr. Tessy .FA 58 .RD 17.05.2011 .BG b .SY ade .GPS 27.178057  -78.007789 .RM ac",
              SUCCESS_MESSAGE: (THANKS % "Shweta") + " for Clinic Jabalpur Clinic (cid003)."}

VALID_DATA2 = {SENDER: "1234567890",
               RECEIVER: "919880734937",
               SMS: "cli002 .EID cid005 .NA Mr. Tessy .FA 58 .RD 17.05.2011 .BG b .SY ade .GPS 27.178057  -78.007789 .RM ac",
               SUCCESS_MESSAGE: THANKS}#+ " EID: cid005 NA: Mr. Tessy FA: 58 RD: 17.05.2011 BG: O- SY: Rapid weight loss,Memory loss,Neurological disorders GPS: 27.178057, -78.007789 RM: Hivid,Vidéx EC"}

EXCEED_NAME_LENGTH = {SENDER: "1234567891",
                      RECEIVER: "919880734937",
                      SMS: "cli009 .EID CID003 .NA Mr. O'brain .FA 58 .RD 17.05.2011 .BG b .SY ade .GPS 27.178057  -78.007789 .RM bc",
                      ERROR_MSG: "Error. Incorrect answer for question 2. Please review printed Questionnaire and resend entire SMS."}

EXCEED_NAME_LENGTH2 = {SENDER: "1234567890",
                       RECEIVER: "919880734937",
                       SMS: "cli002 .EID CID005 .NA Mr. O'brain .FA 58 .RD 17.05.2011 .BG b .SY ade .GPS 27.178057  -78.007789 .RM b",
                       ERROR_MSG: "Error. Incorrect answer for na. Please resend entire message."}

BLANK_FIELDS = {SENDER: "",
                RECEIVER: "",
                SMS: "",
                ERROR_MSG: "From * This field is required.To * This field is required.SMS * This field is required."}

EXTRA_PLUS_IN_BTW = {SENDER: "1234567890",
                     RECEIVER: "919880734937",
                     SMS: "cli002 .EID cid002 . .NA Mr. Dessy .FA 58 .. .RD 17.05.2011 .BG b .SY ade .  .GPS 27.178057  -78.007789 .RM ac",
                     ERROR_MSG: THANKS}#+ " cid002 NA: Mr. Dessy FA: 58 RD: 17.05.2011 BG: O- SY: Rapid weight loss,Memory loss,Neurological disorders GPS: 27.178057, -78.007789 RM: Hivid,Vidéx EC"}

PLUS_IN_THE_BEGINNING = {SENDER: "1234567890",
                         RECEIVER: "919880734937",
                         SMS: ". .cli002 .EID CID005 .NA Mr. Fessy .FA 58 .RD 17.05.2011 .BG b .SY ade .RM ac",
                         ERROR_MSG: "Error: SMS Incorrect. Please review printed questionnaire and resend entire SMS."}

UNREGISTERED_FROM_NUMBER = {SENDER: "123445567",
                            RECEIVER: "919880734937",
                            SMS: "cli002 .EID CID005 . .NA Mr. Kessy .FA 58 .RD 17.05.2011 .BG b .SY ade .GPS 27.178057  -78.007789 .RM ac",
                            ERROR_MSG: "Error. You are not authorized to submit data for this Questionnaire. Please contact your supervisor."}

REGISTER_DATA_SENDER = {SENDER: "1234567890",
                        RECEIVER: "919880734937",
                        SMS: "REG .t Reporter .m %s .L  Jaipur .g 26.917 75.817 .N Donald Duck" % random_number(9),
                        ERROR_MSG: u"Thank you Shweta. We registered your Reporter "}

REGISTER_DATA_SENDER_FROM_UNKNOWN_NUMBER = {SENDER: "12345678453",
                                            RECEIVER: "919880734937",
                                            SMS: "REG .t Reporter .m 0123456789 .L   Jaipur .g 26.917 75.817 .N Mr. McDuck .s rep100000",
                                            ERROR_MSG: "Error. You are not registered as a Data Sender. Please contact your supervisor."}

REGISTER_NEW_SUBJECT = {SENDER: "1234567890",
                        RECEIVER: "919880734937",
                        SMS: "REG .T Clinic .m   123456 .l Jaipur .G 26.917 75.817 ..  .n Clinic Jaipur . ",
                        SUCCESS_MESSAGE: "Thank you Shweta"}

REGISTER_NEW_SUBJECT_TRIAL_ACCOUNT = {SENDER: TRIAL_ACCOUNT_DATA_SENDER_MOBILE_NO,
                        RECEIVER: "447860034166",
                        SMS: "cli fn ln loc 1,1 1283192",
                        SUCCESS_MESSAGE: "Thank you Shweta"}

NEW_SUBMISSION_TRIAL_ACCOUNT = {SENDER: TRIAL_ACCOUNT_DATA_SENDER_MOBILE_NO,
                        RECEIVER: "447860034166",
                        SMS: "cli051 cid001 name 24 25.12.2012 a a 1,1 a",
                        SUCCESS_MESSAGE: "Thank you Shweta"}

REGISTER_EXISTING_SUBJECT_SHORT_CODE = {SENDER: "1234567890",
                                        RECEIVER: "919880734937",
                                        SMS: "REG .T Clinic .m   123456 .l Jaipur .G 26.917 75.817 ..  .n Clinic Jaipur .S cid001 . ",
                                        ERROR_MSG: "Error. cid001 already exists. Register your Clinic with a different Identification Number."}

REGISTER_INVALID_GEO_CODE = {SENDER: "1234567890",
                             RECEIVER: "919880734937",
                             SMS: "cli Clinic blr Agra 127.178057,-78.007789 9900099000",
                             ERROR_MSG: "Error. Incorrect answer for question 4. Please review printed Questionnaire and resend entire SMS."}

REGISTER_WITH_WRONG_NUMBER_OF_ANSWERS = {SENDER: "1234567890",
                             RECEIVER: "919880734937",
                             SMS: "cli Clinic blr Agra 27.178057,-78.007789 9900099000 wat another",
                             ERROR_MSG: "Error. Incorrect number of responses. Please review printed Questionnaire and resend entire SMS.Updated"}
                             # SMS: "REG .T Clinic .m   123456 .l Agra .G 127.178057 -78.007789 .n Clinic Agra .S CLIAGRA",
                             # ERROR_MSG: "Error. Incorrect answer for question 5. Please review printed Questionnaire and resend entire SMS."}

WITH_INVALID_GEO_CODE_FORMAT = {SENDER: "1234567890",
                                RECEIVER: "919880734937",
                                SMS: 'cli002 .EID cid002 . .NA Mr. De`Melo .FA 58 .RD 17.05.2011 .BG ab .SY ade .GPS 127.178057  -78.007789 .RM a',
                                ERROR_MSG: "Error. Incorrect answer for na, bg, gps. Please resend entire message."}

ONLY_QUESTIONNAIRE_CODE = {SENDER: "1234567890",
                           RECEIVER: "919880734937",
                           SMS: "cli009",
                           ERROR_MSG: "Error. Incorrect number of responses. Please review printed Questionnaire and resend entire SMS.Updated"}

WRONG_NUMBER_OF_ARGS = {SENDER: "1234567891",
                        RECEIVER: "919880734937",
                        SMS: "cli009 cid003  Mr.Tessy  58  17.05.2011  b  ade ",
                        ERROR_MSG: "Error. Incorrect number of responses. Please review printed Questionnaire and resend entire SMS."}

VALID_DATA_FOR_ORDERED_SMS = {SENDER: "1234567890",
                              RECEIVER: "919880734937",
                              SMS: "cli011  cid003  Mr.Tessy  58  17.05.2011  b  ade  27.178057,-78.007789 b ac",
                              SUCCESS_MESSAGE: THANKS}#+ " EID: cid003 NA: Mr. Tessy FA: 58 RD: 17.05.2011 BG: O- SY: Rapid weight loss,Memory loss,Neurological disorders GPS: 27.178057,-78.007789 RM: Rétrovir"}

EXCEED_NAME_LENGTH_FOR_ORDERED_SMS = {SENDER: "1234567890",
                                      RECEIVER: "919880734937",
                                      SMS: "cli011  CID003  Mr.O'brain  58  17.05.2011  b  ade  27.178057,-78.007789 c",
                                      ERROR_MSG: "Error. Incorrect answer for na. Please resend entire message."}

DOT_IN_THE_BEGINNING_FOR_ORDERED_SMS = {SENDER: "1234567890",
                                        RECEIVER: "919880734937",
                                        SMS: " cli011  cid003  Mr.Tessy  58  17.05.2011  b  ade  27.178057,-78.007789 a",
                                        ERROR_MSG: "Error: SMS Incorrect. Please review printed questionnaire and resend entire SMS."}

UNREGISTERED_FROM_NUMBER_FOR_ORDERED_SMS = {SENDER: "123445567",
                                            RECEIVER: "919880734937",
                                            SMS: "cli002  CID005 .  Mr.Kessy  58  17.05.2011  b  ade",
                                            ERROR_MSG: "Your telephone number is not yet registered in our system. Please contact your supervisor."}

UNREGISTER_ENTITY_ID = {SENDER: "123445567",
                        RECEIVER: "919880734937",
                        SMS: "cli002  cid0090   Mr.Dessy  58   17.05.2011  b  ade    27.178057,-78.007789 a",
                        ERROR_MSG: "Error. Clinic cid0090 is not registered. Check the Identification Number and resend entire SMS or contact your supervisor."}

UNREGISTER_ENTITY_ID_AND_SOME_INVALID_DATA = {SENDER: "1234567890",
                                              RECEIVER: "919880734937",
                                              SMS: "cli002 cid0090 Mr.Dessy 20 17.12.2011 b ade 27.178057,-78.007789 a",
                                              ERROR_MSG: "Error. cid0090 is not registered. Check the Identification Number and resend entire SMS or contact your supervisor."}

UNAUTHORIZED_DATASENDER = { SENDER: "2619876",
                            RECEIVER: "919880734937",
                            SMS: "cli002 cid005 Mr.Dessy 120 17.17.2011 b ade 27.178057,-78.007789 a",
                            ERROR_MSG: "Error. You are not authorized to submit data for this Questionnaire. Please contact your supervisor."}

MULTIPLE_WRONG_DATA = {SENDER: "123445567",
                            RECEIVER: "919880734937",
                            SMS: "wrcode CID00X5 name age 17.05.2011 b ade 27.178057,-78.007789 ac extradata"}
