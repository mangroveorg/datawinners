# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8


##Variables
from datawinners.messageprovider.tests.test_message_handler import THANKS

PROJECT_NAME = "project_name"
SMS = "sms"
RESPONSE_MESSAGE = "message"

VALID_DATA = {SMS: "cli005 .EID cid003 .NA Mr. Tessy .FA 58 .RD 17.05.2011 .BG b .SY ade .GPS 27.178057  -78.007789",
              RESPONSE_MESSAGE: THANKS}#+ " SY: Rapid weight loss,Memory loss,Neurological disorders  BG: O- NA: Mr. Tessy RD: 17.05.2011 FA: 58 EID: cid003 GPS: 27.178057,-78.007789"}

EXCEED_NAME_LENGTH = {
    SMS: "cli009 .EID CID003 .NA Mr. O'brain .FA 58 .RD 17.05.2011 .BG b .SY ade .GPS 27.178057 -78.007789 .RM a",
    RESPONSE_MESSAGE: "Error. Incorrect answer for question 2. Please review printed Questionnaire and resend entire SMS."}

VALID_DATA2 = {SMS: "cli005 .EID cid004 .NA Mr. O'man .FA 58 .RD 17.05.2011 .BG b .SY ade .GPS 27.178057  -78.007789",
               RESPONSE_MESSAGE: (
                                     THANKS % "Test") + " for Clinic Khandwa Clinic (cid004)."}#+ " EID: cid004 NA: Mr. O'man FA: 58 RD: 17.05.2011 BG: O- SY: Rapid weight loss,Memory loss,Neurological disorders  GPS: 27.178057, -78.007789"}

VALID_ORDERED_SMS_DATA = {SMS: "cli005 cid004 O'man 58 17.05.2011 b ade 27.178057,-78.007789",
                          RESPONSE_MESSAGE: (
                                                THANKS % "Test") + ": cid004; O'man; 58; 17.05.2011; O-; Rapid weight loss,Memory loss,Neurological disorders ; 27.178057, -78.007789"}
SUBJECT_REGISTRATION_VIA_SMS = {SMS: "cli mariestopes madagascar avaradoha -1,-3 261498394"}
