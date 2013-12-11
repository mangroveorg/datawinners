import logging
from django.utils.translation import ugettext_lazy, gettext
import xlrd
from datawinners.accountmanagement.helper import is_org_user
from datawinners.accountmanagement.models import NGOUserProfile, Organization
from datawinners.project.helper import get_feed_dictionary, get_web_transport_info
from datawinners.project.submission.validator import ImportSubmissionValidator
from mangrove.transport.player.parser import XlsOrderedParser, XlsParser
from mangrove.transport.services.survey_response_service import SurveyResponseService

logger = logging.getLogger("importsubmission")


class SubmissionImporter():
    def __init__(self, dbm, feed_dbm, user, form_model, project):
        self.dbm = dbm
        self.user = user
        self.form_model = form_model
        self.submission_validator = ImportSubmissionValidator(dbm, form_model, project)
        self.submission_persister = SubmissionPersister(user, dbm, feed_dbm, form_model, project)
        self.project = project

    def import_submission(self, file_content):
        saved_entries,invalid_row_details,ignored_entries = [], [], []
        total_submissions = 0
        user_profile = NGOUserProfile.objects.get(user=self.user)

        parser = SubmissionParser(file_content, self.form_model);
        message = parser.validate_template()

        if not message:
            parsed_rows = parser.get_parsed_rows();
            total_submissions = len(parsed_rows)
            is_organization_user = is_org_user(self.user)
            message = self._validate_and_update_reporter(parsed_rows, user_profile, is_organization_user)

            if not message:
                valid_rows, invalid_row_details = self.submission_validator.validate_rows(parsed_rows)
                ignored_entries, saved_entries = self.submission_persister.save_submission(is_organization_user, user_profile, valid_rows)
                if ignored_entries:
                    ignored_row_start = total_submissions - len(ignored_entries)
                    message = gettext("You have exceeded the limit. Starting from row %s is ignored" % str(ignored_row_start))
                else:
                    message = gettext('%s of %s Submissions imported. Please check below for details') % (len(saved_entries), len(parsed_rows))
        return SubmissionImportResponse(saved_entries=saved_entries,
                                        errored_entrie_details=invalid_row_details,
                                        ignored_entries=ignored_entries,
                                        message=message,
                                        total_submissions=total_submissions)

    def _validate_and_update_reporter(self, parsed_rows, user_profile, is_organization_user):
        error = ""
        if self.project.is_summary_project() and not is_organization_user:
            if self._uploaded_submission_has_reporter_id(parsed_rows):
                error = gettext("You are not allowed to do submission on some other DS")

            self._add_logged_in_user_as_reporter(parsed_rows, user_profile)
        return error

    def _add_logged_in_user_as_reporter(self, parsed_rows, user_profile):
        for row in parsed_rows:
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

    def __init__(self, user, dbm, feed_dbm, form_model, project):
        self.user = user
        self.dbm = dbm
        self.feed_dbm = feed_dbm
        self.form_model = form_model
        self.project = project

    def save_submission(self, is_organization_user, user_profile, valid_rows):
        organization = Organization.objects.get(org_id=user_profile.org_id)
        saved_entries, ignored_entries = [], []
        for valid_row in valid_rows:
            if organization.has_exceeded_quota_and_notify_users():
                ignored_entries = valid_rows[len(saved_entries):]
                break
            else:
                self._save_survey(is_organization_user, user_profile, valid_row)
                saved_entries.append(valid_row)
                organization.increment_message_count_for(incoming_web_count=1)
        return ignored_entries, saved_entries

    def _get_reporter_id_for_submission(self, is_organization_user, user_profile, valid_row):
        if self.project.is_summary_project() and is_organization_user:
            reporter_id = valid_row.get('eid')
        else:
            reporter_id = user_profile.reporter_id
        return reporter_id

    def _save_survey(self, is_organization_user, user_profile, valid_row):
        reporter_id = self._get_reporter_id_for_submission(is_organization_user, user_profile, valid_row)
        service = SurveyResponseService(self.dbm, logger, self.feed_dbm, user_profile.reporter_id)
        additional_feed_dictionary = get_feed_dictionary(self.project)
        transport_info = get_web_transport_info(self.user.username)
        return service.save_survey(self.form_model.form_code, valid_row, [],
                                   transport_info, valid_row, reporter_id, additional_feed_dictionary)

class SubmissionParser():

    def __init__(self, file_content, form_model):
        self.file_content = file_content
        self.form_model = form_model
        self.parser = XlsOrderedParser()

    def validate_template(self):

        rows = self._parse()
        try:
            header_row = rows[0]
            col_mapping = {}
            for field in self.form_model.fields:
                header_cell = [i for i, col in enumerate(header_row) if field.label in col]
                index = header_cell[0]
                col_mapping.update({field.code:index})

            if len(col_mapping) == len(self.form_model.fields):
                self.parsed_rows = self._get_rows(rows, col_mapping)
                return ""

        except:
            return gettext("columns not matched. Template invalid")


    def _parse(self):
        p = XlsSubmissionParser()
        return p.parse(self.file_content)

    def _validate_columns(self, rows):

        header_row = rows[0]
        col_mapping = {}

        for field in self.form_model.fields:
            index = [i for i, col in enumerate(header_row) if field.label in col][0]
            col_mapping.update({field.code:index})

        return len(col_mapping) == len(self.form_model.fields), col_mapping

    def _get_rows(self, rows, col_mapping):
        result = []
        for data in rows[1:]:
            row_value = {}
            for field in self.form_model.fields:
                row_value.update({field.code: data[col_mapping[field.code]]})
            result.append(row_value)

        return result

    def get_parsed_rows(self):
        return self.parsed_rows

class XlsSubmissionParser(XlsParser):
    def parse(self, xls_contents):
        assert xls_contents is not None
        workbook = xlrd.open_workbook(file_contents=xls_contents)
        worksheet = workbook.sheets()[0]
        parsedData = []
        for row_num in range(0, worksheet.nrows):
            row = worksheet.row_values(row_num)
            if self._is_empty(row):
                continue
            row = self._clean(row)
            parsedData.append(row)
        return parsedData
