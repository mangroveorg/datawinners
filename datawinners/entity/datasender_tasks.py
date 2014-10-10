import logging
from datawinners.main.database import get_db_manager
from datawinners.project.view_models import ReporterEntity
from datawinners.tasks import app
from mangrove.datastore.entity import get_by_short_code
from mangrove.form_model.form_model import REPORTER
from mangrove.transport.contract.survey_response import SurveyResponse


@app.task(max_retries=3, throw=False)
def update_datasender_on_open_submissions(database_name, reporter_id):
    logger = logging.getLogger('datawinners.tasks')
    try:
        dbm = get_db_manager(database_name)
        reporter_entity = ReporterEntity(get_by_short_code(dbm, reporter_id, [REPORTER]))
        rows = dbm.load_all_rows_in_view("anonymous_submissions", key=reporter_entity.mobile_number)

        for row in rows:
            update_survey_response(dbm, row, reporter_entity.entity.id)

    except Exception as e:
        logger.exception('Failed for db: %s ,reporter_id: %s' % (database_name, reporter_id))
        logger.exception(e)


def update_survey_response(dbm, row, reporter_id):
    survey_response_doc = SurveyResponse.__document_class__.wrap(row['value'])
    survey_response = SurveyResponse.new_from_doc(dbm=dbm, doc=survey_response_doc)
    survey_response.is_anonymous_submission = None
    survey_response.owner_uid = reporter_id
    survey_response.save()