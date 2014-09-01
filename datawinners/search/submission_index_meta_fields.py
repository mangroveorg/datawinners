ES_SUBMISSION_FIELD_DS_ID = "ds_id"
ES_SUBMISSION_FIELD_DS_NAME = "ds_name"
ES_SUBMISSION_FIELD_DATE = "date"
ES_SUBMISSION_FIELD_STATUS = "status"
ES_SUBMISSION_FIELD_ERROR_MSG = "error_msg"
ES_SUBMISSION_FIELD_DS_PHONE_NUMBER = "open_datasender_phone_number"
#ES_SUBMISSION_FIELD_ENTITY_SHORT_CODE = "entity_short_code"

meta_fields = [ES_SUBMISSION_FIELD_DS_ID, ES_SUBMISSION_FIELD_DS_NAME, ES_SUBMISSION_FIELD_DATE,
               ES_SUBMISSION_FIELD_STATUS, ES_SUBMISSION_FIELD_ERROR_MSG]

submission_meta_fields = [{"name": ES_SUBMISSION_FIELD_DATE, "type": "date", "date_format": 'submission_date_format'},
                          {"name": ES_SUBMISSION_FIELD_STATUS},
                          {"name": ES_SUBMISSION_FIELD_DS_NAME},
                          {"name": ES_SUBMISSION_FIELD_DS_ID},
                          {"name": ES_SUBMISSION_FIELD_ERROR_MSG},
                          {"name": ES_SUBMISSION_FIELD_DS_PHONE_NUMBER}]
                          #{"name": ES_SUBMISSION_FIELD_ENTITY_SHORT_CODE}]


submission_meta_field_names = dict([(field["name"], None) for field in submission_meta_fields])
