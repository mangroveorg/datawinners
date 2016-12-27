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
    return {
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
