from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template.context import RequestContext

def registration_complete(request,user=None):
#    user = request.user
#    print user
#    organization = Organization.objects.get(org_id=user.organization_id)[0]
#    {'organization' : organization,'user':user}, context_instance=RequestContext(request)
#    user = kwargs.get('user')
#     {'user':user}, context_instance=RequestContext(request)

    return render_to_response('registration/registration_complete.html')

@login_required(login_url='/login')
def home(request):
    print request.user
    return render_to_response('registration/home.html',context_instance=RequestContext(request))