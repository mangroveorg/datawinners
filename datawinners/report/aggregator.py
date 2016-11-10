from datawinners.report.all_reports import AllReportsView
from mangrove.transport.contract.survey_response import get_survey_responses_by_form_model_id


def get_report_data(dbm, config):
    rows = get_survey_responses_by_form_model_id(dbm, config.questionnaires[0]["id"], AllReportsView.BATCH_SIZE)
    return [{config.questionnaires[0]["alias"]: row} for index, row in enumerate(rows) if index < AllReportsView.BATCH_SIZE]
