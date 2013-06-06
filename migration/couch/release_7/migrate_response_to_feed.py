from datawinners.accountmanagement.models import OrganizationSetting
from datawinners.project.data_sender_helper import get_data_sender
from datawinners.project.models import Project
from mangrove.datastore.database import DatabaseManager
from mangrove.feeds.enriched_survey_response import EnrichedSurveyResponseBuilder
from mangrove.form_model.form_model import get_form_model_by_code
from mangrove.utils.types import is_string


class ProjectNotFoundException(Exception):
    pass


def project_by_form_model_id(dbm, form_model_id):
    assert isinstance(dbm, DatabaseManager)
    assert is_string(form_model_id)
    rows = dbm.load_all_rows_in_view('project_by_form_model_id', key=form_model_id)
    if not len(rows):
        raise ProjectNotFoundException("project does not exist for form model id %s " % form_model_id)

    return Project._wrap_row(rows[0])


class MigrateToFeed:
    def __init__(self, dbm, feed_dbm, logger=None):
        self.dbm = dbm
        self.feed_dbm = feed_dbm
        self.logger = logger

    def project_info(self, form_code):
        form_model = get_form_model_by_code(self.dbm, form_code)
        project = project_by_form_model_id(self.dbm, form_model.id)

        return {'project': {'id': project.id, 'name': project.name, 'type': project.entity_type,
                            'status': project.state}}

    def enriched_dbm(self, survey_response):
        form_model = get_form_model_by_code(self.dbm, survey_response.form_code)
        org_id = OrganizationSetting.objects.get(document_store=self.dbm.database_name).organization_id
        data_sender = get_data_sender(self.dbm, org_id, survey_response)
        builder = EnrichedSurveyResponseBuilder(self.dbm, survey_response, form_model, data_sender[1],
                                                self.project_info(survey_response.form_code), self.logger)
        return builder.feed_document()

    def _new_feed(self, survey_response):
        document = self.enriched_dbm(survey_response)
        self.feed_dbm._save_document(document)

    def _update_feed(self, survey_response):
        document = self.enriched_dbm(survey_response)
        self.feed_dbm._save_document(document)

    def migrate(self, survey_response):
        raw_doc = self.feed_dbm.database.get(survey_response.id)
        if raw_doc is None:
            self._new_feed(survey_response)
        elif raw_doc['modified'] != survey_response.modified:
            self._update_feed(survey_response)
