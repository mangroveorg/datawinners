from collections import OrderedDict
from datetime import datetime
import json
import os
from tempfile import NamedTemporaryFile, TemporaryFile, mkdtemp
import tempfile
import zipfile

from django.http import HttpResponse
from django.template.defaultfilters import slugify
from xlsxwriter import Workbook
from django.core.servers.basehttp import FileWrapper

from datawinners.project.submission.export import export_filename, add_sheet_with_data, export_media_folder_name, export_to_new_excel, \
    create_multi_sheet_excel_headers, create_multi_sheet_entries
from datawinners.project.submission.exporter import SubmissionExporter
from datawinners.project.submission.formatter import SubmissionFormatter
from datawinners.project.submission.submission_search import get_scrolling_submissions_query
from mangrove.datastore.documents import SurveyResponseDocument
from mangrove.form_model.field import ExcelDate, DateField


class XFormSubmissionExporter(SubmissionExporter):

    def _create_excel_workbook(self, columns, submission_list, submission_type):
        file_name = export_filename(submission_type, self.project_name)
        workbook_file = AdvancedQuestionnaireSubmissionExporter(self.form_model, columns,
                                                             self.local_time_delta).create_excel(submission_list)
        workbook_file.close()
        # for sheet_name, header_row in headers.items():
        #     add_sheet_with_data(data_rows_dict.get(sheet_name, []), header_row, wb, sheet_name_prefix=sheet_name)

        return file_name, workbook_file

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
        file_name, workbook_file = self._create_excel_workbook(columns, search_results, submission_type)
        media_folder = self._create_images_folder(submission_ids)
        folder_name = export_media_folder_name(submission_type, self.project_name)
        file_name_normalized, zip_file = self._archive_images_and_workbook(workbook_file, file_name, folder_name, media_folder)
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

    def _archive_images_and_workbook(self, workbook_file, file_name, folder_name=None, media_folder=None):
        file_name_normalized = slugify(file_name)
        zip_file = TemporaryFile()
        archive = zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED)
        self.add_directory_to_archive(archive, folder_name, media_folder)
        archive.write(workbook_file.name, compress_type=zipfile.ZIP_DEFLATED,
                      arcname="%s.xlsx" % file_name_normalized)
        archive.close()
        return file_name_normalized, zip_file

    def _create_response(self, columns, submission_list, submission_type):
        file_name = slugify(export_filename(submission_type, self.project_name))
        workbook_file = AdvancedQuestionnaireSubmissionExporter(self.form_model, columns,
                                                             self.local_time_delta).create_excel(submission_list)

        workbook_file.seek(0)
        response = HttpResponse(FileWrapper(workbook_file), mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        response['Content-Disposition'] = "attachment; filename=%s.xlsx" % file_name
        return response
        # return export_to_new_excel(headers, data_rows_dict, export_filename(submission_type, self.project_name))


GEODCODE_FIELD_CODE = "geocode"
FIELD_SET = "field_set"

class AdvancedQuestionnaireSubmissionExportHeaderCreator():

    def __init__(self, columns, form_model):
        self.columns = columns
        self.form_model = form_model

    def create_headers(self):
        repeat_headers = OrderedDict()
        repeat_headers.update({'main': ''})
        headers = self._format_tabular_data(self.columns, repeat_headers)
        if self.form_model.has_nested_fields:
            self._append_relating_columns(headers)
        repeat_headers.update({'main': headers})

        return repeat_headers

    def _append_relating_columns(self, cols):
        cols.append('_index')
        cols.append('_parent_index')

    def _format_tabular_data(self, columns, repeat):
        headers = []
        for col_def in columns.values():
            if col_def.get('type', '') == GEODCODE_FIELD_CODE:
                headers.append(col_def['label'] + " Latitude")
                headers.append(col_def['label'] + " Longitude")
            elif col_def.get('type', '') == FIELD_SET:
                _repeat = self._format_tabular_data(col_def['fields'], repeat)
                self._append_relating_columns(_repeat)
                repeat.update({self._get_repeat_column_name(col_def['label']): _repeat})
            else:
                headers.append(col_def['label'])
        return headers

    def _get_repeat_column_name(self, label):
        return slugify(label)[:20]

class AdvancedQuestionnaireSubmissionExporter():

    def __init__(self, form_model, columns, local_time_delta):
        self.form_model = form_model
        self.columns = columns
        self.local_time_delta = local_time_delta

    def create_excel(self, submission_list):
        workbook_file = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
        workbook = Workbook(workbook_file, options={'constant_memory': True})

        excel_headers = AdvancedQuestionnaireSubmissionExportHeaderCreator(self.columns, self.form_model).create_headers()
        create_multi_sheet_excel_headers(excel_headers, workbook)

        sheet_names_index_map = dict([(sheet_name, index) for index, sheet_name in enumerate(excel_headers.iterkeys())])
        sheet_name_row_count_map = dict([(sheet_name, 0) for sheet_name in sheet_names_index_map.iterkeys()])

        formatter = AdvanceSubmissionFormatter(self.columns, self.form_model, self.local_time_delta)

        for row_number, row_dict in enumerate(submission_list):
            formatted_values, formatted_repeats = [], {}

            if row_number == 20000:
            #export limit set to 20K after performance exercise
            #since scan & scroll API does not support result set size the workaround is to handle it this way
                break

            result = formatter.format_row(row_dict['_source'], row_number, formatted_repeats)

            if self.form_model.has_nested_fields:
                result.append(row_number + 1)

            formatted_values.append(result)
            formatted_repeats.update({'main': formatted_values})

            create_multi_sheet_entries(formatted_repeats, workbook, sheet_names_index_map, sheet_name_row_count_map)

        workbook.close()
        return workbook_file



class AdvanceSubmissionFormatter(SubmissionFormatter):
    def __init__(self, columns, form_model, local_time_delta):
        super(AdvanceSubmissionFormatter, self).__init__(columns, local_time_delta)
        self.form_model = form_model

    def _get_repeat_col_name(self, label):
        return slugify(label)[:20]

    def format_row(self, row, index, formatted_repeats):
        return self.__format_row(row, self.columns, index, formatted_repeats)

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
                    col_val_parsed = self._try_parse(float, parsed_value)
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
