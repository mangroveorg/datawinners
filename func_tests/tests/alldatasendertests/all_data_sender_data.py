# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8


##Variables
NAME = "name"
MOBILE_NUMBER = "mobile_number"
LOCATION = "location"
GPS = "gps"
SUCCESS_MSG = "message"
ERROR_MSG = "message"
PROJECT_NAME = "project_name"
ASSOCIATE = "associate"
DISSOCIATE = "disassociate"
UID = "uid"
ASSOCIATE_SUCCESS_TEXT = "Data Senders associated Successfully. Please Wait...."
DISSOCIATE_SUCCESS_TEXT = "Data Senders dissociated Successfully. Please Wait...."

ASSOCIATE_DATA_SENDER = {PROJECT_NAME: "clinic test project",
                         UID: "rep1",
                         MOBILE_NUMBER: "1234567890"}

DISSOCIATE_DATA_SENDER = {PROJECT_NAME: "clinic test project",
                         UID: "rep1",
                         MOBILE_NUMBER: "1234567890"}

DISSOCIATE_DS_WITHOUT_SELECTING_PROJECT = {UID: "rep1", ERROR_MSG: "Please select atleast 1 Project"}

ASSOCIATE_DS_WITHOUT_SELECTING_PROJECT = {UID: "rep2", ERROR_MSG: "Please select atleast 1 Project"}

DISSOCIATE_DS_WITHOUT_SELECTING_DS = {PROJECT_NAME: "clinic test project", ERROR_MSG: u"Please select atleast 1 data sender"}

ASSOCIATE_DS_WITHOUT_SELECTING_DS = {PROJECT_NAME: "clinic test project", ERROR_MSG: u"Please select atleast 1 data sender"}
