# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8


##Variables
ENTITY_TYPE = "entity_type"
SHORT_NAME = "short_name"
AUTO_GENERATE = "auto_generate"
NAME = "name"
LOCATION = "location"
GEO_CODE = "geo_code"
DESCRIPTION = "description"
MOBILE_NUMBER = "mobile_number"
SUCCESS_MSG = "message"
ERROR_MSG = "message"

SUB_FIRST_NAME = "sub_first_name"
SUB_LAST_NAME = "sub_last_name"
SUB_UNIQUE_ID = "sub_unique_id"
SUCCESSFUL_MESSAGE = "Clinic with Identification Number %s successfully registered."

VALID_DATA = {ENTITY_TYPE: "clinic",
              SUB_FIRST_NAME: "Clinic Monodova",
              SUB_LAST_NAME: "wat",
              LOCATION: "Monodova",
              GEO_CODE: "47.411631 28.369885",
              MOBILE_NUMBER: "345-678-90",
              SUB_UNIQUE_ID: None,
              SUCCESS_MSG: "Clinic with Identification Number %s successfully registered."}
VALID_DATA_FOR_EDIT = {ENTITY_TYPE: "clinic",
                       SUB_FIRST_NAME: "Clinic Monodova editted",
                       SUB_LAST_NAME: "wat",
                       LOCATION: "Monodova",
                       GEO_CODE: "47,28",
                       MOBILE_NUMBER: "001-345-678-90",
                       SUB_UNIQUE_ID: None,
                       SUCCESS_MSG: "Your changes have been saved."}

SUBJECT_DATA_WITHOUT_UNIQUE_ID = {ENTITY_TYPE: "clinic",
                                  SUB_FIRST_NAME: "Clinic Monodova",
                                  SUB_LAST_NAME: "wat",
                                  LOCATION: "Monodova",
                                  GEO_CODE: "47.411631 28.369885",
                                  MOBILE_NUMBER: "34-567-890",
                                  SUB_UNIQUE_ID: None,
                                  SUCCESS_MSG: SUCCESSFUL_MESSAGE}

EXISTING_SHORT_CODE = {ENTITY_TYPE: "clinic",
                       SUB_FIRST_NAME: "Clinic Amparaky",
                       SUB_LAST_NAME: "wat",
                       LOCATION: "Amparaky",
                       GEO_CODE: "-19.316667 46.633333",
                       MOBILE_NUMBER: "34567890",
                       SUB_UNIQUE_ID: "CID001",
                       ERROR_MSG: "Clinic with ID Number 'cid001' already exists or has previously collected data."}

WITHOUT_LOCATION_NAME = {ENTITY_TYPE: "clinic",
                         SUB_FIRST_NAME: "Clinic Without Location",
                         SUB_LAST_NAME: "cli050",
                         MOBILE_NUMBER: "3456734568",
                         LOCATION: "",
                         GEO_CODE: "23.955267  45.816013",
                         SUB_UNIQUE_ID: None,
                         SUCCESS_MSG: "This field is required."}

WITHOUT_GPS = {ENTITY_TYPE: "clinic",
               SUB_FIRST_NAME: "Alladin",
               SUB_LAST_NAME: "cli",
               MOBILE_NUMBER: "4567345683",
               LOCATION: "MAHAVELO,AMBOTAKA,MANAKARA ATSIMO,VATOVAVY FITOVINANY",
               GEO_CODE: "",
               SUB_UNIQUE_ID: None,
               SUCCESS_MSG: "This field is required."}

INVALID_LATITUDE_GPS = {ENTITY_TYPE: "clinic",
                        SUB_FIRST_NAME: "Invalid Latitude GPS",
                        SUB_LAST_NAME: "cli",
                        MOBILE_NUMBER: "+673-456-83-45",
                        LOCATION: "DIANA",
                        GEO_CODE: "123,90",
                        SUB_UNIQUE_ID: None,
                        ERROR_MSG: "Incorrect GPS format. The GPS coordinates must be in the following format: xx.xxxx,yy.yyyy. Example -18.8665,47.5315"}

INVALID_LONGITUDE_GPS = {ENTITY_TYPE: "clinic",
                         SUB_FIRST_NAME: "Invalid Longitude GPS",
                         SUB_LAST_NAME: "cli",
                         MOBILE_NUMBER: "(73)4568-34-56",
                         LOCATION: "DIANA",
                         GEO_CODE: "23,190",
                         SUB_UNIQUE_ID: None,
                         ERROR_MSG: "Incorrect GPS format. The GPS coordinates must be in the following format: xx.xxxx,yy.yyyy. Example -18.8665,47.5315"}

INVALID_GPS_AND_PHONE_NUMBER = {ENTITY_TYPE: "clinic",
                                SUB_FIRST_NAME: "Invalid GPS with Semi-Colon",
                                SUB_LAST_NAME: "Invalid GPS with Semi-Colon",
                                LOCATION: "DIANA",
                                GEO_CODE: "23; 10",
                                MOBILE_NUMBER: "734!@#$456",
                                SUB_UNIQUE_ID: None,
                                ERROR_MSG: "Incorrect GPS format. The GPS coordinates must be in the following format: xx.xxxx,yy.yyyy. Example -18.8665,47.5315Please enter a valid phone number."}

WITH_UNICODE_IN_GPS_AND_INVALID_PHONE_NUMBER = {ENTITY_TYPE: "clinic",
                                                SUB_FIRST_NAME: "Unicode in GPS",
                                                SUB_LAST_NAME: "cli",
                                                MOBILE_NUMBER: "567ABCD834",
                                                LOCATION: "DIANA",
                                                GEO_CODE: u"23º aa",
                                                SUB_UNIQUE_ID: None,
                                                ERROR_MSG: "Incorrect GPS format. The GPS coordinates must be in the following format: xx.xxxx,yy.yyyy. Example -18.8665,47.5315Please enter a valid phone number."}

CLINIC_WITH_INVALID_UID = {ENTITY_TYPE: "clinic",
                           SUB_FIRST_NAME: "Clinic Monodova",
                           SUB_LAST_NAME: "wat",
                           LOCATION: "Monodova",
                           GEO_CODE: "47.411631 28.369885",
                           MOBILE_NUMBER: "34-567-890",
                           SUB_UNIQUE_ID: "12345678-=323223",
                           ERROR_MSG: "Only letters and numbers are valid"}

PROJECT_NAME = "project_name"
PROJECT_BACKGROUND = "project_background"
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
WARNING_MESSAGE = "warning_message"

VALID_PROJECT_DATA = {PROJECT_NAME: "Subject reg Activities ", GEN_RANDOM: True,
                      PROJECT_BACKGROUND: "This project is created by functional automation suite.",
                      SUBJECT: "clinic",
                      REPORT_TYPE: "other subject",
                      DEVICES: "sms",
                      PAGE_TITLE: "Questionnaire - Overview",
                      WARNING_MESSAGE:
                          u"Translate or re-word this question if needed, but donʼt change its meaning. You can also delete the question if you donʼt need it for your project."}

VALID_SUBJECT_REGISTRATION_DATA = {ENTITY_TYPE: "clinic",
                                   SUB_FIRST_NAME: "Clinic BANGALORE",
                                   SUB_LAST_NAME: "something",
                                   LOCATION: "Monodova",
                                   GEO_CODE: "47.411631 28.369885",
                                   MOBILE_NUMBER: "990099000",
                                   SUB_UNIQUE_ID: None,
                                   SUCCESS_MSG: SUCCESSFUL_MESSAGE}