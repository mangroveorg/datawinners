import os
import pyexcel as pe

from pyexcel.ext import xlsx #This import is needed for loading excel. Please don't remove them
from pyexcel.ext import xls #This import is needed for loading excel. Please don't remove them
from collections import OrderedDict

XLSFORM_PREDEFINED_COLUMN_NAMES={
                                 "survey": ['type','name','label','calculation','hint','required','appearance','constraint','relevant'],
                                 "choices": ['list name', 'name', 'label']
                                 }
def convert_excel_to_dict(file_name=None, file_content=None, file_type='xlsx'):
    book = pe.get_book(file_name=file_name, file_content=file_content, file_type=file_type)
    excel_as_dict = OrderedDict()
    
    for sheet in book:
        sheet.name_columns_by_row(0)
        records = _to_records(sheet) #sheet.to_records()
        excel_as_dict[sheet.name] = records
    return excel_as_dict

def convert_json_to_excel(json_as_dict, file_type='xlsx'):
#     save_file_name = '/Users/sairamk/temp/sandbox/test_output.xlsx' 
    book_content = OrderedDict()
    for sheet_name in json_as_dict:
        book_content[sheet_name] = convert_json_record_to_array(
                                                                json_as_dict[sheet_name], 
                                                                XLSFORM_PREDEFINED_COLUMN_NAMES.get(sheet_name))
#     pe.save_book_as(dest_file_name=save_file_name, bookdict=book_content)
    excel_raw_stream = pe.save_book_as(dest_file_type=file_type, bookdict=book_content)

    return excel_raw_stream

def convert_json_record_to_array(records, xlsform_predefined_column_names=None):
    rows = []
    if len(records) < 1:
        return rows
    else:
        keys = records[0].keys()
        if xlsform_predefined_column_names:
            column_names = [k for k in keys if k in xlsform_predefined_column_names]
            rows.append(column_names)
        else:
            rows.append(keys)
        for r in records:
            row = []
            for k in keys:
                row.append(r[k])
            rows.append(row)
    return rows

def _to_records(reader):
    """
    Make an array of dictionaries.
    This is a trimmed down version of pyexcel.utils -> to_records. This adds support for Ordered dictionary.
    """
    ret = []
    if len(reader.colnames) > 0:
        headers = reader.colnames
        for row in reader.rows():
            the_dict = OrderedDict(zip(headers, row))
            ret.append(the_dict)
    else:
        raise ValueError('Unable to convert excel to json due to invalid excel structure')
    return ret

def _yield_from_records(records):
    """Reverse function of to_records
        Trimmed down version of pyexcel.utils -> to_records.
    """
    if len(records) < 1:
        yield []
    else:
        keys = records[0].keys()
        yield list(keys)
        for r in records:
            row = []
            for k in keys:
                row.append(r[k])
            yield row

