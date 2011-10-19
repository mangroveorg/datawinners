# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from django.views.generic.base import TemplateView

class FeatureAwareTemplateView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super(FeatureAwareTemplateView, self).get_context_data(**kwargs)
        return RequestContext(self.request, context)


def index(request):
    return render_to_response('home/index_en.html', RequestContext(request))

def switch_language(request, language):
    request.session['django_language'] = language
    if request.META.has_key('HTTP_REFERER'):
        referer= '/' + '/'.join(request.META['HTTP_REFERER'].split('/')[3:])
    else:
        referer= '/'
    return redirect(referer)
