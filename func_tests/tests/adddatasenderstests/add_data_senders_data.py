# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8


##Variables
NAME = "name"
MOBILE_NUMBER = "mobile_number"
COMMUNE = "commune"
GPS = "gps"
SUCCESS_MSG = "message"
ERROR_MSG = "message"

BLANK_FIELDS = {NAME: "",
                MOBILE_NUMBER: "",
                COMMUNE: "",
                GPS: "",
                ERROR_MSG: "Name Enter Data Sender's name This field is required.Mobile Number Enter Data Sender's number eg: +61 (123) 456-7890 This field is required.Please fill out at least one location field correctly.Please fill out at least one location field correctly."}

VALID_DATA = {NAME: "Mickey Duck",
              MOBILE_NUMBER: "9876-543-210",
              COMMUNE: "MAHAVELO,AMBOTAKA,MANAKARA ATSIMO,VATOVAVY FITOVINANY",
              GPS: "-21.7622088847 48.0690991394",
              SUCCESS_MSG: "Registration successful. Unique identification number\(ID\) is: rep"}

EXISTING_DATA = {NAME: "Mickey Mouse",
                 MOBILE_NUMBER: "123-4567-890",
                 COMMUNE: "MAHAVELO,AMBOTAKA,MANAKARA ATSIMO,VATOVAVY FITOVINANY",
                 GPS: "-21.7622088847 48.0690991394",
                 ERROR_MSG: "Mobile Number Sorry, the telephone number 1234567890 has already been registered"}

WITHOUT_LOCATION_NAME = {NAME: "Mini Mouse",
                         MOBILE_NUMBER: "345-673-4568",
                         COMMUNE: "",
                         GPS: "-20.676646 47.197266",
                         SUCCESS_MSG: "Registration successful. Unique identification number\(ID\) is: rep"}

WITHOUT_GPS = {NAME: "Alladin",
               MOBILE_NUMBER: "4567345682",
               COMMUNE: "MAHAVELO,AMBOTAKA,MANAKARA ATSIMO,VATOVAVY FITOVINANY",
               GPS: "",
               SUCCESS_MSG: "Registration successful. Unique identification number\(ID\) is: rep"}

INVALID_LATITUDE_GPS = {NAME: "Invalid Latitude GPS",
                        MOBILE_NUMBER: "+673-4568-345",
                        COMMUNE: "",
                        GPS: "123 90",
                        ERROR_MSG: "Incorrect GPS format. The GPS coordinates must be in the following format: xx.xxxx yy.yyyy. Example -18.8665 47.5315"}

INVALID_LONGITUDE_GPS = {NAME: "Invalid Longitude GPS",
                         MOBILE_NUMBER: "(73)456-834-56",
                         COMMUNE: "",
                         GPS: "23 190",
                         ERROR_MSG: "Incorrect GPS format. The GPS coordinates must be in the following format: xx.xxxx yy.yyyy. Example -18.8665 47.5315"}

INVALID_GPS = {NAME: "Invalid GPS with Semi-Colon",
               MOBILE_NUMBER: "7345abc456",
               COMMUNE: "",
               GPS: "23; 10",
               ERROR_MSG: "Mobile Number Please enter a valid phone number.Incorrect GPS format. The GPS coordinates must be in the following format: xx.xxxx yy.yyyy. Example -18.8665 47.5315"}

INVALID_GPS_WITH_COMMA = {NAME: "Invalid GPS With Comma",
                          MOBILE_NUMBER: "734ABCD456",
                          COMMUNE: "",
                          GPS: "23,10",
                          ERROR_MSG: "Mobile Number Please enter a valid phone number.Incorrect GPS format. The GPS coordinates must be in the following format: xx.xxxx yy.yyyy. Example -18.8665 47.5315"}

WITH_UNICODE_IN_GPS = {NAME: "Unicode in GPS",
                       MOBILE_NUMBER: "567!@#$834",
                       COMMUNE: "",
                       GPS: u"23º 45",
                       ERROR_MSG: "Mobile Number Please enter a valid phone number.Incorrect GPS format. The GPS coordinates must be in the following format: xx.xxxx yy.yyyy. Example -18.8665 47.5315"}
