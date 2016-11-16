from django.http import HttpResponse
from django.template import RequestContext, Template
from django.views.generic import TemplateView

from datawinners.main.database import get_database_manager
from datawinners.report.aggregator import get_report_data
from mangrove.datastore.report_config import get_report_configs, get_report_config


class AllReportsView(TemplateView):
    template_name = 'report/index.html'

    def get(self, request, *args, **kwargs):
        dbm = get_database_manager(request.user)
        configs = get_report_configs(dbm)
        return self.render_to_response(RequestContext(request, {
            "configs": configs,
            "content": (configs or '') and _get_content(dbm, configs[0], request)
        }))


def report_content(request, report_id):
    dbm = get_database_manager(request.user)
    config = get_report_config(dbm, report_id)
    return HttpResponse(_get_content(dbm, config, request))


def _get_content(dbm, config, request):
    page_number = request.GET.get("page_number") or "1"
    return Template(config.template()).render(RequestContext(request, {"report_data": get_report_data(dbm, config, int(page_number))}))
