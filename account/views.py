from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template.context import RequestContext

@login_required(login_url='/login')
def settings(request):
    return render_to_response("account/settings.html", context_instance=RequestContext(request))
