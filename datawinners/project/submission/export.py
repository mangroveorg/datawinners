import logging
from django.http import HttpResponse
import math
import resource
import xlwt
from datawinners import utils
from django.template.defaultfilters import slugify

logger = logging.getLogger("datawinners")


def add_sheet_with_data(raw_data_list, headers, wb, sheet_name_prefix):
    data_list = [headers] + raw_data_list
    total_column_count = len(headers)
    number_of_sheets = math.ceil(total_column_count / 256.0)
    sheet_number = 1
    column_number = 1
    get_sheet_name = lambda: '%s_%d' % (sheet_name_prefix, sheet_number) if number_of_sheets > 1 else sheet_name_prefix

    while sheet_number <= number_of_sheets:
        data_list_with_max_allowed_columns = [l[column_number - 1: column_number + 255] for l in data_list]
        utils.workbook_add_sheet(wb, data_list_with_max_allowed_columns, get_sheet_name())
        column_number += 256
        sheet_number += 1


def create_excel_response(headers, raw_data_list, file_name):
    response = HttpResponse(mimetype="application/vnd.ms-excel")
    response['Content-Disposition'] = 'attachment; filename="%s.xls"' % (slugify(file_name),)

    wb = xlwt.Workbook()
    add_sheet_with_data(raw_data_list, headers, wb, 'data_log')

    wb.save(response)

    logger.error('Memory before response: %s (kb)' % resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)

    return response

def export_filename(submission_type, project_name):
    suffix = submission_type + '_log' if submission_type else 'analysis'
    file_name = "%s_%s" % (project_name, suffix)
    return file_name