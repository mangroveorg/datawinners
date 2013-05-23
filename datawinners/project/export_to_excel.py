from django.http import HttpResponse


import datawinners.utils as utils
from datawinners.project.survey_response_router import SurveyResponseRouter

def _create_excel_response(raw_data_list, file_name):
    response = HttpResponse(mimetype="application/vnd.ms-excel")
    from django.template.defaultfilters import slugify

    response['Content-Disposition'] = 'attachment; filename="%s.xls"' % (slugify(file_name),)
    wb = utils.get_excel_sheet(raw_data_list, 'data_log')
    wb.save(response)
    return response


def _prepare_export_data(submission_type, project_name, header_list, formatted_values):
    exported_data = _get_exported_data(header_list, formatted_values, submission_type)
    suffix = submission_type + '_log' if submission_type else 'analysis'
    file_name = "%s_%s" % (project_name, suffix)
    return exported_data, file_name


def _get_exported_data(header, formatted_values, submission_log_type):
    data = [header] + formatted_values
    submission_id_col = 0
    status_col = 4
    reply_sms_col = 5
    if submission_log_type in [SurveyResponseRouter.ALL, SurveyResponseRouter.DELETED]:
        return [each[submission_id_col + 1:reply_sms_col] + each[reply_sms_col + 1:] for each in data]
    elif submission_log_type in [SurveyResponseRouter.ERROR]:
        return [each[submission_id_col + 1:status_col] + each[status_col + 1:] for each in data]
    elif submission_log_type in [SurveyResponseRouter.SUCCESS]:
        return [each[submission_id_col + 1:status_col] + each[reply_sms_col + 1:] for each in data]
    else:
        return [each[1:] for each in data]


def _empty_if_no_data(list, index):
    return '' if len(list) < index + 1 else list[index]

def format_field_values_for_excel(row, form_model):
    changed_row = dict()
    for question_code, question_value in row[-1].iteritems():
        revision = row[0]
        field = form_model.get_field_by_code_and_rev(question_code, revision)
        if field:
            changed_row[question_code] = field.formatted_field_values_for_excel(question_value)
        else:
            changed_row[question_code] = question_value
    return changed_row
