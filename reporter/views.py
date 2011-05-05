from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from mangrove.datastore.database import get_db_manager
from datawinners.reporter.forms import ReporterRegistrationForm

from mangrove.datastore import datarecord
from mangrove.datastore.datadict import DataDictType


@login_required(login_url='/login')
def register(request):
    if request.method == 'GET':
        form = ReporterRegistrationForm()
        return render_to_response('reporter/register.html', {'form': form},context_instance=RequestContext(request))
    form = ReporterRegistrationForm(request.POST)
    message = None
    if form.is_valid():
        form_data = form.cleaned_data
        manager = get_db_manager()
        dummy_type = DataDictType(manager, name='Dummy Type', slug='dummy_type', primitive_type='string')
        data = [(k, v, dummy_type) for (k,v) in form_data.items()]
        registered_reporter = datarecord.register(manager,entity_type=["Reporter"], data=data, location=[],
                                                  source="Web")
        form = ReporterRegistrationForm()
        message = "The reporter was successfully registered with id %s" % registered_reporter.id
    return render_to_response('reporter/register.html', {'form': form, 'message': message},context_instance=RequestContext(request))
