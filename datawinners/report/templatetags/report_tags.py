from django import template
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
        output = self.nodelist.render(context)
        return output