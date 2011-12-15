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

VALID_DATA = {ENTITY_TYPE: "clinic",
              SHORT_NAME: "cli",
              AUTO_GENERATE: True,
              NAME: "Clinic Monodova",
              LOCATION: "Monodova",
              GPS: "47.411631 28.369885",
              DESCRIPTION: "This is a clinic in monodova",
              MOBILE_NUMBER: "345-678-90",
              SUCCESS_MSG: "Registration successful. Unique identification number\(ID\) is: "}

AUTO_GENERATE_FALSE = {ENTITY_TYPE: "clinic",
                       SHORT_NAME: "cli",
                       AUTO_GENERATE: False,
                       NAME: "Clinic Monodova",
                       LOCATION: "Monodova",
                       GPS: "47.411631 28.369885",
                       DESCRIPTION: "This is a clinic in monodova",
                       MOBILE_NUMBER: "34-567-890",
                       SUCCESS_MSG: "Registration successful. Unique identification number\(ID\) is: "}

EXISTING_SHORT_CODE = {ENTITY_TYPE: "clinic",
                       SHORT_NAME: "CID001",
                       AUTO_GENERATE: False,
                       NAME: "Clinic Amparaky",
                       LOCATION: "Amparaky",
                       GPS: "-19.316667 46.633333",
                       DESCRIPTION: "This is a clinic in Amparaky",
                       MOBILE_NUMBER: "34567890",
                       ERROR_MSG: "Entity with Unique Identification Number (ID) = cid001 already exists."}

WITHOUT_LOCATION_NAME = {ENTITY_TYPE: "waterpoint",
                         NAME: "Waterpoint Without Location",
                         SHORT_NAME: "wat",
                         AUTO_GENERATE: True,
                         MOBILE_NUMBER: "3456734568",
                         LOCATION: "",
                         GPS: "23.955267  45.816013",
                         DESCRIPTION: "This is a water point Without Location",
                         SUCCESS_MSG: "Registration successful. Unique identification number\(ID\) is: "}

WITHOUT_GPS = {ENTITY_TYPE: "clinic",
               NAME: "Alladin",
               SHORT_NAME: "cli",
               AUTO_GENERATE: True,
               MOBILE_NUMBER: "4567345683",
               LOCATION: "MAHAVELO,AMBOTAKA,MANAKARA ATSIMO,VATOVAVY FITOVINANY",
               GPS: "",
               DESCRIPTION: "This is a clinic in MAHAVELO",
               SUCCESS_MSG: "Registration successful. Unique identification number\(ID\) is: "}

INVALID_LATITUDE_GPS = {ENTITY_TYPE: "clinic",
                        NAME: "Invalid Latitude GPS",
                        SHORT_NAME: "cli",
                        AUTO_GENERATE: True,
                        MOBILE_NUMBER: "+673-456-83-45",
                        LOCATION: "",
                        GPS: "123 90",
                        DESCRIPTION: "This is a clinic with Invalid Latitude GPS",
                        ERROR_MSG: "GPS Incorrect GPS format. The GPS coordinates must be in the following format: xx.xxxx yy.yyyy. Example -18.8665 47.5315Mobile Number Optional Please enter a valid phone number."}

INVALID_LONGITUDE_GPS = {ENTITY_TYPE: "clinic",
                         NAME: "Invalid Longitude GPS",
                         SHORT_NAME: "cli",
                         AUTO_GENERATE: True,
                         MOBILE_NUMBER: "(73)4568-34-56",
                         LOCATION: "",
                         GPS: "23 190",
                         DESCRIPTION: "This is a clinic with Invalid Longitude GPS",
                         ERROR_MSG: "GPS Incorrect GPS format. The GPS coordinates must be in the following format: xx.xxxx yy.yyyy. Example -18.8665 47.5315Mobile Number Optional Please enter a valid phone number."}

INVALID_GPS = {ENTITY_TYPE: "clinic",
               NAME: "Invalid GPS with Semi-Colon",
               SHORT_NAME: "cli",
               AUTO_GENERATE: True,
               MOBILE_NUMBER: "734!@#$456",
               LOCATION: "",
               GPS: "23; 10",
               DESCRIPTION: "This is a clinic with Invalid GPS with Semi-Colon",
               ERROR_MSG: "GPS Incorrect GPS format. The GPS coordinates must be in the following format: xx.xxxx yy.yyyy. Example -18.8665 47.5315Mobile Number Optional Please enter a valid phone number."}

INVALID_GPS_WITH_COMMA = {ENTITY_TYPE: "clinic",
                          NAME: "Invalid GPS With Comma",
                          SHORT_NAME: "cli",
                          AUTO_GENERATE: True,
                          MOBILE_NUMBER: "734abcd3456",
                          LOCATION: "",
                          GPS: "23,10",
                          DESCRIPTION: "This is a clinic with Invalid GPS With Comma",
                          ERROR_MSG: "GPS Incorrect GPS format. The GPS coordinates must be in the following format: xx.xxxx yy.yyyy. Example -18.8665 47.5315Mobile Number Optional Please enter a valid phone number."}

WITH_UNICODE_IN_GPS = {ENTITY_TYPE: "clinic",
                       NAME: "Unicode in GPS",
                       SHORT_NAME: "cli",
                       AUTO_GENERATE: True,
                       MOBILE_NUMBER: "567ABCD834",
                       LOCATION: "",
                       GPS: u"23º 45",
                       DESCRIPTION: "This is a clinic with Unicode in GPS",
                       ERROR_MSG: "GPS Incorrect GPS format. The GPS coordinates must be in the following format: xx.xxxx yy.yyyy. Example -18.8665 47.5315Mobile Number Optional Please enter a valid phone number."}
