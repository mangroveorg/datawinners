# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from datawinners.accountmanagement.models import Organization


def registration_complete(request, user=None):
    return render_to_response('registration/registration_complete.html')


@login_required(login_url='/login')
def home(request):
    profile = request.user.get_profile()
    organization = Organization.objects.get(org_id=profile.org_id)
    return render_to_response('registration/home.html', {'organization': organization}, context_instance=RequestContext(request))
