# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template.context import RequestContext

@login_required(login_url='/login')
def questionnaire(request):
    return render_to_response('project/questionnaire.html', context_instance=RequestContext(request))
  