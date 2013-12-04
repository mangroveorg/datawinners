import logging
from datawinners.accountmanagement.helper import is_org_user
from datawinners.accountmanagement.models import NGOUserProfile, Organization
from datawinners.project.submission.validator import ImportSubmissionValidator
from datawinners.submission.views import check_quotas_and_update_users
from mangrove.transport import TransportInfo
from mangrove.transport.player.parser import XlsOrderedParser
from mangrove.transport.services.survey_response_service import SurveyResponseService

importsubmission_logger = logging.getLogger("importsubmission")


class SubmissionImporter():
    def __init__(self, dbm, feed_dbm, user, form_model, project):
        self.dbm = dbm
        self.user = user
        self.form_model = form_model
        self.submission_validator = ImportSubmissionValidator(dbm, form_model)
        self.parser = XlsOrderedParser()
        self.project = project

    def import_submission(self, file_content):
        user_profile = NGOUserProfile.objects.get(user=self.user)
        parsed_rows = self.parser.parse(file_content)

        if self.project.is_summary_project() and not is_org_user(self.user):
            for row in parsed_rows:
                row[1].update({"eid": user_profile.reporter_id})

        valid_rows, invalid_rows = self.submission_validator.validate_rows(parsed_rows)

        ignored_entries, saved_entries = SubmissionPersister().save_submission(user_profile, valid_rows)

        return SubmissionImportResponse(saved_entries=saved_entries,
                                        errored_entries=invalid_rows,
                                        ignored_entries=ignored_entries)

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

    def save_submission(self, user_profile, valid_rows):
        organization = Organization.objects.get(org_id=user_profile.org_id)
        saved_entries, ignored_entries = [], []
        for valid_row in valid_rows:
            if organization.has_exceeded_submission_limit():
                ignored_entries = valid_rows[len(saved_entries):]
                break
            else:
                self._save_submission(user_profile, valid_row)
                saved_entries.append(valid_row)
                organization.increment_message_count_for(incoming_web_count=1)
        check_quotas_and_update_users(organization)
        return ignored_entries, saved_entries

    def _get_reporter_id_for_submission(self, user_profile, valid_row):
        if self.project.is_summary_project() and is_org_user(self.user):
            reporter_id = valid_row.get('eid')
        else:
            reporter_id = user_profile.reporter_id
        return reporter_id

    def _save_submission(self, user_profile, valid_row):
        reporter_id = self._get_reporter_id_for_submission(user_profile, valid_row)
        service = SurveyResponseService(self.dbm, importsubmission_logger, self.feed_dbm, user_profile.reporter_id)
        additional_feed_dictionary = get_feed_dictionary(self.project)
        transport_info = get_transport_info(self.user)
        return service.save_survey(self.form_model.form_code, valid_row, [],
                                   transport_info, valid_row, reporter_id,
                                   additional_feed_dictionary)

def get_feed_dictionary(project):
        additional_feed_dictionary = {}
        project_dict = {
            'id': project.id,
            'name': project.name,
            'type': project.entity_type,
            'status': project.state
        }
        additional_feed_dictionary.update({'project': project_dict})
        return additional_feed_dictionary

def get_transport_info(user):
        return TransportInfo(transport="web", source=user.username, destination="")
