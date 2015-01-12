from tempfile import NamedTemporaryFile
import tempfile
import zipfile
import math
import xlsxwriter

from django.core.servers.basehttp import FileWrapper

from django.http import HttpResponse
import xlwt
from django.template.defaultfilters import slugify


from datawinners.workbook_utils import workbook_add_sheet, workbook_add_sheets, workbook_add_header, workbook_add_row
from datawinners.workbook_utils import worksheet_add_header
from mangrove.form_model.field import ExcelDate


def add_sheet_with_data(raw_data, headers, workbook, formatter, sheet_name_prefix=None):
    ws = workbook.add_worksheet(name=sheet_name_prefix)
    worksheet_add_header(ws, headers, get_header_style(workbook))
    date_formats = {}

    for row_number, row in enumerate(raw_data):
        if formatter:
            row = formatter.format_row(row['_source'])
        for column, val in enumerate(row):
            if isinstance(val, ExcelDate):
                if not date_formats.has_key(val.date_format):
                    date_format = {'submission_date': 'mmm d yyyy hh:mm:ss'}.get(val.date_format, val.date_format)
                    date_formats.update({val.date_format: workbook.add_format({'num_format': date_format})})
                ws.write(row_number + 1, column, val.date.replace(tzinfo=None), date_formats.get(val.date_format))

            elif isinstance(val, float):
                ws.write_number(row_number + 1, column, val)
            else:
                ws.write(row_number + 1, column, val)

def create_non_zipped_response(excel_workbook, file_name):
    file_name_normalized = slugify(file_name)
    response = HttpResponse(mimetype="application/vnd.ms-excel")
    response['Content-Disposition'] = 'attachment; filename="%s.xls"' % (file_name_normalized)
    excel_workbook.save(response)
    return response


def create_excel_response(headers, raw_data_list, file_name):
    response = HttpResponse(mimetype="application/vnd.ms-excel")
    response['Content-Disposition'] = 'attachment; filename="%s.xls"' % (slugify(file_name),)

    wb = xlwt.Workbook()
    add_sheet_with_data(raw_data_list, headers, wb, 'data_log')

    wb.save(response)
    return response

def get_header_style(workbook):
    header_style = workbook.add_format({'bold': True})
    header_style.set_font_name("Helvetica")
    header_style.set_align('center')
    header_style.set_align('vcenter')
    header_style.set_text_wrap('right')
    return header_style

def export_to_new_excel(headers, raw_data, file_name, formatter=None):
    file_name_normalized = slugify(file_name)
    import io
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    if isinstance(headers, dict):
        for sheet_name, header_row in headers.items():
            add_sheet_with_data(raw_data.get(sheet_name, []), header_row, workbook, formatter, sheet_name)
    else:
        add_sheet_with_data(raw_data, headers, workbook, formatter)
    workbook.close()

    output.seek(0)
    response = HttpResponse(output.read(), mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    response['Content-Disposition'] = "attachment; filename=%s.xlsx" % file_name_normalized

    return response


def create_excel_sheet_with_data(raw_data_list, headers, wb, sheet_name_prefix, formatter):
    total_column_count = len(headers)
    number_of_sheets = math.ceil(total_column_count / 256.0)
    workbook_add_sheets(wb, number_of_sheets, sheet_name_prefix)
    workbook_add_header(wb, headers, number_of_sheets)
    for row_number, row in enumerate(raw_data_list):
        if row_number == 20000:
            #export limit set to 20K after performance exercise
            #since scan & scroll API does not support result set size the workaround is to handle it this way
            return
        row = formatter.format_row(row['_source'])
        workbook_add_row(wb, row, number_of_sheets, row_number + 1)


def export_to_zipped_excel(headers, raw_data, file_name, formatter):
    wb = xlwt.Workbook()
    create_excel_sheet_with_data(raw_data, headers, wb, 'data_log', formatter)
    return create_zipped_response(wb, file_name)

def export_to_excel_no_zip(headers, raw_data, file_name, formatter):
    wb = xlwt.Workbook()
    create_excel_sheet_with_data(raw_data, headers, wb, 'data_log', formatter)
    return create_non_zipped_response(wb, file_name)


def export_filename(submission_type, project_name):
    suffix = submission_type + '_log' if submission_type else 'analysis'
    file_name = "%s_%s" % (project_name, suffix)
    return file_name

def export_media_folder_name(submission_type, project_name):
    suffix = submission_type + '_log' if submission_type else 'analysis'
    folder_name = "%s_MediaFiles_%s" % (project_name, suffix)
    return folder_name
