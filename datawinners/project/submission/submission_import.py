# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from collections import OrderedDict
import logging
import os
from django.utils.translation import gettext
import xlrd
from datawinners.accountmanagement.helper import is_org_user
from datawinners.accountmanagement.models import NGOUserProfile
from datawinners.entity.entity_exceptions import InvalidFileFormatException
from datawinners.entity.import_data import get_filename_and_contents
from datawinners.project.helper import get_feed_dictionary, get_web_transport_info
from datawinners.project.submission.validator import SubmissionWorkbookRowValidator
from mangrove.transport.player.parser import XlsParser
from mangrove.transport.services.survey_response_service import SurveyResponseService

logger = logging.getLogger("datawinners")


class SubmissionImporter():
    def __init__(self, dbm, feed_dbm, user, form_model, project, submission_quota_service):
        self.dbm = dbm
        self.user = user
        self.form_model = form_model
        self.project = project
        self.submission_validator = SubmissionWorkbookRowValidator(dbm, form_model, project)
        self.submission_persister = SubmissionPersister(user, dbm, feed_dbm, form_model, project,
                                                        submission_quota_service)


    def import_submission(self, request):
        saved_entries, invalid_row_details, ignored_entries = [], [], []
        total_submissions = 0

        try:
            file_content = self._get_uploaded_content(request)
            is_organization_user = is_org_user(self.user)

            tabular_data = XlsSubmissionParser().parse(file_content)
            if len(tabular_data) <= 1:
                raise ImportValidationError(gettext("The imported file is empty."))
            q_answer_dicts = SubmissionWorkbookMapper(tabular_data, self.form_model).process()
            SubmissionWorkbookValidator(self.form_model).validate(
                q_answer_dicts)

            user_profile = NGOUserProfile.objects.filter(user=self.user)[0]
            #todo add this when default reporter question gets added
            #self._add_reporter_id_for_datasender(q_answer_dicts, user_profile, is_organization_user, is_summary_project)

            valid_rows, invalid_row_details = self.submission_validator.validate_rows(q_answer_dicts)
            ignored_entries, saved_entries = self.submission_persister.save_submissions(is_organization_user,
                                                                                        user_profile, valid_rows)
            total_submissions = len(invalid_row_details)+len(valid_rows)
            if ignored_entries:
                ignored_row_start = total_submissions - len(ignored_entries) + 1
                message = gettext("You have crossed the 1000 Submissions limit for your Basic account. Submissions from row %s have been ignored and were not imported.") % str(ignored_row_start)
            else:
                message = gettext('%s of %s Submissions imported. Please check below for details.') % (len(saved_entries), total_submissions)
        except InvalidFileFormatException as e:
            message = gettext(
                u"We could not import your data ! You are using a document format we canʼt import. Please use the excel (.xls) template file!")
        except ImportValidationError as e:
            message = e.message
        except Exception as e:
            message = gettext("Some unexpected error happened. Please check the excel file and import again.")
            logger.exception("Submission import failed")

        return SubmissionImportResponse(saved_entries=saved_entries,
                                        errored_entrie_details=invalid_row_details,
                                        ignored_entries=ignored_entries,
                                        message=message,
                                        total_submissions=total_submissions)

    def _get_uploaded_content(self, request):
        file_name, file_content = get_filename_and_contents(request)
        base_name, extension = os.path.splitext(file_name)
        if extension != '.xls':
            raise InvalidFileFormatException()

        return file_content

    def _add_reporter_id_for_datasender(self, parsed_rows, user_profile, is_organization_user):

        for row in parsed_rows:
            if is_organization_user:
                if row['eid'] == '':
                    row.update({'eid': user_profile.reporter_id})
            else:
                row.update({"eid": user_profile.reporter_id})

    def _uploaded_submission_has_reporter_id(self, parsed_rows):
        for row in parsed_rows:
            if "eid" in row[1].keys():
                return True
        return False


class SubmissionImportResponse():
    def __init__(self, saved_entries, errored_entrie_details, ignored_entries, message, total_submissions):
        self.saved_entries = saved_entries
        self.errored_entrie_details = errored_entrie_details
        self.ignored_entries = ignored_entries
        self.message = message
        self.total_submissions = total_submissions


class SubmissionPersister():
    def __init__(self, user, dbm, feed_dbm, form_model, project, submission_quota_service):
        self.user = user
        self.dbm = dbm
        self.feed_dbm = feed_dbm
        self.form_model = form_model
        self.project = project
        self.submission_quota_service = submission_quota_service

    def save_submissions(self, is_organization_user, user_profile, valid_rows):
        saved_entries, ignored_entries = [], []
        for valid_row in valid_rows:
            if self.submission_quota_service.has_exceeded_quota_and_notify_users():
                ignored_entries = valid_rows[len(saved_entries):]
                break
            else:
                self._save_survey(user_profile, valid_row)
                saved_entries.append(valid_row)
                self.submission_quota_service.increment_web_submission_count()
        return ignored_entries, saved_entries

    def _save_survey(self, user_profile, valid_row):
        reporter_id = user_profile.reporter_id
        service = SurveyResponseService(self.dbm, logger, self.feed_dbm, user_profile.reporter_id)
        additional_feed_dictionary = get_feed_dictionary(self.project)
        transport_info = get_web_transport_info(self.user.username)
        return service.save_survey(self.form_model.form_code, valid_row, [],
                                   transport_info, valid_row, reporter_id, additional_feed_dictionary)


class SubmissionWorkbookValidator():
    def __init__(self, form_model):
        self.form_model = form_model

    def validate(self, q_answer_dicts):
        expected_cols = [f.code for f in self.form_model.fields]
        if set(q_answer_dicts[0].keys()) != set(expected_cols):
            raise ImportValidationError(gettext(
                "The columns you are importing do not match the current Questionnaire. Please download the latest template for importing."))
        return None


class ImportValidationError(Exception):
    def __init__(self, message):
        super(Exception, self).__init__(message)


class SubmissionWorkbookMapper():
    def __init__(self, input_data, form_model):
        self.input_data = input_data
        self.form_model = form_model

    def _col_mapping(self, header_row):
        col_mapping = {}
        for i, col in enumerate(header_row):
            question_label = col.split('\n')[0].strip()
            field = [field for field in self.form_model.fields if question_label == field.label.strip()][0]
            col_mapping.update({field.code: i})
        return col_mapping

    def process(self):
        rows = self.input_data
        try:
            col_mapping = self._col_mapping(header_row=rows[0])
            return self._get_q_code_answer_dict(rows, col_mapping)
        except Exception as e:
            raise ImportValidationError(gettext(
                "The columns you are importing do not match. Please download the latest template for importing."))

    def _get_q_code_answer_dict(self, rows, col_mapping):
        result = []
        for data in rows[1:]:
            row_value = OrderedDict()
            for field in self.form_model.fields:
                if col_mapping.has_key(field.code):
                    row_value.update({field.code: data[col_mapping[field.code]]})
            result.append(row_value)

        return result


class XlsSubmissionParser(XlsParser):
    def parse(self, xls_contents):
        assert xls_contents is not None
        workbook = xlrd.open_workbook(file_contents=xls_contents)
        worksheet = workbook.sheets()[0]
        parsedData = []
        for row_num in range(0, worksheet.nrows):
            row = worksheet.row_values(row_num)
            row = self._clean(row)
            parsedData.append(row)
        return parsedData
