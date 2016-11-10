from django.http import HttpResponse
from django.template import RequestContext, Template
from django.views.generic import TemplateView

from datawinners.main.database import get_database_manager
from datawinners.report.aggregator import get_report_data
from mangrove.datastore.report_config import get_report_configs, get_report_config


class AllReportsView(TemplateView):
    BATCH_SIZE = 25
    template_name = 'report/index.html'

    def get(self, request, *args, **kwargs):
        dbm = get_database_manager(request.user)
        configs = get_report_configs(dbm)
        report_data = get_report_data(dbm, configs[0])
        return self.render_to_response(RequestContext(request, {
            "configs": configs,
            "content": Template(configs[0].template()).render(RequestContext(request, {"report_data": report_data}))
        }))


def report_content(request, report_id):
    dbm = get_database_manager(request.user)
    config = get_report_config(dbm, report_id)
    report_data = get_report_data(dbm, config)
    return HttpResponse(Template(config.template()).render(RequestContext(request, {"report_data": report_data})))
