# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8


##Variables
from framework.utils.common_utils import random_number

NAME = "name"
MOBILE_NUMBER = "mobile_number"
MOBILE_NUMBER_WITHOUT_HYPHENS = "mobile_number_without_hyphens"
COMMUNE = "commune"
GPS = "gps"
WEB_CHANNEL = False
EMAIL_ADDRESS = ""
SUCCESS_MSG = "message"
ERROR_MSG = "message"

BLANK_FIELDS = {NAME: "",
                MOBILE_NUMBER: "",
                COMMUNE: "",
                GPS: "",
                ERROR_MSG: "Name This field is required.Mobile Number This field is required.Name Please fill out at least one location field correctly.GPS Coordinates Find GPS coordinates Please fill out at least one location field correctly."}

VALID_DATA = {NAME: "ab Mickey Duck",
              MOBILE_NUMBER: random_number(9),
              MOBILE_NUMBER_WITHOUT_HYPHENS: "98765432101",
              COMMUNE: "MAHAVELO,AMBOTAKA,MANAKARA ATSIMO,VATOVAVY FITOVINANY",
              GPS: "-21.7622088847 48.0690991394",
              SUCCESS_MSG: "Registration successful. ID is: rep"}

VALID_EDIT_DATA = {NAME: "EDIT Mickey Duck",
                   MOBILE_NUMBER: random_number(9),
                   COMMUNE: "PUNE,Madagascar",
                   GPS: "",
                   SUCCESS_MSG: "Your changes have been saved."}

VALID_DATA_WITH_EMAIL = {NAME: "a Mickey Duck",
                         MOBILE_NUMBER: random_number(9),
                         COMMUNE: "MAHAVELO,AMBOTAKA,MANAKARA ATSIMO,VATOVAVY FITOVINANY,Madagascar",
                         EMAIL_ADDRESS: "mIcKeY",
                         GPS: "-21.7622088847,48.0690991394",
                         SUCCESS_MSG: "Registration successful. ID is: "}

VALID_DATA_WITH_EMAIL_EDITED = {NAME: "a Mickey Duck",
                         MOBILE_NUMBER: random_number(9),
                         COMMUNE: "MAHAVELO,AMBOTAKA,MANAKARA ATSIMO,VATOVAVY FITOVINANY,Madagascar",
                         EMAIL_ADDRESS: "mIcKeY_new",
                         GPS: "-21.7622088847,48.0690991394",
                         SUCCESS_MSG: "Your changes have been saved."}


VALID_DATA_WITH_EMAIL_FOR_EDIT = {NAME: "Mickey Duck",
                                  MOBILE_NUMBER: VALID_DATA_WITH_EMAIL[MOBILE_NUMBER],
                                  COMMUNE: "MAHAVELO,AMBOTAKA,MANAKARA ATSIMO,VATOVAVY FITOVINANY",
                                  GPS: "65.34, 17.21",
                                  SUCCESS_MSG: "Your changes have been saved."}

VALID_DATA_WITHOUT_EMAIL = {NAME: "Mickey Duck",
                            MOBILE_NUMBER: "9876-544-2102",
                            COMMUNE: "MAHAVELO,AMBOTAKA,MANAKARA ATSIMO,VATOVAVY FITOVINANY",
                            EMAIL_ADDRESS: "",
                            GPS: "-21.7622088847 48.0690991394",
                            ERROR_MSG: "Email address This field is required."}

EXISTING_DATA = {NAME: "Mickey Mouse",
                 MOBILE_NUMBER: "123-4567-890",
                 COMMUNE: "MAHAVELO,AMBOTAKA,MANAKARA ATSIMO,VATOVAVY FITOVINANY",
                 GPS: "-21.7622088847 48.0690991394",
                 ERROR_MSG: "Mobile Number Sorry, the telephone number 1234567890 has already been registered"}

WITHOUT_LOCATION_NAME = {NAME: "a Mini Mouse",
                         MOBILE_NUMBER: random_number(),
                         COMMUNE: "",
                         GPS: "-20.676646 47.197266",
                         SUCCESS_MSG: "Registration successful. ID is: rep"}

WITHOUT_GPS = {NAME: "Alladin",
               MOBILE_NUMBER: random_number(),
               COMMUNE: "MAHAVELO,AMBOTAKA,MANAKARA ATSIMO,VATOVAVY FITOVINANY",
               GPS: "",
               SUCCESS_MSG: "Registration successful. ID is: rep"}

INVALID_LATITUDE_GPS = {NAME: "Invalid Latitude GPS",
                        MOBILE_NUMBER: "+673-4568-345",
                        COMMUNE: "",
                        GPS: "123 90",
                        ERROR_MSG: "GPS Coordinates Find GPS coordinates Incorrect GPS format. The GPS coordinates must be in the following format: xx.xxxx,yy.yyyy. Example -18.8665,47.5315"}

INVALID_LONGITUDE_GPS = {NAME: "Invalid Longitude GPS",
                         MOBILE_NUMBER: "(73)456-834-56",
                         COMMUNE: "",
                         GPS: "23 190",
                         ERROR_MSG: "GPS Coordinates Find GPS coordinates Incorrect GPS format. The GPS coordinates must be in the following format: xx.xxxx,yy.yyyy. Example -18.8665,47.5315"}

INVALID_GPS = {NAME: "Invalid GPS with Semi-Colon",
               MOBILE_NUMBER: "7345abc456",
               COMMUNE: "",
               GPS: "23; 10",
               ERROR_MSG: u"Mobile Number Please enter a valid phone number.GPS Coordinates Find GPS coordinates Incorrect GPS format. The GPS coordinates must be in the following format: xx.xxxx,yy.yyyy. Example -18.8665,47.5315"}

INVALID_GPS_WITH_COMMA = {NAME: "Invalid GPS With Comma",
                          MOBILE_NUMBER: "734ABCD456",
                          COMMUNE: "",
                          GPS: "23,10",
                          ERROR_MSG: "Mobile Number Please enter a valid phone number.Incorrect GPS format. The GPS coordinates must be in the following format: xx.xxxx,yy.yyyy. Example -18.8665,47.5315"}

WITH_UNICODE_IN_GPS = {NAME: "Unicode in GPS",
                       MOBILE_NUMBER: "567!@#$834",
                       COMMUNE: "",
                       GPS: u"23º 45",
                       ERROR_MSG: "Mobile Number Please enter a valid phone number.GPS Coordinates Find GPS coordinates Incorrect GPS format. The GPS coordinates must be in the following format: xx.xxxx,yy.yyyy. Example -18.8665,47.5315"}

VALID_DATA_FOR_LONG_UID = {NAME: "Donald Duck",
                           MOBILE_NUMBER: "261336231",
                           MOBILE_NUMBER_WITHOUT_HYPHENS: "261336231",
                           COMMUNE: "MAHAVELO,AMBOTAKA,MANAKARA ATSIMO,VATOVAVY FITOVINANY",
                           GPS: "-21.7622088847 48.0690991394",
                           ERROR_MSG: u'Unique ID Unique ID should be less than 12 characters    Let us generate an ID for you'}