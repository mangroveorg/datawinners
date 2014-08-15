from django.http import HttpResponse
import math
import xlwt
from datawinners import utils
from django.template.defaultfilters import slugify


def create_excel_response(headers, raw_data_list, file_name):
    response = HttpResponse(mimetype="application/vnd.ms-excel")
    response['Content-Disposition'] = 'attachment; filename="%s.xls"' % (slugify(file_name),)

    wb = xlwt.Workbook()
    data_list = [headers] + raw_data_list
    total_column_count = len(headers)
    number_of_sheets = math.ceil(total_column_count / 256.0)
    sheet_number = 1
    column_number = 1

    while sheet_number <= number_of_sheets:
        data_list_with_max_allowed_columns = [l[column_number-1: column_number+255] for l in data_list]
        utils.workbook_add_sheet(wb, data_list_with_max_allowed_columns, 'data_log_%d' % sheet_number)
        column_number += 256
        sheet_number += 1

    wb.save(response)
    return response

def export_filename(submission_type, project_name):
    suffix = submission_type + '_log' if submission_type else 'analysis'
    file_name = "%s_%s" % (project_name, suffix)
    return file_name