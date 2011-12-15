# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8


##Variables
PROJECT_NAME = "project_name"
PROJECT_BACKGROUND = "project_background"
PROJECT_TYPE = "project_type"
REPORT_TYPE = "report_type"
SUBJECT = "subject"
DEVICES = "devices"
ERROR_MSG = "message"
PAGE_TITLE = "page_title"
GEN_RANDOM = "gen_random"
SURVEY = "survey"
PUBLIC_INFO = "public information"
DATA_SENDER_WORK = "data sender work"
OTHER_SUBJECT = "other subject"

VALID_DATA = {PROJECT_NAME: "Reporter Activities ", GEN_RANDOM: True,
              PROJECT_BACKGROUND: "This project is created by functional automation suite.",
              PROJECT_TYPE: SURVEY,
              SUBJECT: "",
              REPORT_TYPE: "data sender work",
              DEVICES: "sms",
              PAGE_TITLE: "Projects - Overview"}

VALID_DATA2 = {PROJECT_NAME: "Water Point2 Morondava ", GEN_RANDOM: True,
               PROJECT_BACKGROUND: "This project is created by functional automation suite.",
               PROJECT_TYPE: "survey",
               SUBJECT: "waterpoint",
               REPORT_TYPE: "other subject",
               DEVICES: "sms",
               PAGE_TITLE: "Projects - Overview"}

BLANK_FIELDS = {PROJECT_NAME: "",
                PROJECT_BACKGROUND: "",
                PROJECT_TYPE: "",
                SUBJECT: "",
                REPORT_TYPE: "",
                DEVICES: "",
                ERROR_MSG: "Name  This field is required."}
