from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template.context import RequestContext

def registration_complete(request,user=None):
    return render_to_response('registration/registration_complete.html')

@login_required(login_url='/login')
def home(request):
    print request.user
    return render_to_response('registration/home.html',context_instance=RequestContext(request))