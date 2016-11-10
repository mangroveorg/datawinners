from django.http import HttpResponse
from django.template import RequestContext, Template
from django.views.generic import TemplateView

from datawinners.main.database import get_database_manager
from mangrove.datastore.report_config import get_report_configs, get_report_config
from mangrove.transport.contract.survey_response import get_survey_responses_by_form_model_id


class AllReportsView(TemplateView):
    BATCH_SIZE = 25
    template_name = 'report/index.html'

    def get(self, request, *args, **kwargs):
        dbm = get_database_manager(request.user)
        configs = get_report_configs(dbm)
        report_data = _get_report_data(dbm, configs[0])
        return self.render_to_response(RequestContext(request, {
            "configs": configs,
            "content": Template(configs[0].template()).render(RequestContext(request, {"report_data": report_data}))
        }))


def report_content(request, report_id):
    dbm = get_database_manager(request.user)
    config = get_report_config(dbm, report_id)
    report_data = _get_report_data(dbm, config)
    return HttpResponse(Template(config.template()).render(RequestContext(request, {"report_data": report_data})))


def _get_report_data(dbm, config):
    rows = get_survey_responses_by_form_model_id(dbm, config.questionnaires[0]["id"], AllReportsView.BATCH_SIZE)
    return _fetch_report_data(config.questionnaires[0]["alias"], rows)


def _fetch_report_data(questionnaire_alias, rows):
    return [{questionnaire_alias: row} for index, row in enumerate(rows) if index < AllReportsView.BATCH_SIZE]
