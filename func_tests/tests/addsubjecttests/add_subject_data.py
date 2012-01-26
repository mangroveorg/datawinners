# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8


##Variables
ENTITY_TYPE = "entity_type"
SHORT_NAME = "short_name"
AUTO_GENERATE = "auto_generate"
NAME = "name"
LOCATION = "location"
GPS = "geo_code"
DESCRIPTION = "description"
MOBILE_NUMBER = "mobile_number"
SUCCESS_MSG = "message"
ERROR_MSG = "message"

SUB_FIRST_NAME = "sub_first_name"
SUB_LAST_NAME = "sub_last_name"
SUB_UNIQUE_ID = "sub_unique_id"
SUCCESSFUL_MESSAGE = "Successfully submitted. Unique identification number\(ID\) is: "

VALID_DATA = {ENTITY_TYPE: "clinic",
              SUB_FIRST_NAME: "Clinic Monodova",
              SUB_LAST_NAME: "wat",
              LOCATION: "Monodova",
              GPS: "47.411631 28.369885",
              MOBILE_NUMBER: "345-678-90",
              SUB_UNIQUE_ID: None,
              SUCCESS_MSG: SUCCESSFUL_MESSAGE}

AUTO_GENERATE_FALSE = {ENTITY_TYPE: "clinic",
                       SUB_FIRST_NAME: "Clinic Monodova",
                       SUB_LAST_NAME: "wat",
                       LOCATION: "Monodova",
                       GPS: "47.411631 28.369885",
                       MOBILE_NUMBER: "34-567-890",
                       SUB_UNIQUE_ID: None,
                       SUCCESS_MSG: SUCCESSFUL_MESSAGE}

EXISTING_SHORT_CODE = {ENTITY_TYPE: "clinic",
                       SUB_FIRST_NAME: "Clinic Amparaky",
                       SUB_LAST_NAME: "wat",
                       LOCATION: "Amparaky",
                       GPS: "-19.316667 46.633333",
                       MOBILE_NUMBER: "34567890",
                       SUB_UNIQUE_ID: "CID001",
                       ERROR_MSG: "Entity with Unique Identification Number (ID) = cid001 already exists."}

WITHOUT_LOCATION_NAME = {ENTITY_TYPE: "waterpoint",
                         SUB_FIRST_NAME: "Waterpoint Without Location",
                         SUB_LAST_NAME: "wat",
                         MOBILE_NUMBER: "3456734568",
                         LOCATION: "",
                         GPS: "23.955267  45.816013",
                         SUB_UNIQUE_ID: None,
                         SUCCESS_MSG: "This field is required."}

WITHOUT_GPS = {ENTITY_TYPE: "clinic",
               SUB_FIRST_NAME: "Alladin",
               SUB_LAST_NAME: "cli",
               MOBILE_NUMBER: "4567345683",
               LOCATION: "MAHAVELO,AMBOTAKA,MANAKARA ATSIMO,VATOVAVY FITOVINANY",
               GPS: "",
               SUB_UNIQUE_ID: None,
               SUCCESS_MSG: "This field is required."}

INVALID_LATITUDE_GPS = {ENTITY_TYPE: "clinic",
                        SUB_FIRST_NAME: "Invalid Latitude GPS",
                        SUB_LAST_NAME: "cli",
                        MOBILE_NUMBER: "+673-456-83-45",
                        LOCATION: "DIANA",
                        GPS: "123 90",
                        SUB_UNIQUE_ID: None,
                        ERROR_MSG: "Incorrect GPS format. The GPS coordinates must be in the following format: xx.xxxx yy.yyyy. Example -18.8665 47.5315"}

INVALID_LONGITUDE_GPS = {ENTITY_TYPE: "clinic",
                         SUB_FIRST_NAME: "Invalid Longitude GPS",
                         SUB_LAST_NAME: "cli",
                         MOBILE_NUMBER: "(73)4568-34-56",
                         LOCATION: "DIANA",
                         GPS: "23 190",
                         SUB_UNIQUE_ID: None,
                         ERROR_MSG: "Incorrect GPS format. The GPS coordinates must be in the following format: xx.xxxx yy.yyyy. Example -18.8665 47.5315"}


INVALID_GPS =   {ENTITY_TYPE: "clinic",
                 SUB_FIRST_NAME: "Invalid GPS with Semi-Colon",
                 SUB_LAST_NAME: "Invalid GPS with Semi-Colon",
                 LOCATION: "DIANA",
                 GPS: "23; 10",
                 MOBILE_NUMBER: "734!@#$456",
                 SUB_UNIQUE_ID: None,
                 ERROR_MSG: "Please enter a valid phone number.Incorrect GPS format. The GPS coordinates must be in the following format: xx.xxxx yy.yyyy. Example -18.8665 47.5315"}


INVALID_GPS_WITH_COMMA = {ENTITY_TYPE: "clinic",
                          SUB_FIRST_NAME: "Invalid GPS With Comma",
                          SUB_LAST_NAME: "cli",
                          MOBILE_NUMBER: "734abcd3456",
                          LOCATION: "DIANA",
                          GPS: "23,10",
                          SUB_UNIQUE_ID: None,
                          ERROR_MSG: "Please enter a valid phone number.Incorrect GPS format. The GPS coordinates must be in the following format: xx.xxxx yy.yyyy. Example -18.8665 47.5315"}

WITH_UNICODE_IN_GPS = {ENTITY_TYPE: "clinic",
                       SUB_FIRST_NAME: "Unicode in GPS",
                       SUB_LAST_NAME: "cli",
                       MOBILE_NUMBER: "567ABCD834",
                       LOCATION: "DIANA",
                       GPS: u"23º 45",
                       SUB_UNIQUE_ID: None,
                       ERROR_MSG: "Please enter a valid phone number.Incorrect GPS format. The GPS coordinates must be in the following format: xx.xxxx yy.yyyy. Example -18.8665 47.5315"}
