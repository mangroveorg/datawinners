from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import resolve
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import RequestContext, Template
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, RedirectView
import os
import mimetypes
from datawinners.accountmanagement.decorators import session_not_expired, is_not_expired, is_datasender
from datawinners.main.database import get_database_manager
from mangrove.datastore.report_config import get_report_configs, get_report_config
from datawinners import utils



class AllReportsView(TemplateView):
    template_name = 'report/index.html'

    @method_decorator(login_required)
    @method_decorator(session_not_expired)
    @method_decorator(is_datasender)
    @method_decorator(is_not_expired)
    def get(self, request, *args, **kwargs):
        dbm = get_database_manager(request.user)
        configs = get_report_configs(dbm)
        organization = utils.get_organization(request)
        is_pro_sms = organization.is_pro_sms
        return self.render_to_response(RequestContext(request, {
            "configs": configs,
            "is_pro_sms": is_pro_sms
        }))


def report_content(request, report_id):
    dbm = get_database_manager(request.user)
    config = get_report_config(dbm, report_id)
    return HttpResponse(
        '<link rel="stylesheet" href="/reports/' + report_id + '/stylesheet/" />' +
        _get_content(request, dbm, config),
    )


def report_stylesheet(request, report_id):
    style = _get_file(request, report_id, "styles.css").replace("{{report_id}}", report_id)
    return HttpResponse(mimetype="text/css", content=style)


def report_file(request, report_id, file_name):
    _file = _get_file(request, report_id, file_name)
    file_extn = os.path.splitext(file_name)[-1]
    mime_type = mimetypes.types_map.get(file_extn, 'application/octet-stream')
    return HttpResponse(mimetype=mime_type, content=_file)


def _get_file(request, report_id, file_name):
    dbm = get_database_manager(request.user)
    return get_report_config(dbm, report_id).file(file_name)


def _get_content(request, dbm, config):
    template = config.template() or _template_content(request, config) or ''
    return Template(template).render(RequestContext(request, {
        "dbm": dbm,
        "config": config,
        "filters": request.GET
    }))


def _template_content(request, config):
    request.GET = {}
    view, args, kwargs = resolve(config.template_url)
    args += (request,)
    return view(*args, **kwargs).content
