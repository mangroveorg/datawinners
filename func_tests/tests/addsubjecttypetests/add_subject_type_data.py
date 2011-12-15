# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8


ENTITY_TYPE = 'entity_type'
ERROR_MESSAGE = 'message'
SUCCESS_MESSAGE = 'message'

# valid entity data
VALID_ENTITY = {ENTITY_TYPE: "Hospital", SUCCESS_MESSAGE: "hospital"}
# already exist entity
ALREADY_EXIST_ENTITY = {ENTITY_TYPE: "clinic", ERROR_MESSAGE: "clinic already registered as a subject type. Please select clinic from the drop down menu."}
# Blank entity
BLANK = {ENTITY_TYPE: "", ERROR_MESSAGE: "Only letters and numbers are valid"}
INVALID_ENTITY = {ENTITY_TYPE: "w@terpo!nt", ERROR_MESSAGE: "Only letters and numbers are valid"}
