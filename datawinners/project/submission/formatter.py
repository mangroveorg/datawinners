from datetime import datetime
import re
from datawinners.project.helper import SUBMISSION_DATE_FORMAT_FOR_SUBMISSION
from mangrove.form_model.field import ExcelDate, DateField
from datawinners.search.submission_index_constants import SubmissionIndexConstants

GEODCODE_FIELD_CODE = "geocode"


class SubmissionFormatter(object):
    def __init__(self, columns):
        """
        :param header_keys: specifies column order of formated output.
        """
        self.columns = columns

    def format_tabular_data(self, values):
        formatted_values = []
        headers = []
        for col_def in self.columns.values():
            if col_def.get('type', '') == GEODCODE_FIELD_CODE:
                headers.append(col_def['label'] + " Latitude")
                headers.append(col_def['label'] + " Longitude")
            else:
                if col_def['label'] != "Phone number":
                    headers.append(col_def['label'])
        for row in values:
            formatted_values.append(self._format_row(row))

        return headers, formatted_values

    def _format_row(self, row):
        result = []
        for field_code in self.columns.keys():
            try:
                
                parsed_value= ""
                if row.get(field_code):
                    parsed_value = ', '.join(row.get(field_code)) if isinstance(row.get(field_code),list) else row.get(field_code)

                if self.columns[field_code].get("type") == "date" or field_code == "date":
                    date_format = self.columns[field_code].get("format")
                    py_date_format = DateField.DATE_DICTIONARY.get(date_format) or SUBMISSION_DATE_FORMAT_FOR_SUBMISSION
                    try:
                        col_val = ExcelDate(datetime.strptime(row[field_code], py_date_format),
                                            date_format or "submission_date")
                    except Exception:
                        col_val = row.get(field_code) or ""
                    result.append(col_val)
                elif self.columns[field_code].get("type") == GEODCODE_FIELD_CODE:
                        col_val = self._split_gps(parsed_value)
                        result.extend(col_val)
                elif self.columns[field_code].get("type") == 'select':
                    result.append(parsed_value)
                elif self.columns[field_code].get("type") == 'integer':
                    col_val_parsed = try_parse(float, parsed_value)
                    result.append(col_val_parsed)
                elif field_code == SubmissionIndexConstants.DATASENDER_ID_KEY and row.get(field_code) == 'N/A':
                    col_val = ""
                    result.append(col_val)
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
                return [try_parse(float, value),""]
            return [try_parse(float, coordinates_split[0]), try_parse(float, coordinates_split[1])]


def try_parse(type, value):
    if value is None:
        return None
    try:
        return type(value)
    except ValueError:
        return value
