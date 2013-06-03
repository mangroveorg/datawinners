# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8


##Variables
from tests.createquestionnairetests.create_questionnaire_data import QUESTIONS

TITLE = "title"
MESSAGE = "message"
PROJECT_NAME = "project_name"
PROJECT_BACKGROUND = "project_background"
PROJECT_TYPE = "project_type"
REPORT_TYPE = "report_type"
SUBJECT = "subject"
DEVICES = "devices"
ERROR_MSG = "message"
PAGE_TITLE = "page_title"
GEN_RANDOM = "gen_random"
DATA_SENDER_WORK = "data sender work"
OTHER_SUBJECT = "other subject"
DEFAULT_QUESTION = "default_question"
PROJECT = "project"

VALID_DATA = {PROJECT_NAME: u"clinic3 test project",
              PROJECT_BACKGROUND: u"This project is for automation",
              #PROJECT_TYPE: "survey",
              SUBJECT: u"clinic",
              REPORT_TYPE: OTHER_SUBJECT,
              #DEVICES: "sms"
              }

ACTIVATED_PROJECT_DATA = {PROJECT_NAME: u"clinic test project",
              PROJECT_BACKGROUND: u"This project is for automation",
              #PROJECT_TYPE: "survey",
              SUBJECT: u"clinic",
              REPORT_TYPE: OTHER_SUBJECT,
              #DEVICES: "sms"
              }

WATER_POINT_DATA = {PROJECT_NAME: u"water point morondova",
                    PROJECT_BACKGROUND: u"This project is for automation",
                    #PROJECT_TYPE: "survey",
                    SUBJECT: u"waterpoint",
                    REPORT_TYPE: OTHER_SUBJECT,
                    #DEVICES: "sms"
                    }

QUESTIONNAIRE_DATA_FOR_WATER_POINT = {QUESTIONS: ["Which waterpoint are you reporting on?", "What is the reporting period for the activity?"]}

VALID_DATA2 = {PROJECT_NAME: u"clinic4 test project",
               PROJECT_BACKGROUND: u"This project is for automation",
               #PROJECT_TYPE: "survey",
               SUBJECT: u"clinic",
               REPORT_TYPE: OTHER_SUBJECT,
               #DEVICES: "sms"
               }

REPORTER_ACTIVITIES_DATA = {PROJECT_NAME: u"reporter activities",
                            PROJECT_BACKGROUND: u"This project is for automation",
                            #PROJECT_TYPE: "survey",
                            SUBJECT: "",
                            REPORT_TYPE: DATA_SENDER_WORK,
                            #DEVICES: "sms"
                            }

QUESTIONNAIRE_DATA_FOR_REPORTER_ACTIVITIES = {QUESTIONS: ["What is the reporting period for the activity?"]}

LIGHT_BOX_DATA = {TITLE: "Warning !!",
                  SUBJECT: "Changing the subject type will remove all questions from your questionnaire as well as all your collected data. Are you sure you want to continue?",
                  PROJECT: "Changing the project type will remove all questions from your questionnaire as well as all your collected data. Are you sure you want to continue?"}
