from datetime import datetime

import xlwt

from mangrove.form_model.field import ExcelDate


VAR = "HNI"
SUBMISSION_DATE_QUESTION = u'Submission Date'
WIDTH_ONE_CHAR = 256
MAX_COLUMN_WIDTH_IN_CHAR = 65
BUFFER_WIDTH = 3
MAX_ROWS_IN_MEMORY = 500
EXCEL_CELL_FLOAT_STYLE = xlwt.easyxf(num_format_str='#0.0###')
EXCEL_CELL_INTEGER_STYLE = xlwt.easyxf(num_format_str='#0')
EXCEL_DATE_STYLE = {'mm.yyyy': xlwt.easyxf(num_format_str='MMM, YYYY'),
                    'dd.mm.yyyy': xlwt.easyxf(num_format_str='MMM DD, YYYY'),
                    'mm.dd.yyyy': xlwt.easyxf(num_format_str='MMM DD, YYYY'),
                    'yyyy': xlwt.easyxf(num_format_str='YYYY'),
                    'submission_date': xlwt.easyxf(num_format_str='MMM DD, YYYY hh:mm:ss')}


def workbook_add_sheets(wb, number_of_sheets, sheet_name_prefix):
    sheet_number = 1
    column_number = 1
    get_sheet_name = lambda: '%s_%d' % (sheet_name_prefix, sheet_number) if number_of_sheets > 1 else sheet_name_prefix

    while sheet_number <= number_of_sheets:
        wb.add_sheet(get_sheet_name())
        column_number += 256
        sheet_number += 1


def get_header_style(workbook, type=None):
    header_style = workbook.add_format({'bold':True})
    header_style.set_font_name("Helvetica")
    header_style.set_align('center')
    header_style.set_text_wrap('right')
    if type is None:
        return header_style

    header_style.set_text_wrap()

    brown = workbook.add_format({'color':'brown'})
    brown.set_font_name("Helvetica")
    brown.set_align('vjustify')

    italic = workbook.add_format({'italic':True, 'color':'gray'})

    gray = workbook.add_format({'color':'gray'})
    gray.set_font_name("Helvetica")
    gray.set_align('vcenter')
    
    return header_style, brown, italic, gray


def colToExcel(col): # col is 1 based
    excelCol = str()
    div = col
    while div:
        (div, mod) = divmod(div-1, 26) # will return (x, 0 .. 25)
        excelCol = chr(mod + 65) + excelCol

    return excelCol


def worksheet_add_header(worksheet, headers, workbook, browser=None, offset=0):
    for column, header in enumerate(headers):
        if isinstance(header, tuple):
            header_styles = get_header_style(workbook, "Template")
            max_width = max([len(item) for item, style_object in header]) + BUFFER_WIDTH
            max_width = min(max_width, MAX_COLUMN_WIDTH_IN_CHAR)
            worksheet.set_row(0, 100)
            wrap_text = workbook.add_format({'text_wrap': True})
            column_in_letter = colToExcel(column+1)
            worksheet.set_column("%s:%s" % (column_in_letter, column_in_letter), max_width/1.5, wrap_text)
            if isinstance(browser, str) and "Mac OS" in browser:
                label, instruction, exemple = header[0][0].replace("\n", "\n\r"), header[1][0].replace("\n", "\n\r"), \
                                              header[2][0].replace("\n", " \n\r")
            else:
                label, instruction, exemple = header[0][0], header[1][0], header[2][0]
            worksheet.write_rich_string(0, column, header_styles[0], label, header_styles[1], instruction,
                                        header_styles[2], exemple)

        else:
            worksheet.set_row(0, 50)
            worksheet.write(0, offset + column, header, get_header_style(workbook))

