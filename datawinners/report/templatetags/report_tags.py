from django import template
import xml.etree.ElementTree as ET

from datawinners.report.aggregator import get_report_data
from datawinners.report.filter import get_filter_values, get_report_filters
from datawinners.report.template_resolver import resolve_data

register = template.Library()


@register.tag
def loop(parser, token):
    nodelist = parser.parse(('endloop',))
    parser.delete_first_token()
    return LoopNode(nodelist)


@register.simple_tag
def dist(qn):
    return "hello world"


@register.simple_tag
def count(qn):
    return "1"


@register.inclusion_tag('report/filters.html', takes_context=True)
def filters(context):
    report_filters = get_report_filters(context.get("dbm"), context.get("config"), context.get("config").questionnaires[0])
    _stopgap_load_previous_selected_values(context.get("filters"), report_filters)
    return {
        "report_id": context.get("report_id"),
        "idnr_filters": report_filters["idnr_filters"],
        "date_filters": report_filters["date_filters"]
    }


class LoopNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        filter_values = get_filter_values(context.get("dbm"), context.get("config"), context.get("filters"))
        data = get_report_data(context.get("dbm"), context.get("config"), filter_values[0], filter_values[1])
        resolved_data = resolve_data(self._parse_cell_values(), data)
        return self._generate_html(resolved_data)

    def _parse_cell_values(self):
        cells = ET.fromstring(self.nodelist[0].s).findall("./td")
        return [cell.text.replace("\"", "") for cell in cells]

    def _generate_html(self, resolved_data):
        return "".join(["<tr>%s</tr>" % "".join(["<td>%s</td>" % row[val] for val in self._parse_cell_values()]) for row in resolved_data])


def _stopgap_load_previous_selected_values(filter_values, report_filters):
    for report_filter in report_filters["idnr_filters"]:
        new_options = report_filter["field"].options
        if report_filter["field"].identifier in filter_values and \
                filter_values[report_filter["field"].identifier].split(";")[-1]:
            new_options = []
            for option in report_filter["field"].options:
                new_option = option
                if filter_values[report_filter["field"].identifier].split(";")[-1] == option[0]:
                    new_option = option + ('selected',)
                new_options.append(new_option)
        setattr(report_filter["field"], "new_options", new_options)
    for report_filter in report_filters["date_filters"]:
        if report_filter["field"].identifier in filter_values and \
                filter_values[report_filter["field"].identifier].split(";")[-1]:
            setattr(report_filter["field"], "value", filter_values[report_filter["field"].identifier].split(";")[-1])
