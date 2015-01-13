from collections import OrderedDict
from datetime import datetime
import json
import os
from tempfile import NamedTemporaryFile, TemporaryFile, mkdtemp
import zipfile

from django.http import HttpResponse
from django.template.defaultfilters import slugify
from xlsxwriter import Workbook
from django.core.servers.basehttp import FileWrapper

from datawinners.project.submission.export import export_filename, add_sheet_with_data, export_media_folder_name, export_to_new_excel
from datawinners.project.submission.exporter import SubmissionExporter
from datawinners.project.submission.formatter import SubmissionFormatter
from datawinners.project.submission.submission_search import get_scrolling_submissions_query
from mangrove.datastore.documents import SurveyResponseDocument
from mangrove.form_model.field import ExcelDate, DateField


class XFormSubmissionExporter(SubmissionExporter):
    # def _create_zipped_response(self, columns, submission_list, submission_type):
    #     #headers, data_rows_dict = AdvanceSubmissionFormatter(columns, self.form_model,
    #     #                                                     self.local_time_delta).format_tabular_data(submission_list)
    #     return self._create_excel_response(columns, submission_list,
    #                                        export_filename(submission_type, self.project_name))

    # def _create_excel_response(self, columns, submission_list, submission_type):
    #     file_name, wb = self._create_excel_workbook(columns, submission_list, submission_type)
    #     response = HttpResponse(mimetype="application/vnd.ms-excel")
    #     response['Content-Disposition'] = 'attachment; filename="%s.xls"' % (slugify(file_name),)
    #     wb.save(response)
    #     return response

    def _create_excel_workbook(self, columns, submission_list, submission_type):
        file_name = export_filename(submission_type, self.project_name)
        headers, data_rows_dict = AdvanceSubmissionFormatter(columns, self.form_model,
                                                             self.local_time_delta).format_tabular_data(submission_list)
        wb = Workbook(options={'constant_memory': True})
        for sheet_name, header_row in headers.items():
            add_sheet_with_data(data_rows_dict.get(sheet_name, []), header_row, wb, sheet_name_prefix=sheet_name)
        return file_name, wb

    def add_files_to_temp_directory_if_present(self, submission_id, folder_name):
        submission = self.dbm._load_document(submission_id, SurveyResponseDocument)
        files = submission._data.get('_attachments', {})
        for name in files.keys():
            complete_name = os.path.join(folder_name, name)
            temp_file = open(complete_name, "w")
            file = self.dbm.get_attachments(submission_id, name)
            temp_file.write(file)
            temp_file.close()

    @staticmethod
    def add_directory_to_archive(archive, folder_name, media_folder):
        for dir_path, dir_name, file_names in os.walk(media_folder):
            for file_name in file_names:
                complete_name = os.path.join(media_folder, file_name)
                archive.write(complete_name, arcname=folder_name + "/" + file_name, compress_type=zipfile.ZIP_DEFLATED)

    def create_excel_response_with_media(self, submission_type, query_params):
        columns, search_results = self.get_columns_and_search_results(query_params, submission_type)
        submission_ids = self.get_submission_ids(query_params)
        file_name, workbook = self._create_excel_workbook(columns, search_results, submission_type)
        media_folder = self._create_images_folder(submission_ids)
        folder_name = export_media_folder_name(submission_type, self.project_name)
        file_name_normalized, zip_file = self._archive_images_and_workbook(workbook, file_name, folder_name, media_folder)
        response = HttpResponse(FileWrapper(zip_file, blksize=8192000), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="%s.zip"' % file_name_normalized
        zip_file.seek(0)
        return response

    def get_submission_ids(self, query_params):
        query_params['response_fields'] = []
        search_results, query_fields = get_scrolling_submissions_query(self.dbm, self.form_model, query_params,
                                                                       self.local_time_delta)
        return search_results

    def _create_images_folder(self, submission_ids):
        temp_dir = mkdtemp()
        for row_number, row_dict in enumerate(submission_ids):
            self.add_files_to_temp_directory_if_present(row_dict["_id"], temp_dir)

        return temp_dir

    def _archive_images_and_workbook(self, workbook, file_name, folder_name=None, media_folder=None):
        file_name_normalized = slugify(file_name)
        # temporary_excel_file = NamedTemporaryFile(suffix=".xls", delete=False)
        # workbook.save(temporary_excel_file)
        # temporary_excel_file.close()
        zip_file = TemporaryFile()
        archive = zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED)
        self.add_directory_to_archive(archive, folder_name, media_folder)
        archive.write(workbook.filename, compress_type=zipfile.ZIP_DEFLATED,
                      arcname="%s.xls" % file_name_normalized)
        archive.close()
        return file_name_normalized, zip_file

    def _create_response(self, columns, submission_list, submission_type):
        headers, data_rows_dict = AdvanceSubmissionFormatter(columns, self.form_model,
                                                             self.local_time_delta).format_tabular_data(submission_list)
    def _create_response(self, columns, submission_list, submission_type):
        headers, data_rows_dict = AdvanceSubmissionFormatter(columns, self.form_model,
                                                             self.local_time_delta).format_tabular_data(submission_list)
        return export_to_new_excel(headers, data_rows_dict, export_filename(submission_type, self.project_name))

    # def _create_excel_response(self, columns, submission_list, submission_type):
    #     response = HttpResponse(mimetype="application/vnd.ms-excel")
    #     file_name = export_filename(submission_type, self.project_name)
    #     response['Content-Disposition'] = 'attachment; filename="%s.xls"' % (slugify(file_name),)
    #     headers, data_rows_dict = AdvanceSubmissionFormatter(columns, self.form_model,
    #                                                          self.local_time_delta).format_tabular_data(submission_list)
    #     wb = Workbook()
    #     for sheet_name, header_row in headers.items():
    #         add_sheet_with_data(data_rows_dict.get(sheet_name, []), header_row, wb, sheet_name)
    #     wb.save(response)
    #     return response
    #
    # def _create_response(self, columns, submission_list, submission_type):
    #     headers, data_rows_dict = AdvanceSubmissionFormatter(columns, self.form_model, self.local_time_delta).format_tabular_data(submission_list)
    #     return export_to_new_excel(headers, data_rows_dict, export_filename(submission_type, self.project_name))
        

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