def workbook_add_header(wb, headers, number_of_sheets):
    style = xlwt.easyxf('borders: top double, bottom double, right double')
    algn = xlwt.Alignment()
    algn.wrap = 1
    style.alignment = algn
    column_number = 1
    sheet_number = 1
    row_number = 0
    while sheet_number <= number_of_sheets:
        ws = wb.get_sheet(sheet_number - 1)
        data_list_with_max_allowed_columns = headers[column_number - 1: column_number + 255]
        column_number += 256
        sheet_number += 1
        for col_number, val in enumerate(data_list_with_max_allowed_columns):
            if isinstance(val, tuple):
                max_width = max([len(item) for item, style_object in val]) + BUFFER_WIDTH
                max_width = min(max_width, MAX_COLUMN_WIDTH_IN_CHAR)
                ws.col(col_number).width = WIDTH_ONE_CHAR * max_width
                ws.row(row_number).height = WIDTH_ONE_CHAR * 5
                ws.write_rich_text(row_number, col_number, val, style)
            else:
                ws.row(row_number).height = WIDTH_ONE_CHAR * 4
                ws.write(row_number, col_number, val, _header_style())


def workbook_add_row(wb, data, number_of_sheets, row_number):
    column_number = 1
    sheet_number = 1
    while sheet_number <= number_of_sheets:
        ws = wb.get_sheet(sheet_number - 1)
        data_list_with_max_allowed_columns = data[column_number - 1: column_number + 255]
        column_number += 256
        sheet_number += 1
        if row_number % MAX_ROWS_IN_MEMORY == 0:
            ws.flush_row_data()
            ws.row_tempfile.flush()
        row = _clean(data_list_with_max_allowed_columns)
        write_row_to_worksheet(ws, row, row_number)


def _clean(row):
    new_row = []
    for each in row:
        if type(each) is datetime:
            each = _clean_date(each)
        new_row.append(each)
    return new_row


def _clean_date(date_val):
    new_date_val = date_val.replace(tzinfo=None)
    return new_date_val


def _header_style():
    my_font = xlwt.Font()
    my_font.name = 'Helvetica Bold'
    my_font.bold = True
    my_alignment = xlwt.Alignment()
    my_alignment.vert = my_alignment.VERT_CENTER
    my_alignment.wrap = my_alignment.WRAP_AT_RIGHT
    header_style = xlwt.easyxf()
    header_style.font = my_font
    header_style.alignment = my_alignment
    return header_style


def workbook_add_sheet(wb, raw_data, sheet_name):
    ws = wb.add_sheet(sheet_name)

    for row_number, row in enumerate(raw_data):
        if row_number == 0:
            row = _clean(row)
            style = xlwt.easyxf('borders: top double, bottom double, right double')
            algn = xlwt.Alignment()
            algn.wrap = 1
            style.alignment = algn

            for col_number, val in enumerate(row):
                if isinstance(val, tuple):
                    max_width = max([len(item) for item, style_object in val])+BUFFER_WIDTH
                    max_width = min(max_width,MAX_COLUMN_WIDTH_IN_CHAR)
                    ws.col(col_number).width = WIDTH_ONE_CHAR * max_width
                    ws.row(row_number).height = WIDTH_ONE_CHAR * 5
                    ws.write_rich_text(row_number, col_number, val, style)
                else:
                    ws.row(row_number).height = WIDTH_ONE_CHAR * 4
                    ws.write(row_number, col_number, val, _header_style())

        else:
            if row_number > 0 and row_number % MAX_ROWS_IN_MEMORY == 0:
                ws.flush_row_data()
            row = _clean(row)
            write_row_to_worksheet(ws, row, row_number)
    return ws


def get_excel_sheet(raw_data, sheet_name):
    wb = xlwt.Workbook()
    workbook_add_sheet(wb, raw_data, sheet_name)
    return wb


def write_row_to_worksheet(ws, row, row_number):
    for col_number, val in enumerate(row):
        if isinstance(val, ExcelDate):
            ws.col(col_number).width = WIDTH_ONE_CHAR * (len(str(val.date)) + BUFFER_WIDTH)
            ws.write(row_number, col_number, val.date.replace(tzinfo=None),
                style=EXCEL_DATE_STYLE.get(val.date_format))
        elif isinstance(val, float):
            cell_format = EXCEL_CELL_FLOAT_STYLE
            if(int(val) == val):
                cell_format = EXCEL_CELL_INTEGER_STYLE
            ws.write(row_number, col_number, val, style=cell_format)
        else:
            ws.write(row_number, col_number, val, style=xlwt.Style.default_style)