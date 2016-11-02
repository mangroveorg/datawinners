from django.template import RequestContext
from django.views.generic import TemplateView


class AllReportsView(TemplateView):
    template_name = 'report/index.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response(RequestContext(request))