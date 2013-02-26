from django.http import HttpResponse
from mangrove.form_model.field import SelectField, IntegerField, GeoCodeField, DateField

from project.helper import _to_str
from project.submission_router import SubmissionRouter

import datawinners.utils as utils

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
    if submission_log_type in [SubmissionRouter.ALL, SubmissionRouter.DELETED]:
        return [each[submission_id_col + 1:reply_sms_col] + each[reply_sms_col + 1:] for each in data]
    elif submission_log_type in [SubmissionRouter.ERROR]:
        return [each[submission_id_col + 1:status_col] + each[status_col + 1:] for each in data]
    elif submission_log_type in [SubmissionRouter.SUCCESS]:
        return [each[submission_id_col + 1:status_col] + each[reply_sms_col + 1:] for each in data]
    else:
        #for analysis page
        return [each[1:] for each in data]


def format_field_values_for_excel(row, form_model):
    changed_row = dict()
    for question_code, question_value in row[-1].iteritems():
        field = form_model.get_field_by_code_and_rev(question_code, row[0])
        if isinstance(field, SelectField):
            row[-1][question_code] = field.get_option_value_list(question_value)
            changed_row[question_code] = row[-1][question_code]
        elif isinstance(field, IntegerField):
            try:
                row[-1][question_code] = float(question_value)
                changed_row[question_code] = row[-1][question_code]
            except ValueError:
                changed_row[question_code] = question_value
        elif isinstance(field, GeoCodeField):
            formatted_question_value = question_value.replace(',', ' ')
            changed_row[field.code + '_lat'] = formatted_question_value.split(' ')[0]
            changed_row[field.code + '_long'] = formatted_question_value.split(' ')[1]
        elif isinstance(field, DateField):
            row[-1][question_code] = _to_str(question_value, field)
            changed_row[question_code] = row[-1][question_code]
        else:
            changed_row[question_code] = question_value
    return changed_row