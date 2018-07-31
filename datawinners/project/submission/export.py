import tempfile
import math

import xlsxwriter

from django.core.servers.basehttp import FileWrapper

from django.http import HttpResponse
import xlwt
from django.template.defaultfilters import slugify


from datawinners.workbook_utils import workbook_add_sheet, workbook_add_sheets, workbook_add_header, workbook_add_row
from datawinners.workbook_utils import worksheet_add_header
from mangrove.form_model.field import ExcelDate
from datawinners.project.submission.analysis_helper import enrich_analysis_data
from mangrove.form_model.form_model import EntityFormModel


def add_sheet_with_data(raw_data, headers, workbook, formatter=None, sheet_name_prefix=None, browser=None, questionnaire=None):
    ws = workbook.add_worksheet(name=sheet_name_prefix)
    worksheet_add_header(ws, headers, workbook, browser)
    date_formats = {}

    for row_number, row in enumerate(raw_data):
        if questionnaire and formatter and not isinstance(questionnaire, EntityFormModel):
            #For advanced transformation
            row = enrich_analysis_data(row['_source'], questionnaire, row['_id'], is_export=True)
            row = formatter.format_row(row)
        elif formatter:
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


def get_header_style(workbook):
    header_style = workbook.add_format({'bold': True})
    header_style.set_font_name("Helvetica")
    header_style.set_align('center')
    header_style.set_align('vcenter')
    header_style.set_text_wrap('right')
    return header_style


def create_multi_sheet_excel_headers(excel_headers, workbook):
    for sheet_name, headers in excel_headers.iteritems():
        if not headers:
            continue
        ws = workbook.add_worksheet(name=sheet_name)
        worksheet_add_header(ws, headers, workbook, get_header_style(workbook))


def _remove_relating_columns(headers):
    headers.remove('_index')
    headers.remove('_parent_index')


def create_single_sheet_excel_headers(excel_headers, workbook):
    ws = workbook.add_worksheet(name='main')
    offset = 0
    for sheet_name, headers in excel_headers.iteritems():
        if not headers:
            continue
        worksheet_add_header(ws, headers, workbook, get_header_style(workbook), offset)
        offset += len(headers)


def create_multi_sheet_entries(raw_data, workbook, excel_headers, row_count_dict):
    date_formats = {}

    for sheet_name, data in raw_data.iteritems():
        if sheet_name not in excel_headers:
            continue
        ws = workbook.worksheets()[excel_headers[sheet_name]]
        for row in raw_data[sheet_name]:
            for column, val in enumerate(row):
                row_number = row_count_dict[sheet_name]
                if isinstance(val, ExcelDate):
                    if not date_formats.has_key(val.date_format):
                        date_format = {'submission_date': 'mmm d yyyy hh:mm:ss'}.get(val.date_format, val.date_format)
                        date_formats.update({val.date_format: workbook.add_format({'num_format': date_format})})
                    ws.write(row_number + 1, column, val.date.replace(tzinfo=None), date_formats.get(val.date_format))

                elif isinstance(val, float):
                    ws.write_number(row_number + 1, column, val)
                else:
                    ws.write(row_number + 1, column, val)
            row_count_dict[sheet_name] += 1


def create_single_sheet_entries(raw_data, workbook, row_count_dict):
    date_formats = {}
    ws = workbook.worksheets()[0]
    flattened_rows = _flatten_repeat_rows(raw_data['main'][0])
    last_row_number = row_count_dict['main']
    for index, row in enumerate(flattened_rows):
        row_number = last_row_number + index + 1
        for column, val in enumerate(row):
            if isinstance(val, ExcelDate):
                if not date_formats.has_key(val.date_format):
                    date_format = {'submission_date': 'mmm d yyyy hh:mm:ss'}.get(val.date_format, val.date_format)
                    date_formats.update({val.date_format: workbook.add_format({'num_format': date_format})})
                ws.write(row_number, column, val.date.replace(tzinfo=None), date_formats.get(val.date_format))
            elif isinstance(val, float):
                ws.write_number(row_number, column, val)
            else:
                ws.write(row_number, column, val)

    row_count_dict['main'] += len(flattened_rows)


def _flatten_repeat_rows(raw_data):
    flattened_rows = []
    result = []
    repeated_data = []

    for val in raw_data:
        if isinstance(val, list):
            repeated_data.append({'row_index': len(result), 'data': val})
            max_number_of_columns_for_repeat = max([len(item) for item in val])
            [result.append('') for i in range(max_number_of_columns_for_repeat)]
        else:
            result.append(val)

    submission_unique_id = result[0]
    # Merging First Repeat with the base data
    _split_repeated_data(repeated_data, result, 0)
    flattened_rows.append(result)

    if repeated_data:
        total_number_of_rows = max([len(item['data']) for item in repeated_data])
        # splitting further repeats as separate rows
        for row_index in range(total_number_of_rows):
            row = ['' for i in range(len(result))]
            _split_repeated_data(repeated_data, row, row_index + 1)

            if any(row):
                row[0] = submission_unique_id
                flattened_rows.append(row)
    return flattened_rows


def _split_repeated_data(repeated_data, row, row_index):
    for repeated_datum in repeated_data:
        if len(repeated_datum['data']) > row_index:
            start_column_index = repeated_datum['row_index']
            for index, val in enumerate(repeated_datum['data'][row_index]):
                row[index + start_column_index] = val


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
    data = [headers]
    data.extend(raw_data_list)
    workbook_add_sheet(wb, data, file_name)

    wb.save(response)
    return response

def export_to_new_excel(headers, raw_data, file_name, formatter=None, hide_codes_sheet=False, browser=None, questionnaire=None):
    file_name_normalized = slugify(file_name)
    output = tempfile.TemporaryFile()
    workbook = xlsxwriter.Workbook(output, {'constant_memory': True})
    if isinstance(headers, dict):
        for sheet_name, header_row in headers.items():
            add_sheet_with_data(raw_data.get(sheet_name, []), header_row, workbook, formatter, sheet_name, browser, questionnaire=questionnaire)
    else:
        add_sheet_with_data(raw_data, headers, workbook, formatter, questionnaire=questionnaire)
    if hide_codes_sheet:
        worksheets = workbook.worksheets()
        codes_sheet = worksheets[workbook._get_sheet_index('codes')]
        codes_sheet.hide()
    workbook.close()
    output.seek(0)
    response = HttpResponse(FileWrapper(output), mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    response['Content-Disposition'] = "attachment; filename=%s.xlsx" % file_name_normalized

    return response

def failed_export_to_new_excel(file_name, headers, raw_data):
    file_name_normalized = slugify(file_name)
    output = tempfile.TemporaryFile()
    workbook = xlsxwriter.Workbook(output, {'constant_memory': True})
    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({'bold': True})
    date_format = workbook.add_format({'num_format': 'dd/mm/yy hh:mm'})

    col = 0

    for label in headers:
        worksheet.write(0, col, label, bold)
        col += 1

    row = 1
    col = 0

    for log in raw_data:
        for item in log:
            if col == 1:
                worksheet.write(row, col, item, date_format)
            else:
                worksheet.write(row, col, item)
            col += 1
        row += 1
        col = 0

    workbook.close()
    output.seek(0)
    response = HttpResponse(FileWrapper(output), mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

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

#I believe this method is never used. Validate and remove
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
    folder_name = "%s_MediaFiles_%s" % (slugify(project_name), suffix)
    return folder_name
