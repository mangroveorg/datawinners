from django.http import HttpResponse
from django.template import RequestContext, Template
from django.views.generic import TemplateView

from datawinners.main.database import get_database_manager
from datawinners.report.aggregator import get_report_data, get_report_filters
from mangrove.datastore.report_config import get_report_configs, get_report_config


class AllReportsView(TemplateView):
    template_name = 'report/index.html'

    def get(self, request, *args, **kwargs):
        dbm = get_database_manager(request.user)
        configs = get_report_configs(dbm)
        return self.render_to_response(RequestContext(request, {
            "configs": configs,
            "content": (configs or '') and Template(_build_report_content(dbm, configs[0], request)).render(
                RequestContext(request))
        }))


def report_content(request, report_id):
    dbm = get_database_manager(request.user)
    config = get_report_config(dbm, report_id)
    content = _build_report_content(dbm, config, request)
    return HttpResponse(content)


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
    content += _get_content(dbm, config, request)
    return content


def _get_style_content(config):
    return '<link rel="stylesheet" href="/reports/' + config.id + '/stylesheet/" />'


def _get_content(dbm, config, request):
    page_number = request.GET.get("page_number") or "1"
    return Template(config.template()).render(RequestContext(request, {
        "report_data": get_report_data(dbm, config, int(page_number)),
        "report_filters": get_report_filters(dbm, config),
        "report_id": "report_" + config.id
    }))


# Add questionnaire id if condition of the map function for effective indexing
def create_report_view(request, report_id):
    dbm = get_database_manager(request.user)
    config = get_report_config(dbm, report_id)
    sort_fields = [_form_key_for_couch_view(field) for field in config.sort_fields]
    combined_view_key = ",".join(sort_fields)
    dbm.create_view(_report_view_name(report_id),
                    "function(doc) { if(doc.document_type == 'SurveyResponse') {  emit([%s], 1) } }" % (combined_view_key),
                    "")
    return HttpResponse("Created")


def delete_report_view(request, report_id):
    dbm = get_database_manager(request.user)
    del dbm.database["_design/"+_report_view_name(report_id)]
    return HttpResponse("deleted")


def _form_key_for_couch_view(field_path):
    root_path = "doc.values"
    temp_path = ""
    for field in field_path.split(".")[1:]:
        temp_path += "['"
        temp_path += field
        temp_path += "'][0]"
    return root_path + temp_path[:-3]


def _report_view_name(report_id):
    return "report_" + report_id
