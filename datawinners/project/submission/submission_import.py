import logging
from datawinners.accountmanagement.helper import is_org_user
from datawinners.accountmanagement.models import NGOUserProfile, Organization
from datawinners.project.helper import get_feed_dictionary, get_web_transport_info
from datawinners.project.submission.validator import ImportSubmissionValidator
from datawinners.submission.views import check_quotas_and_update_users
from mangrove.transport.player.parser import XlsOrderedParser
from mangrove.transport.services.survey_response_service import SurveyResponseService

importsubmission_logger = logging.getLogger("importsubmission")


class SubmissionImporter():
    def __init__(self, dbm, feed_dbm, user, form_model, project):
        self.dbm = dbm
        self.user = user
        self.form_model = form_model
        self.submission_validator = ImportSubmissionValidator(dbm, form_model)
        self.submission_persister = SubmissionPersister(user, dbm, feed_dbm, form_model, project)
        self.parser = XlsOrderedParser()
        self.project = project

    def import_submission(self, file_content):
        user_profile = NGOUserProfile.objects.get(user=self.user)
        parsed_rows = self.parser.parse(file_content)
        is_organization_user = is_org_user(self.user)

        if self.project.is_summary_project() and not is_organization_user:
            for row in parsed_rows:
                row[1].update({"eid": user_profile.reporter_id})

        valid_rows, invalid_rows = self.submission_validator.validate_rows(parsed_rows)

        ignored_entries, saved_entries = self.submission_persister.save_submission(is_organization_user, user_profile, valid_rows)

        return SubmissionImportResponse(saved_entries=saved_entries, errored_entries=invalid_rows, ignored_entries=ignored_entries)

class SubmissionImportResponse():
    def __init__(self, saved_entries, errored_entries, ignored_entries):
        self.saved_entries = saved_entries
        self.errored_entries = errored_entries
        self.ignored_entries = ignored_entries

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
            if organization.has_exceeded_submission_limit():
                ignored_entries = valid_rows[len(saved_entries):]
                break
            else:
                self._save_survey(is_organization_user, user_profile, valid_row)
                saved_entries.append(valid_row)
                organization.increment_message_count_for(incoming_web_count=1)
        check_quotas_and_update_users(organization)
        return ignored_entries, saved_entries

    def _get_reporter_id_for_submission(self, is_organization_user, user_profile, valid_row):
        if self.project.is_summary_project() and is_organization_user:
            reporter_id = valid_row.get('eid')
        else:
            reporter_id = user_profile.reporter_id
        return reporter_id

    def _save_survey(self, is_organization_user, user_profile, valid_row):
        reporter_id = self._get_reporter_id_for_submission(is_organization_user, user_profile, valid_row)
        service = SurveyResponseService(self.dbm, importsubmission_logger, self.feed_dbm, user_profile.reporter_id)
        additional_feed_dictionary = get_feed_dictionary(self.project)
        transport_info = get_web_transport_info(self.user.username)
        return service.save_survey(self.form_model.form_code, valid_row, [],
                                   transport_info, valid_row, reporter_id, additional_feed_dictionary)