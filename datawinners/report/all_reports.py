from django.http import HttpResponse
from django.template import RequestContext, Template
from django.views.generic import TemplateView

from datawinners.main.database import get_database_manager
from mangrove.datastore.report_config import get_report_configs, get_report_config


class AllReportsView(TemplateView):
    template_name = 'report/index.html'

    def get(self, request, *args, **kwargs):
        configs = get_report_configs(get_database_manager(request.user))
        return self.render_to_response(RequestContext(request, {
            "configs": configs,
            "content": Template(configs[0].template()).render(RequestContext(request))
        }))


def report_content(request, report_id):
    config = get_report_config(get_database_manager(request.user), report_id)
    return HttpResponse(Template(config.template()).render(RequestContext(request)))
