from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from datawinners.accountmanagement.models import Organization

@login_required(login_url='/login')
def settings(request):
    profile = request.user.get_profile()
    organization = Organization.objects.get(org_id=profile.org_id)
    return render_to_response("account/settings.html", {'organization' : organization}, context_instance=RequestContext(request))
