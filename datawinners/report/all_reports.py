import json

from django.http import HttpResponse
from django.template import RequestContext, Template
from django.views.generic import TemplateView
from mangrove.datastore.report_config import get_report_configs, get_report_config

from datawinners.main.database import get_database_manager
from datawinners.report.aggregator import get_report_data, get_report_filters, get_total_count, BATCH_SIZE


class AllReportsView(TemplateView):
    template_name = 'report/index.html'

    def get(self, request, *args, **kwargs):
        dbm = get_database_manager(request.user)
        configs = get_report_configs(dbm)
        return self.render_to_response(RequestContext(request, {
            "configs": configs
        }))


def report_content(request, report_id):
    dbm = get_database_manager(request.user)
    config = get_report_config(dbm, report_id)
    content, count = _build_report_content(dbm, config, request)
    return HttpResponse(
        json.dumps(
            {
                "content": content,
                "totalCount": get_total_count(dbm, config),
                "count": count,
                "pageSize": BATCH_SIZE
            }),
        content_type='application/json')


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


def _build_report_content(dbm, config, request):
    content = ""
    content += _get_style_content(config)
    data_content, data_count = _get_content(dbm, config, request)
    content += data_content
    return content, data_count


def _get_style_content(config):
    return '<link rel="stylesheet" href="/reports/' + config.id + '/stylesheet/" />'


def _get_content(dbm, config, request):
    filters = get_report_filters(dbm, config)
    page_number = request.GET.get("page_number") or "1"
    data = get_report_data(dbm, config, int(page_number))
    return Template(config.template()).render(RequestContext(request, {
        "report_data": data,
        "idnr_filters": filters["idnr_filters"],
        "date_filters": filters["date_filters"],
        "report_id": "report_" + config.id
    })), len(data)
