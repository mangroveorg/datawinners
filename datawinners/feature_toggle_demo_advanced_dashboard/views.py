# Create your views here.
from datawinners.accountmanagement.decorators import valid_web_user,\
    is_datasender
from django.shortcuts import render_to_response
from django.template.context import RequestContext

@valid_web_user
@is_datasender
def advanced_dashboard(request):
    context = {}
    return render_to_response('advanced_dashboard/home.html',
                              context, context_instance=RequestContext(request))    