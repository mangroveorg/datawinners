# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from datawinners.location.LocationTree import LocationTree
from datawinners.main.utils import get_database_manager
from datawinners.messageprovider.message_handler import get_success_msg_for_registration_using
from datawinners.reporter.forms import ReporterRegistrationForm
import helper

from mangrove.errors.MangroveException import MangroveException, MultipleReportersForANumberException
from mangrove.transport.player.player import WebPlayer, Request
from mangrove.transport.submissions import SubmissionHandler
from mangrove.utils.types import is_empty
from mangrove.form_model.form_model import REGISTRATION_FORM_CODE


@login_required(login_url='/login')
def register(request):
    dbm = get_database_manager(request)
    if request.method == 'GET':
        location = LocationTree()
        form = ReporterRegistrationForm()
        return render_to_response('reporter/register.html', {'form': form}, context_instance=RequestContext(request))

    form = ReporterRegistrationForm(request.POST)
    message = None
    success = True
    form_errors = []
    form_errors.extend(form.non_field_errors())
    if form.is_valid():
        form_errors=[]
        form_data = {k: v for (k, v) in form.cleaned_data.items() if not is_empty(v)}
        try:
            entered_telephone_number = form_data.get("telephone_number")
            tel_number = _get_telephone_number(entered_telephone_number)
            if not helper.unique(dbm, tel_number):
                raise MultipleReportersForANumberException(entered_telephone_number)

            web_player = WebPlayer(dbm,SubmissionHandler(dbm))
            response = web_player.accept(
                Request(transport='web', message=_get_data(form_data), source='web', destination='mangrove'))
            message = get_success_msg_for_registration_using(response, "Reporter", "web")
        except MangroveException as exception:
            form_errors.append(exception.message)
            success = False

    return render_to_response('reporter/register.html', {'form': form, 'message': message, 'form_errors': form_errors , 'success': success},
                              context_instance=RequestContext(request))


def _get_location_heirarchy_from_location_name(display_location):
    if is_empty(display_location):
        return None
    lowest_level_location, high_level_location = tuple(display_location.split(','))
    tree = LocationTree()
    location_hierarchy = tree.get_hierarchy_path(lowest_level_location)
    return location_hierarchy


def _get_location_hierarchy(display_location,geo_code):
    location_hierarchy = _get_location_heirarchy_from_location_name(display_location)
    if location_hierarchy is None and geo_code is not None:
        lat_string,long_string=tuple(geo_code.split())
        tree=LocationTree()
        location_hierarchy=tree.get_location_hierarchy_for_geocode(lat=float(lat_string),long=float(long_string))
    return location_hierarchy


def _get_data(form_data):
    #TODO need to refactor this code. The master dictionary should be maintained by the registration form  model
    mapper = {'telephone_number': 'M', 'geo_code': 'G', 'Name': 'N', 'location': 'L'}
    data = dict()
    telephone_number = form_data.get('telephone_number')
    geo_code = form_data.get('geo_code')
    display_location=form_data.get('location')
    location_hierarchy = _get_location_hierarchy(display_location,geo_code)

    if telephone_number is not None:
        data[mapper['telephone_number']] = _get_telephone_number(telephone_number)
    if geo_code is not None:
        data[mapper['geo_code']] = geo_code
    if location_hierarchy is  not None:
    #TODO change this when we decide how we will process location
        data[mapper['location']] = str(location_hierarchy)

    data[mapper['Name']] = form_data.get('first_name')
    data['form_code'] = REGISTRATION_FORM_CODE
    data['T'] = 'Reporter'
    return data

def _get_telephone_number(number_as_given):
    return "".join([num for num in number_as_given if num.isdigit()])
