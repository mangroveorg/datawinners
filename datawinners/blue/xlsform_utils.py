import os
import pyexcel as pe
from pyexcel.ext import xlsx
from collections import OrderedDict

def convert_excel_to_dict(file_name=None, file_content=None, file_type='xlsx'):
    book = pe.get_book(file_name=file_name, file_content=file_content, file_type=file_type)
    excel_as_dict = OrderedDict()
    
    for sheet in book:
        sheet.name_columns_by_row(0)
        records = sheet.to_records()
        excel_as_dict[sheet.name] = records
    return excel_as_dict

def convert_json_to_excel(json):
#     should convert json to temp file and return back that file
    pass