from datawinners.accountmanagement.models import OrganizationSetting
from datawinners.accountmanagement.post_activation_events import create_feed_database
from datawinners.project.data_sender_helper import get_data_sender
from datawinners.project.models import Project
from datawinners.main.database import get_db_manager
from mangrove.datastore.database import DatabaseManager
from mangrove.datastore.documents import EnrichedSurveyResponseDocument
from mangrove.errors.MangroveException import FormModelDoesNotExistsException
from mangrove.feeds.enriched_survey_response import EnrichedSurveyResponseBuilder
from mangrove.form_model.form_model import get_form_model_by_code
from mangrove.transport.contract.survey_response import SurveyResponse
from mangrove.utils.types import is_string

BATCH_SIZE = 100
UNDELETED_SURVEY_RESPONSE = "undeleted_survey_response/undeleted_survey_response"


class ProjectNotFoundException(Exception):
    pass


def project_by_form_model_id(dbm, form_model_id):
    assert isinstance(dbm, DatabaseManager)
    assert is_string(form_model_id)
    rows = dbm.load_all_rows_in_view('project_by_form_model_id', key=form_model_id)
    if not len(rows):
        raise ProjectNotFoundException("project does not exist for form model id %s " % form_model_id)

    return Project._wrap_row(rows[0])


class FeedBuilder:
    def __init__(self, db_name, logger):
        self.dbm = get_db_manager(db_name)
        self.feed_dbm = create_feed_database(db_name)
        self.logger = logger

    def project_info(self, form_code):
        form_model = get_form_model_by_code(self.dbm, form_code)
        project = project_by_form_model_id(self.dbm, form_model.id)

        return {'project': {'id': project.id, 'name': project.name, 'type': project.entity_type,
                            'status': project.state}}

    def enriched_dbm(self, survey_response):
        form_model = get_form_model_by_code(self.dbm, survey_response.form_code)
        org_id = OrganizationSetting.objects.get(document_store=self.dbm.database_name).organization_id
        data_sender = get_data_sender(self.dbm, survey_response)
        builder = EnrichedSurveyResponseBuilder(self.dbm, survey_response, form_model, data_sender[1],
                                                self.project_info(survey_response.form_code), self.logger)
        return builder.feed_document()

    def _new_feed(self, survey_response):
        document = self.enriched_dbm(survey_response)
        self.feed_dbm._save_document(document)

    def _update_feed(self, raw_doc, survey_response):
        existing_enriched_response = EnrichedSurveyResponseDocument.wrap(raw_doc)
        document = self.enriched_dbm(survey_response)
        existing_enriched_response.update(document)
        self.feed_dbm._save_document(existing_enriched_response)

    def _migrate(self, survey_response):
        raw_doc = self.feed_dbm.database.get(survey_response.id)
        if raw_doc is None:
            self._new_feed(survey_response)
        elif raw_doc['survey_response_modified_time'] != survey_response.modified:
            self._update_feed(raw_doc, survey_response)

    def _log_success_message(self, survey_response):
        self.logger.info('Successfully migrated survey_reponse_id : %s' % survey_response.id)

    def _create_feed_doc(self, survey_response):
        try:
            self._migrate(survey_response)
            self._log_success_message(survey_response)
        except (ProjectNotFoundException, FormModelDoesNotExistsException) as exception:
            self.logger.error('db_name: %s , exception: %s, failed survey_response_id : %s, error : %s' % (
                self.dbm.database_name, exception.__class__.__name__, survey_response.id, exception.message))
        except Exception as exception:
            self.logger.exception('db_name: %s , exception: Other, failed survey_response_id : %s, error : %s' % (
                self.dbm.database_name, survey_response.id, exception.message))

    def migrate_db(self):
        self.logger.info(
            '\n ============================================= Start =============================================\n')
        self.logger.info('Start  db  : %s' % self.dbm.database_name)
        rows = self.dbm.database.iterview(UNDELETED_SURVEY_RESPONSE, BATCH_SIZE, reduce=False)
        for row in rows:
            survey_response_doc = SurveyResponse.__document_class__.wrap(row['value'])
            survey_response = SurveyResponse.new_from_doc(dbm=self.dbm, doc=survey_response_doc)
            self._create_feed_doc(survey_response)
        self.logger.info(
            '\n ========================================= End ==================================================\n')


    def migrate_document(self, survey_response_id):
        survey_response = SurveyResponse.get(self.dbm, survey_response_id)
        self._migrate(survey_response)
        self._log_success_message(survey_response)
