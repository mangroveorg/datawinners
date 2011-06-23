# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import xlwt
from datetime import datetime

def clean_date(date_val):
    new_date_val = date_val.replace(tzinfo=None)
    return new_date_val

def clean(row):
    new_row = []
    for each in row:
        if type(each) is datetime:
            each = clean_date(each)
        new_row.append(each)
    return new_row

def get_excel_sheet(raw_data, sheet_name):
    wb = xlwt.Workbook()
    ws = wb.add_sheet(sheet_name)
    for row_number, row  in enumerate(raw_data):
        row = clean(row)
        for col_number, val in enumerate(row):
            ws.write(row_number, col_number, val)
    return wb