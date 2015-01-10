from collections import OrderedDict
from datetime import datetime
import json

from django.http import HttpResponse
from django.template.defaultfilters import slugify
import xlwt

from datawinners.project.submission.export import export_filename, add_sheet_with_data, export_to_new_excel
from datawinners.project.submission.exporter import SubmissionExporter
from datawinners.project.submission.formatter import SubmissionFormatter
from mangrove.form_model.field import ExcelDate, DateField


class XFormSubmissionExporter(SubmissionExporter):
    def _create_zipped_response(self, columns, submission_list, submission_type):
        headers, data_rows_dict = AdvanceSubmissionFormatter(columns, self.form_model,
                                                             self.local_time_delta).format_tabular_data(submission_list)
        return self._create_excel_response(headers, data_rows_dict, export_filename(submission_type, self.project_name))

    def _create_excel_response(self, columns, submission_list, submission_type):
        response = HttpResponse(mimetype="application/vnd.ms-excel")
        file_name = export_filename(submission_type, self.project_name)
        response['Content-Disposition'] = 'attachment; filename="%s.xls"' % (slugify(file_name),)
        headers, data_rows_dict = AdvanceSubmissionFormatter(columns, self.form_model,
                                                             self.local_time_delta).format_tabular_data(submission_list)
        wb = xlwt.Workbook()
        for sheet_name, header_row in headers.items():
            add_sheet_with_data(data_rows_dict.get(sheet_name, []), header_row, wb, sheet_name)
        wb.save(response)
        return response

    def _create_response(self, columns, submission_list, submission_type):
        headers, data_rows_dict = AdvanceSubmissionFormatter(columns, self.form_model, self.local_time_delta).format_tabular_data(submission_list)
        return export_to_new_excel(headers, data_rows_dict, export_filename(submission_type, self.project_name))
        

GEODCODE_FIELD_CODE = "geocode"
FIELD_SET = "field_set"


class AdvanceSubmissionFormatter(SubmissionFormatter):
    def __init__(self, columns, form_model, local_time_delta):
        super(AdvanceSubmissionFormatter, self).__init__(columns, local_time_delta)
        self.form_model = form_model

    def append_relating_columns(self, cols):
        cols.append('_index')
        cols.append('_parent_index')

    def format_tabular_data(self, submission_list):

        repeat_headers = OrderedDict()
        repeat_headers.update({'main': ''})
        headers = self._format_tabular_data(self.columns, repeat_headers)

        formatted_values, formatted_repeats = [], {}
        for row_number, row_dict in enumerate(submission_list):

            if row_number == 20000:
            #export limit set to 20K after performance exercise
            #since scan & scroll API does not support result set size the workaround is to handle it this way
                break

            result = self._format_row(row_dict['_source'], row_number, formatted_repeats)
            if self.form_model.has_nested_fields:
                result.append(row_number + 1)
            formatted_values.append(result)

        if self.form_model.has_nested_fields:
            self.append_relating_columns(headers)

        repeat_headers.update({'main': headers})
        formatted_repeats.update({'main': formatted_values})
        return repeat_headers, formatted_repeats

    def _get_repeat_col_name(self, label):
        return slugify(label)[:20]

    def _format_tabular_data(self, columns, repeat):
        headers = []
        for col_def in columns.values():
            if col_def.get('type', '') == GEODCODE_FIELD_CODE:
                headers.append(col_def['label'] + " Latitude")
                headers.append(col_def['label'] + " Longitude")
            elif col_def.get('type', '') == FIELD_SET:
                _repeat = self._format_tabular_data(col_def['fields'], repeat)
                self.append_relating_columns(_repeat)
                repeat.update({self._get_repeat_col_name(col_def['label']): _repeat})
            else:
                headers.append(col_def['label'])
        return headers

    def _format_row(self, row, i, formatted_repeats):
        return self.__format_row(row, self.columns, i, formatted_repeats)

    def _add_repeat_data(self, repeat, col_name, row):
        if repeat.get(col_name):
            repeat.get(col_name).extend(row)
        else:
            repeat.update({col_name: row})

    def __format_row(self, row, columns, index, repeat):
        result = []
        for field_code in columns.keys():
            try:
                parsed_value = ""
                if row.get(field_code):
                    parsed_value = '; '.join(row.get(field_code)) if isinstance(row.get(field_code), list) else row.get(
                        field_code)

                if columns[field_code].get("type") == "date" or field_code == "date":
                    date_format = columns[field_code].get("format")
                    date_value_str = row.get(field_code, '')
                    try:
                        if field_code == 'date':
                            date_value = self._convert_to_localized_date_time(date_value_str)
                        else:
                            date_value = datetime.strptime(date_value_str, DateField.DATE_DICTIONARY.get(date_format))

                        col_val = ExcelDate(date_value, date_format or "submission_date")
                    except Exception:
                        col_val = row.get(field_code) or ""
                    result.append(col_val)
                elif columns[field_code].get("type") == GEODCODE_FIELD_CODE:
                    col_val = self._split_gps(parsed_value)
                    result.extend(col_val)
                elif columns[field_code].get("type") == 'integer':
                    col_val_parsed = try_parse(float, parsed_value)
                    result.append(col_val_parsed)
                elif columns[field_code].get("type") == 'field_set':
                    _repeat_row = []
                    repeat_answers = json.loads(row.get(field_code))
                    repeat_fields = columns[field_code].get('fields')
                    for repeat_item in repeat_answers:
                        for question_code, data_value in repeat_item.items():
                            if repeat_fields[question_code].get(
                                    'type') == 'field_set':  # every field_set in a repeat is a list
                                repeat_item[question_code] = json.dumps(data_value)
                        _result = self.__format_row(repeat_item, repeat_fields, index, repeat)
                        _repeat_row.append(_result)
                        _result.append('')
                        _result.append(index + 1)

                    self._add_repeat_data(repeat, self._get_repeat_col_name(columns[field_code]['label']), _repeat_row)
                else:
                    result.append(parsed_value)
            except Exception:
                col_val = row.get(field_code) or ""
                result.extend(col_val)

        return result

    def _split_gps(self, value):
        if not value:
            return ['', '']
        value_stripped = value.replace("  ", " ").strip()
        if ',' in value_stripped:
            coordinates_split = value_stripped.split(',')
            return [try_parse(float, coordinates_split[0]), try_parse(float, coordinates_split[1])]
        else:
            coordinates_split = value.split()
            if len(coordinates_split) == 1:
                return [try_parse(float, value), ""]
            return [try_parse(float, coordinates_split[0]), try_parse(float, coordinates_split[1])]


def try_parse(type, value):
    if value is None:
        return None
    try:
        return type(value)
    except ValueError:
        return value