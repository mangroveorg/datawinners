#export
# from mangrove.transport.repository.survey_responses import SUCCESS_SURVEY_RESPONSE_VIEW_NAME, UNDELETED_SURVEY_RESPONSE_VIEW_NAME, DELETED_SURVEY_RESPONSE_VIEW_NAME, get_survey_responses
#
# def successful_survey_responses(dbm, form_code):
#     return get_survey_responses(dbm, form_code, None, None, view_name=SUCCESS_SURVEY_RESPONSE_VIEW_NAME)
#
# def undeleted_survey_responses(dbm, form_code):
#     return get_survey_responses(dbm, form_code, None, None, view_name=UNDELETED_SURVEY_RESPONSE_VIEW_NAME)
#
# def deleted_survey_responses(dbm, form_code, from_time=None, to_time=None, page_number=0, page_size=None):
#     return get_survey_responses(dbm, form_code, from_time, to_time, page_number, page_size, DELETED_SURVEY_RESPONSE_VIEW_NAME)
#
# def all_survey_responses(dbm, form_code, from_time=None, to_time=None, page_number=0, page_size=None):
#     return get_survey_responses(dbm, form_code, from_time, to_time, page_number, page_size)
#
# class SurveyResponseRouter(object):
#     ALL = "all"
#     SUCCESS = "success"
#     ERROR = "error"
#     DELETED = "deleted"
#
#     SURVEY_RESPONSE_ROUTER = {
#         ALL: undeleted_survey_responses,
#         SUCCESS: successful_survey_responses,
#         ERROR: undeleted_survey_responses,
#         DELETED: deleted_survey_responses
#     }
#
#     def route(self, type):
#         return self.SURVEY_RESPONSE_ROUTER.get(type, successful_survey_responses)