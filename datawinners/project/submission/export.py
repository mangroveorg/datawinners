from tempfile import NamedTemporaryFile
import tempfile
import zipfile
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse
import math
import xlwt
from datawinners import utils
from django.template.defaultfilters import slugify


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


def _create_zip_file(file_name_normalized, temporary_excel_file):
    zip_file = tempfile.TemporaryFile()
    archive = zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED)
    archive.write(temporary_excel_file.name, compress_type=zipfile.ZIP_DEFLATED,
                  arcname="%s.xls" % file_name_normalized)
    archive.close()
    return zip_file


def zip_excel_workbook(excel_workbook, file_name):
    file_name_normalized = slugify(file_name)
    temporary_excel_file = NamedTemporaryFile(suffix=".xls", delete=False)
    excel_workbook.save(temporary_excel_file)
    temporary_excel_file.flush()
    temporary_excel_file.close()
    zip_file = _create_zip_file(file_name_normalized, temporary_excel_file)
    response = HttpResponse(FileWrapper(zip_file, blksize=8192000), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="%s.zip"' % (file_name_normalized,)
    response['Content-Length'] = zip_file.tell()
    zip_file.seek(0)
    return response


def create_excel_response(headers, raw_data_list, file_name):
    response = HttpResponse(mimetype="application/vnd.ms-excel")
    response['Content-Disposition'] = 'attachment; filename="%s.xls"' % (slugify(file_name),)

    wb = xlwt.Workbook()
    add_sheet_with_data(raw_data_list, headers, wb, 'data_log')

    wb.save(response)
    return response


def create_zipped_excel_response(headers, raw_data_list, file_name):
    wb = xlwt.Workbook()
    add_sheet_with_data(raw_data_list, headers, wb, 'data_log')
    return zip_excel_workbook(wb, file_name)


def export_filename(submission_type, project_name):
    suffix = submission_type + '_log' if submission_type else 'analysis'
    file_name = "%s_%s" % (project_name, suffix)
    return file_name