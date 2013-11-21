#export
#from django.http import HttpResponse


#import datawinners.utils as utils
#from datawinners.project.survey_response_router import SurveyResponseRouter
#from django.template.defaultfilters import slugify


# def _prepare_export_data(submission_type, project_name, header_list, formatted_values):
#     suffix = submission_type + '_log' if submission_type else 'analysis'
#     file_name = "%s_%s" % (project_name, suffix)
#     return header_list + formatted_values, file_name





#def _get_exported_data(header, formatted_values, submission_log_type):
    #
    # submission_id_col = 0
    # status_col = 4
    # reply_sms_col = 5
    # if submission_log_type in [SurveyResponseRouter.ALL, SurveyResponseRouter.DELETED]:
    #     return [each[submission_id_col + 1:reply_sms_col] + each[reply_sms_col + 1:] for each in data]
    # elif submission_log_type in [SurveyResponseRouter.ERROR]:
    #     return [each[submission_id_col + 1:status_col] + each[status_col + 1:] for each in data]
    # elif submission_log_type in [SurveyResponseRouter.SUCCESS]:
    #     return [each[submission_id_col + 1:status_col] + each[reply_sms_col + 1:] for each in data]
    # else:



# def _empty_if_no_data(list, index):
#     return '' if len(list) < index + 1 else list[index]

# def format_field_values_for_excel(row, form_model):
#     changed_row = dict()
#     for question_code, question_value in row[-1].iteritems():
#         revision = row[0]
#         field = form_model.get_field_by_code_and_rev(question_code, revision)
#         if field:
#             changed_row[question_code] = field.formatted_field_values_for_excel(question_value)
#         else:
#             changed_row[question_code] = question_value
#     return changed_row
