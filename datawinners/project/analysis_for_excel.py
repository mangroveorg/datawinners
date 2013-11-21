#export
# from datawinners.project.survey_response_data import SurveyResponseData
# from datawinners.main.utils import timebox
# from datawinners.project.Header import Header
# from datawinners.project.data_sender import DataSender
# from datawinners.project.export_to_excel import format_field_values_for_excel
#
# class AnalysisForExcel(SurveyResponseData):
#
#     def __init__(self, form_model, manager, org_id, filters, keyword=None):
#         super(AnalysisForExcel, self).__init__(form_model, manager, org_id, Header, None, filters, keyword)
#
#     def get_leading_part(self):
#         leading_part = []
#         for submission in self.filtered_survey_responses:
#             data_sender_tuple, rp, subject_tuple, submission_date = super(AnalysisForExcel,
#                 self).get_survey_response_details_for_excel(submission)
#             subject_id = subject_tuple[1] if subject_tuple else ""
#             subject_name = subject_tuple[0] if subject_tuple else ""
#             data_sender = DataSender.from_tuple(data_sender_tuple)
#             leading_part.append(
#                 filter(lambda x: x, [submission.id, subject_name, subject_id, rp, submission_date, data_sender.name,
#                                      data_sender.reporter_id]))
#         return leading_part
#
#     @timebox
#     def _get_field_values(self):
#         submission_values = [(submission.form_model_revision, submission.values) for submission in
#                              self.filtered_survey_responses]
#         field_values = []
#         for row in submission_values:
#             fields_ = []
#             formatted_row = format_field_values_for_excel(row, self.form_model)
#             for field in self.form_model.non_rp_fields_by():
#                 fields_.extend(self.order_formatted_row(field.code, formatted_row))
#             field_values.append(fields_)
#         return field_values
