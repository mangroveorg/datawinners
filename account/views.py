from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from datawinners.accountmanagement.models import Organization
from datawinners.account.forms import OrganizationForm

@login_required(login_url='/login')
def settings(request):
    if request.method == 'GET':
        profile = request.user.get_profile()
        organization = Organization.objects.get(org_id=profile.org_id)
        organization_form = OrganizationForm(instance = organization)
        return render_to_response("account/settings.html", {'organization_form' : organization_form}, context_instance=RequestContext(request))

    if request.method == 'POST':
        OrganizationForm.update(request.form, org_id)

