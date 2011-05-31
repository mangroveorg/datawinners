from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from datawinners.main.utils import get_database_manager
from datawinners.messageprovider.message_handler import get_success_msg_for_registration_using
from datawinners.reporter.forms import ReporterRegistrationForm

from mangrove.errors.MangroveException import MangroveException
from mangrove.transport.submissions import SubmissionHandler, Request
from mangrove.utils.types import is_empty


@login_required(login_url='/login')
def register(request):
    if request.method == 'GET':
        form = ReporterRegistrationForm()
        return render_to_response('reporter/register.html', {'form': form}, context_instance=RequestContext(request))
    form = ReporterRegistrationForm(request.POST)
    message = None
    success = True

    if form.is_valid():
        form_data = {k: v for (k, v) in form.cleaned_data.items() if not is_empty(v)}
        try:
            s = SubmissionHandler(dbm=get_database_manager(request))
            response = s.accept(
                Request(transport='web', message=_get_data(form_data), source='web', destination='mangrove'))
            message = get_success_msg_for_registration_using(response)
        except MangroveException as exception:
            message = exception.message
            success = False

    return render_to_response('reporter/register.html', {'form': form, 'message': message, 'success': success},
                              context_instance=RequestContext(request))


def _get_data(form_data):

    #TODO need to refactor this code. The master dictionary should be maintained by the registration form  model
    mapper = {'telephone_number': 'M', 'geo_code': 'G', 'Name': 'N', 'commune': 'L'}
    data = dict()
    telephone_number = form_data.get('telephone_number')
    geo_code = form_data.get('geo_code')
    commune = form_data.get('commune')

    if telephone_number is not None:
        data[mapper['telephone_number']] = telephone_number
    if geo_code is not None:
        data[mapper['geo_code']] = geo_code
    if commune is  not None:
        data[mapper['commune']] = commune

    data[mapper['Name']] = " ".join([form_data.get('first_name'),form_data.get('last_name')])
    data['form_code'] = 'REG'
    data['T'] = 'Reporter'
    return data


