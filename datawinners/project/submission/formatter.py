from datetime import datetime
import re
from datawinners.accountmanagement.localized_time import convert_utc_to_localized
from datawinners.project.helper import SUBMISSION_DATE_FORMAT_FOR_SUBMISSION
from mangrove.form_model.field import ExcelDate, DateField
from datawinners.search.submission_index_constants import SubmissionIndexConstants

GEODCODE_FIELD_CODE = "geocode"


class SubmissionFormatter(object):
    def __init__(self, columns, local_time_delta):
        """
        :param header_keys: specifies column order of formated output.
        """
        self.columns = columns
        self.local_time_delta = local_time_delta

    def format_tabular_data(self, values):
        formatted_values = []
        headers = self.format_header_data()
        for row_dict in values:
            formatted_values.append(self.format_row(row_dict['_source']))
        return headers, formatted_values

    def format_header_data(self):
        headers = []
        for col_def in self.columns.values():
            if col_def.get('type', '') == GEODCODE_FIELD_CODE:
                headers.append(col_def['label'] + " Latitude")
                headers.append(col_def['label'] + " Longitude")
            else:
                if col_def['label'] != "Phone number":
                    headers.append(col_def['label'])
        return headers

    def _convert_to_localized_date_time(self, submission_date):
        submission_date_time = datetime.strptime(submission_date, SUBMISSION_DATE_FORMAT_FOR_SUBMISSION)
        return convert_utc_to_localized(self.local_time_delta, submission_date_time)

    def _format_date_field(self, field, field_code, result, row, columns):
        date_format = columns[field_code].get("format")
        date_value_str = row[field_code]
        try:
            if field_code == 'date':
                date_value = self._convert_to_localized_date_time(date_value_str)
            else:
                date_value = datetime.strptime(date_value_str, DateField.DATE_DICTIONARY.get(date_format))
            col_val = ExcelDate(date_value, date_format or "submission_date")
        except ValueError:
            col_val = field or ""
        result.append(col_val)

    def _format_data_sender_id_field(self, result):
        col_val = ""
        result.append(col_val)

    def _default_format(self, parsed_value, result):
        result.append(parsed_value)

    def _parsed_field_value(self, field_value):
        parsed_value = ""
        if field_value:
            parsed_value = '; '.join(field_value) if isinstance(field_value, list) else field_value
        return parsed_value

    def format_row(self, row):
        result = []
        for field_code in self.columns.keys():
            field_value = row.get(field_code)
            try:

                parsed_value = self._parsed_field_value(field_value)
                field_type = self.columns[field_code].get("type")
                if field_type == "date" or field_code == "date":
                    self._format_date_field(field_value, field_code, result, row, self.columns)
                elif field_type == GEODCODE_FIELD_CODE:
                    self._format_gps_field(parsed_value, result)
                elif field_type == 'select':
                    self._format_select_field(parsed_value, result)
                elif field_type == 'integer':
                    self._format_integer_field(parsed_value, result)
                elif field_code == SubmissionIndexConstants.DATASENDER_ID_KEY and field_value == 'N/A':
                    self._format_data_sender_id_field(result)
                else:
                    self._default_format(parsed_value, result)

            except Exception:
                col_val = field_value or ""
                result.extend(col_val)

        return result

    def _format_gps_field(self, value, result):
        if not value:
            result.extend(['', ''])
            return

        value_stripped = value.replace("  ", " ").strip()
        if ',' in value_stripped:
            coordinates_split = value_stripped.split(',')
            col_val = [self._try_parse(float, coordinates_split[0]), self._try_parse(float, coordinates_split[1])]
        else:
            coordinates_split = value.split()
            if len(coordinates_split) == 1:
                result.extend([self._try_parse(float, value), ""])
                return

            col_val = [self._try_parse(float, coordinates_split[0]), self._try_parse(float, coordinates_split[1])]

        result.extend(col_val)

    def _try_parse(self, type, value):
        if value is None:
            return None
        try:
            return type(value)
        except ValueError:
            return value

    def _format_integer_field(self, parsed_value, result):
        col_val_parsed = self._try_parse(float, parsed_value)
        result.append(col_val_parsed)

    def _format_select_field(self, parsed_value, result):
        result.append(parsed_value)








