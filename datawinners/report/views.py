from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import RequestContext, Template
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from datawinners.accountmanagement.decorators import session_not_expired, is_not_expired, is_datasender
from datawinners.main.database import get_database_manager
from mangrove.datastore.report_config import get_report_configs, get_report_config


class AllReportsView(TemplateView):
    template_name = 'report/index.html'

    @method_decorator(login_required)
    @method_decorator(session_not_expired)
    @method_decorator(is_datasender)
    @method_decorator(is_not_expired)
    def get(self, request, *args, **kwargs):
        dbm = get_database_manager(request.user)
        configs = get_report_configs(dbm)
        return self.render_to_response(RequestContext(request, {
            "configs": configs
        }))


def report_content(request, report_id):
    dbm = get_database_manager(request.user)
    config = get_report_config(dbm, report_id)
    return HttpResponse(
        '<link rel="stylesheet" href="/reports/' + report_id + '/stylesheet/" />' +
        _get_content(request, dbm, config),
    )


def report_stylesheet(request, report_id):
    dbm = get_database_manager(request.user)
    config = get_report_config(dbm, report_id)
    style = config.stylesheet().replace("{{report_id}}", report_id)
    return HttpResponse(mimetype="text/css", content=style)


def report_font_file(request, report_id, font_file_name):
    dbm = get_database_manager(request.user)
    config = get_report_config(dbm, report_id)
    font_file = config.font_file(font_file_name)
    return HttpResponse(mimetype="font/opentype", content=font_file)


def _get_content(request, dbm, config):
    return Template(config.template()).render(RequestContext(request, {
        "dbm": dbm,
        "config": config,
        "filters": request.GET
    }))
