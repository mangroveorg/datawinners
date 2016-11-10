from django import template
import xml.etree.ElementTree as ET
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


class LoopNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        resolved_data = resolve_data(self._parse_cell_values(), context.get("report_data"))
        return self._generate_html(resolved_data)

    def _parse_cell_values(self):
        cells = ET.fromstring(self.nodelist[0].s).findall("./td")
        return [cell.text.replace("\"", "") for cell in cells]

    def _generate_html(self, resolved_data):
        return "".join(["<tr>%s</tr>" % "".join(["<td>%s</td>" % row[val] for val in self._parse_cell_values()]) for row in resolved_data])
