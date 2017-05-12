import os
import pyexcel as pe

from pyexcel.ext import xlsx #This import is needed for loading excel. Please don't remove them
from pyexcel.ext import xls #This import is needed for loading excel. Please don't remove them
from collections import OrderedDict

XLSFORM_PREDEFINED_COLUMN_NAMES={
                                 "survey": ['type','name','label','calculation','hint','required','appearance','constraint','constraint_message','relevant','default', 'choice_filter','required_message'],
                                 "choices": ['list_name','name', 'label']
                                 }
XLSFORM_EXCLUDE_COLUMN_NAMES={
                              "cascades":['base_index']
                              }
XLSFORM_EXCLUDE_FOR_DEFAULT=['begin_group','end_group', 'begin repeat', 'end repeat', 'note']

def purify_posted_data(excel_as_dict):
    for survey in excel_as_dict['survey']:
        if survey['type'] in XLSFORM_EXCLUDE_FOR_DEFAULT:
            if survey['default'] and survey['default'].strip():
                try:
                    del survey['default']
                except KeyError:
                    pass
    return excel_as_dict

def convert_excel_to_dict(file_name=None, file_content=None, file_type='xlsx'):
    book = pe.get_book(file_name=file_name, file_content=file_content, file_type=file_type)
    excel_as_dict = OrderedDict()
    for sheet in book:
        records = []
        if len(sheet.array) > 0:
            sheet.name_columns_by_row(0)
            if sheet.name == 'survey':
                _add_supported_attributes_that_doesnt_exists(sheet)
            records = _to_records(sheet)
        excel_as_dict[sheet.name] = records
    return excel_as_dict

def convert_json_to_excel(json_as_dict, file_type='xlsx'):
    book_content = OrderedDict()
    for sheet_name in json_as_dict:
        book_content[sheet_name] = convert_json_record_to_array(
                                                                json_as_dict[sheet_name], 
                                                                sheet_name,
                                                                XLSFORM_PREDEFINED_COLUMN_NAMES.get(sheet_name),
                                                                XLSFORM_EXCLUDE_COLUMN_NAMES.get(sheet_name)
                                                                )
    excel_raw_stream = pe.save_book_as(dest_file_type=file_type, bookdict=book_content)

    return excel_raw_stream

def convert_json_record_to_array(records, sheet_name, xlsform_predefined_column_names=None, xlsform_exclude_column_names=None):
    rows = []
    if len(records) < 1:
        if xlsform_predefined_column_names:
            rows.append(xlsform_predefined_column_names)
            empty_content = ['' for k in xlsform_predefined_column_names]
            rows.append(empty_content)
        return rows
    else:
        keys = records[0].keys()
        if xlsform_predefined_column_names:
            column_names = [k for k in keys if k in xlsform_predefined_column_names]
        elif xlsform_exclude_column_names:
            column_names = [k for k in keys if k not in xlsform_exclude_column_names]
        else:
            column_names = keys
        rows.append(column_names)
        for r in records:
            row = []
            for k in column_names:
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
        
def _add_supported_attributes_that_doesnt_exists(sheet):
    supported_attributes_that_doesnt_exists = list(set(XLSFORM_PREDEFINED_COLUMN_NAMES[sheet.name]) - set(sheet.colnames))
    additional_data = list()
    additional_data.append(supported_attributes_that_doesnt_exists)
    for row in sheet.rows():
        additional_data.append(['' for x in supported_attributes_that_doesnt_exists])

    additional_supported_attr_sheet = pe.Sheet(additional_data)
    sheet.column += additional_supported_attr_sheet
    

