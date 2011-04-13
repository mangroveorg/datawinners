from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from accountmanagement.models import Organization
from datawinners.reporter.forms import ReporterRegistrationForm

from datastore import datarecord


@login_required(login_url='/login')
def register(request):
    if request.method =='GET':
        form = ReporterRegistrationForm()
        return render_to_response('reporter/register.html', {'form' : form},context_instance=RequestContext(request))
    form = ReporterRegistrationForm(request.POST)
    if form.is_valid():
        profile = request.user.get_profile()
        organization = Organization.objects.get(org_id=profile.org_id)
        form_data = form.cleaned_data
        print form_data
        data =[(k,v) for k,v in form_data.items()]
        datarecord.register(entity_type=[organization.name, "Reporter"], data=data, location=[], source = "Web")
    return render_to_response('reporter/register.html', {'form' : form},context_instance=RequestContext(request))
