from collections import OrderedDict
import json
import os
from tempfile import TemporaryFile, mkdtemp
import tempfile
from types import NoneType
import zipfile

from django.http import HttpResponse
from django.template.defaultfilters import slugify
from xlsxwriter import Workbook
from django.core.servers.basehttp import FileWrapper

from datawinners.project.submission.export import export_filename, export_media_folder_name, \
    create_multi_sheet_excel_headers, create_multi_sheet_entries, create_single_sheet_excel_headers, \
    create_single_sheet_entries
from datawinners.project.submission.exporter import SubmissionExporter
from datawinners.project.submission.formatter import SubmissionFormatter, GEOCODE_FIELD_CODE
from datawinners.project.submission.submission_search import get_scrolling_submissions_query
from datawinners.search.submission_index_constants import SubmissionIndexConstants
from mangrove.datastore.documents import SurveyResponseDocument
from datawinners.project.submission.analysis_helper import enrich_analysis_data
from datawinners.project.submission.util import AccessFriendlyDict
import logging

logger = logging.getLogger("datawinners")

'''
TODO: Whole Advanced questionnaire export needs code refactoring and cleanup. 
Current approach is complex and maintenance will be difficult. This can be simplified.
'''
class XFormSubmissionExporter(SubmissionExporter):

    def __init__(self, form_model, project_name, dbm, local_time_delta, current_language='en', preferences=None, is_single_sheet=False):
        SubmissionExporter.__init__(self, form_model, project_name, dbm, local_time_delta, current_language, preferences)
        self.is_single_sheet = is_single_sheet

    def _create_excel_workbook(self, columns, submission_list, submission_type):
        file_name = export_filename(submission_type, self.project_name)
        workbook_file = AdvancedQuestionnaireSubmissionExporter(self.form_model, columns, self.local_time_delta,
                                                                self.preferences).create_excel(submission_list, self.is_single_sheet)
        workbook_file.close()

        return file_name, workbook_file

    def add_files_to_temp_directory_if_present(self, submission_id, folder_name):
        submission = self.dbm._load_document(
            submission_id, SurveyResponseDocument)
        files = submission._data.get('_attachments', {})
        if not self.preferences:
            self._add_files_to_temp(files, folder_name, submission_id)
            return

        for preference in self.preferences:
            if preference.get('visibility'):
                field = preference.get('data').replace('%s_' % submission.form_model_id,'')
                name = submission.values.get(field)
                self._check_nested_questions(name, files, folder_name, submission_id)
                
    def _check_nested_questions(self, name, files, folder_name, submission_id):
        if isinstance(name, list): #process for repeats or groups
            for group_item in name:
                for key, val in group_item.items():
                    self._check_nested_questions(val, files, folder_name, submission_id)
                    #self._check_and_add_file_to_temp(val, files,folder_name, submission_id)
        else:
            self._check_and_add_file_to_temp(name, files, folder_name, submission_id)

    def _check_and_add_file_to_temp(self, name, files, folder_name, submission_id):
        if name and name in files.keys():
            temp_file = open(os.path.join(folder_name, name), "w")
            temp_file.write(self.dbm.get_attachments(submission_id, name))
            temp_file.close()


    def _add_files_to_temp(self, files, folder_name, submission_id):
        for name in files.keys():
            if not name.startswith('preview_'): #Ignoring image preview files in export
                temp_file = open(os.path.join(folder_name, name), "w")
                temp_file.write(self.dbm.get_attachments(submission_id, name))
                temp_file.close()

    @staticmethod
    def add_directory_to_archive(archive, folder_name, media_folder):
        for dir_path, dir_name, file_names in os.walk(media_folder):
            for file_name in file_names:
                file_extension = file_name.split('.')[-1]
                file_name_slugifed = "%s.%s" % (slugify(".".join(file_name.split('.')[:-1])), file_extension)
                complete_name = os.path.join(media_folder, file_name)
                archive.write(complete_name, arcname=folder_name + "/" + file_name_slugifed, compress_type=zipfile.ZIP_DEFLATED)

    def create_excel_response_with_media(self, submission_type, query_params):
        columns, search_results = self.get_columns_and_search_results(query_params, submission_type)
        submission_ids = self.get_submission_ids(query_params)
        file_name, workbook_file = self._create_excel_workbook(columns, search_results, submission_type)
        media_folder = self._create_images_folder(submission_ids)
        folder_name = export_media_folder_name(submission_type, self.project_name)
        file_name_normalized, zip_file = self._archive_images_and_workbook(workbook_file, file_name, folder_name,
                                                                           media_folder)
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
        archive = zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED, allowZip64=True)
        self.add_directory_to_archive(archive, folder_name, media_folder)
        archive.write(workbook_file.name, compress_type=zipfile.ZIP_DEFLATED,
                      arcname="%s.xlsx" % file_name_normalized)
        archive.close()
        return file_name_normalized, zip_file

    def _create_response(self, columns, submission_list, submission_type, hide_codes_sheet=False):
        file_name = slugify(export_filename(submission_type, self.project_name))
        workbook_file = AdvancedQuestionnaireSubmissionExporter(self.form_model, columns,
                                                                self.local_time_delta, self.preferences).create_excel(submission_list, self.is_single_sheet)

        workbook_file.seek(0)
        response = HttpResponse(FileWrapper(workbook_file),
                                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        response['Content-Disposition'] = "attachment; filename=%s.xlsx" % file_name
        return response


GEODCODE_FIELD_CODE = "geocode"
FIELD_SET = "field_set"


class AdvancedQuestionnaireSubmissionExportHeaderCreator():
    def __init__(self, columns, form_model, preferences):
        self.columns = columns
        self.form_model = form_model
        self.preferences = preferences

    def create_headers(self):
        repeat_headers = OrderedDict()
        repeat_headers.update({'main': ''})
        headers = self._format_tabular_data({"fields":self.columns}, repeat_headers)
        if self.form_model.has_nested_fields:
            self._append_relating_columns(headers)
        repeat_headers.update({'main': headers})

        return repeat_headers

    def _append_relating_columns(self, cols):
        cols.append('_index')
        cols.append('_parent_index')

    def _format_tabular_data(self, fields_dict, repeat):
        headers = []
        for col_def in fields_dict["fields"].values():
            if col_def.get('type', '') == GEODCODE_FIELD_CODE:
                headers.append(col_def['label'] + " Latitude")
                headers.append(col_def['label'] + " Longitude")
            elif col_def.get('type', '') == FIELD_SET:
                _repeat = self._format_tabular_data(col_def, repeat)
                self._append_relating_columns(_repeat)
                repeat.update({self._get_repeat_column_name(col_def['code']): _repeat})
            else:
                headers.append(col_def['label'])
        return headers

    def _get_repeat_column_name(self, code):
        return slugify(code)[:30]


class AdvancedQuestionnaireSubmissionExporter():
    def __init__(self, form_model, columns, local_time_delta, preferences):
        self.form_model = form_model
        self.columns = columns
        self.local_time_delta = local_time_delta
        self.preferences = preferences

    def create_excel(self, submission_list, is_single_sheet):
        workbook_file = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
        workbook = Workbook(workbook_file, options={'constant_memory': True})

        headers = self.get_visible_headers()
        if isinstance(headers, NoneType):
            headers = {}
        visible_headers = headers

        if is_single_sheet:
            create_single_sheet_excel_headers(visible_headers, workbook)
            row_count_dict = {'main': 0}
            sheet_names_index_map = {}
            previous_headers_count = 0
            for index, sheet_name in enumerate(visible_headers.iterkeys()):
                if sheet_names_index_map:
                    sheet_names_index_map[sheet_name] = previous_headers_count
                else:
                    sheet_names_index_map[sheet_name] = 0

                previous_headers_count += len(visible_headers[sheet_name])

            formatter = AdvanceSubmissionFormatter(self.columns, self.form_model, self.local_time_delta, self.preferences, is_single_sheet)

            for row_number, row_dict in enumerate(submission_list):
                formatted_values, formatted_repeats = [], {}

                if row_number == 20000:
                    # export limit set to 20K after performance exercise
                    #since scan & scroll API does not support result set size the workaround is to handle it this way
                    break

                row = enrich_analysis_data(
                    row_dict['_source'], self.form_model, submission_id=row_dict['_id'], is_export=True)
                result = formatter.format_row(row, row_number, formatted_repeats)

                if self.form_model.has_nested_fields and not is_single_sheet:
                    result.append(row_number + 1)

                formatted_values.append(result)
                formatted_repeats.update({'main': formatted_values})

                create_single_sheet_entries(formatted_repeats, workbook, sheet_names_index_map, row_count_dict)
        else:
            create_multi_sheet_excel_headers(visible_headers, workbook)

            sheet_names_index_map = dict([(sheet_name, index) for index, sheet_name in enumerate(visible_headers.iterkeys())])
            sheet_name_row_count_map = dict([(sheet_name, 0) for sheet_name in sheet_names_index_map.iterkeys()])

            formatter = AdvanceSubmissionFormatter(self.columns, self.form_model, self.local_time_delta, self.preferences)

            for row_number, row_dict in enumerate(submission_list):
                formatted_values, formatted_repeats = [], {}

                if row_number == 20000:
                    # export limit set to 20K after performance exercise
                    #since scan & scroll API does not support result set size the workaround is to handle it this way
                    break

                row = enrich_analysis_data(
                    row_dict['_source'], self.form_model, submission_id=row_dict['_id'], is_export=True)
                result = formatter.format_row(row, row_number, formatted_repeats)

                if self.form_model.has_nested_fields:
                    result.append(row_number + 1)

                formatted_values.append(result)
                formatted_repeats.update({'main': formatted_values})

                create_multi_sheet_entries(formatted_repeats, workbook, sheet_names_index_map, sheet_name_row_count_map)

        workbook.close()
        return workbook_file

    def get_visible_headers(self):
        excel_headers = AdvancedQuestionnaireSubmissionExportHeaderCreator(self.columns, self.form_model,
                                                                           self.preferences).create_headers()
        if not self.preferences:
            return excel_headers

        try:
            header_columns = self._get_visible_headers(excel_headers,
                process_preferences=self.preferences)
            if self.form_model.has_nested_fields:
                header_columns.get('main').extend(['_index', '_parent_index'])
            return header_columns
        except Exception as e:
            logger.exception('Exception occurred while applying preferences for exports. Safely handled for now, by exporting default columns')
            
        return excel_headers #safe handling

    '''
    This method should return back header columns, with excel sheet names as key and array of column headers as values.
    
    example:
        {
            'main':['Datasender name', 'Age'],
            'repeat':['Repeat column label']
        }
    Order of columns are important.    
    '''
    def _get_visible_headers(self, precomputed_excel_headers, process_preferences=[]):

        excel_headers = OrderedDict()
        for preference in process_preferences:
            if preference.get('visibility') or preference.has_key('children'):
                key = preference.get('data')
                if preference.has_key('children'):
                    child_excel_headers = self._get_visible_headers(precomputed_excel_headers,
                        process_preferences=preference.get('children'))
                    if child_excel_headers:
                        for sheet_name,child_columns in child_excel_headers.iteritems():
                            dict_extend_list_value(excel_headers, sheet_name, child_columns)
                elif self.columns.get(key) and self.columns.get(key).get('type') == 'field_set':
                    field_code = self.columns.get(key).get('code')
                    excel_headers.update({field_code: precomputed_excel_headers.get(field_code)})
                    #Not optimal. Temporary fix for Group within repeat scenarios, which won't have
                    #preferences and which should come in separate sheet.
                    for field in self.form_model.fields:
                        if field.is_field_set and field.code == field_code:
                            for child_field in field.fields: #current support only to first level children of repeat. Not recursive.
                                if precomputed_excel_headers.get(child_field.code):
                                    excel_headers.update({child_field.code: precomputed_excel_headers.get(child_field.code)})
                                    
                            
                else:
                    column_header = self._check_and_return_column_header(key, preference.get("title"))
                    dict_extend_list_value(excel_headers, 'main', column_header)
        return excel_headers

    def _check_and_return_column_header(self, key, label):
        header_columns = []
        if self.columns.get(key) and self.columns.get(key).get('type') == GEOCODE_FIELD_CODE:
            header_columns.append(label + " Latitude")
            header_columns.append(label + " Longitude")
        else:
            header_columns.append(label)
        return header_columns


class AdvanceSubmissionFormatter(SubmissionFormatter):
    def __init__(self, columns, form_model, local_time_delta, preferences, is_single_sheet=False):
        super(AdvanceSubmissionFormatter, self).__init__(columns, local_time_delta, preferences)
        self.form_model = form_model
        self.is_single_sheet = is_single_sheet

    def _get_repeat_col_name(self, label):
        return slugify(label)[:30]

    def format_row(self, row, index, formatted_repeats):
        return self.__format_row(row, self.get_visible_columns(), index, formatted_repeats)

    def _add_repeat_data(self, repeat, col_name, row):
        if repeat.get(col_name):
            repeat.get(col_name).extend(row)
        else:
            repeat.update({col_name: row})

    def _format_field_set(self, columns, field_code, index, repeat, row):
        _repeat_row = []
        repeat_answers = json.loads(row.get(field_code))
        repeat_fields = columns[field_code].get('fields')
        for repeat_item in repeat_answers:
            for question_code, data_value in repeat_item.items():
                if repeat_fields.get(question_code, {}).get(
                        'type', None) == 'field_set':  # every field_set in a repeat is a list
                    repeat_item[question_code] = json.dumps(data_value)
            _result = self.__format_row(repeat_item, repeat_fields, index, repeat)
            _repeat_row.append(_result)
            if not self.is_single_sheet:
                _result.append('')
                _result.append(index + 1)
        return _repeat_row

    def __format_row(self, row, columns, index, repeat):
        result = []
        access_friendly_row = AccessFriendlyDict(row)

        for field_code in columns.keys():
            try:
                field_value = row.get(field_code, None)
                if '.' in field_code:
                    field_value = getattr(access_friendly_row, field_code)
                    field_value = self.post_parse_field(
                        field_code, field_value)
                parsed_value = self._parsed_field_value(field_value)
                field_type = columns[field_code].get("type")

                if field_type == "date" or field_code == "date":
                    self._format_date_field(field_value, field_code, result, row, columns)
                elif field_type == GEODCODE_FIELD_CODE:
                    self._format_gps_field(parsed_value, result)
                elif field_type == 'select':
                    self._format_select_field(parsed_value, result)
                elif field_type == 'integer':
                    self._format_integer_field(parsed_value, result)
                elif field_code == SubmissionIndexConstants.DATASENDER_ID_KEY and field_value == 'N/A':
                    self._format_data_sender_id_field(result)
                elif field_type == 'field_set':
                    _repeat_row = self._format_field_set(columns, field_code, index, repeat, row)
                    self._add_repeat_data(repeat, self._get_repeat_col_name(columns[field_code]['code']), _repeat_row)
                else:
                    self._default_format(parsed_value, result)
            except Exception as e:
                col_val = row.get(field_code) or ""
                result.extend(col_val)

        return result

'''
Utility to extend list value in a Dictionary.
example:
 x = {'roll_no': [1,2,3]}
 dict_extend_list_value(x, 'roll_no',[4,5,6])
 will return 
 x = {'roll_no': [1,2,3,4,5,6]}
'''
def dict_extend_list_value(dict_obj, key, value):
    current_value = dict_obj.get(key,[])
    current_value.extend(value)
    dict_obj.update({key:current_value})
    return dict_obj