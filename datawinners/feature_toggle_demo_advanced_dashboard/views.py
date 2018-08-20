# Create your views here.
from datawinners.accountmanagement.decorators import valid_web_user
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from waffle.decorators import waffle_flag

@valid_web_user
@waffle_flag('advanced_dashboard', 'dashboard')
def advanced_dashboard(request):
    context = {}
    return render_to_response('advanced_dashboard/home.html',
                              context, context_instance=RequestContext(request))    