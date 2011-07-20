# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import json
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_view_exempt, csrf_response_exempt
from django.views.decorators.http import require_http_methods
from datawinners import utils
from datawinners.entity import helper
from datawinners.location.LocationTree import LocationTree
from datawinners.main.utils import get_database_manager
from datawinners.messageprovider.message_handler import get_success_msg_for_registration_using, get_submission_error_message_for, get_exception_message_for
from mangrove.datastore.entity import get_all_entity_types, define_type
from datawinners.project import helper as project_helper
from datawinners.entity.forms import EntityTypeForm, ReporterRegistrationForm
from mangrove.errors.MangroveException import EntityTypeAlreadyDefined, MangroveException, MultipleReportersForANumberException
from mangrove.form_model.form_model import REGISTRATION_FORM_CODE, MOBILE_NUMBER_FIELD_CODE, GEO_CODE, NAME_FIELD_CODE, LOCATION_TYPE_FIELD_CODE,ENTITY_TYPE_FIELD_CODE
from mangrove.transport.player.player import Request, WebPlayer, TransportInfo
from mangrove.transport.reporter import find_reporter_entity
from mangrove.transport.submissions import SubmissionHandler
from mangrove.utils.types import is_empty
from datawinners.entity import import_data as import_module


def _validate_post_data(dbm, request):
    form = ReporterRegistrationForm(request.POST)
    message = None
    success = False
    form_errors = []
    form_errors.extend(form.non_field_errors())
    if form.is_valid():
        form_errors = []
        form_data = {k: v for (k, v) in form.cleaned_data.items() if not is_empty(v)}
        try:
            entered_telephone_number = form_data.get("telephone_number")
            tel_number = _get_telephone_number(entered_telephone_number)
            if not helper.unique(dbm, tel_number):
                raise MultipleReportersForANumberException(entered_telephone_number)

            web_player = WebPlayer(dbm, SubmissionHandler(dbm))
            response = web_player.accept(
                Request(message=_get_data(form_data), transportInfo=TransportInfo(transport='web',source='web', destination='mangrove')))
            message = get_success_msg_for_registration_using(response, "Reporter", "web")
            success = True
        except MangroveException as exception:
            form_errors.append(exception.message)
            success = False
    return form, form_errors, message, success


def _get_location_heirarchy_from_location_name(display_location):
    if is_empty(display_location):
        return None
    lowest_level_location, high_level_location = tuple(display_location.split(','))
    tree = LocationTree()
    location_hierarchy = tree.get_hierarchy_path(lowest_level_location)
    return location_hierarchy


def _get_location_hierarchy(display_location, geo_code):
    location_hierarchy = _get_location_heirarchy_from_location_name(display_location)
    if location_hierarchy is None and geo_code is not None:
        lat_string, long_string = tuple(geo_code.split())
        tree = LocationTree()
        location_hierarchy = tree.get_location_hierarchy_for_geocode(lat=float(lat_string), long=float(long_string))
    return location_hierarchy


def _get_data(form_data):
    #TODO need to refactor this code. The master dictionary should be maintained by the registration form  model
    mapper = {'telephone_number': MOBILE_NUMBER_FIELD_CODE, 'geo_code': GEO_CODE, 'Name': NAME_FIELD_CODE, 'location': LOCATION_TYPE_FIELD_CODE}
    data = dict()
    telephone_number = form_data.get('telephone_number')
    geo_code = form_data.get('geo_code')
    display_location = form_data.get('location')
    location_hierarchy = _get_location_hierarchy(display_location, geo_code)

    if telephone_number is not None:
        data[mapper['telephone_number']] = _get_telephone_number(telephone_number)
    if geo_code is not None:
        data[mapper['geo_code']] = geo_code
    if location_hierarchy is  not None:
    #TODO change this when we decide how we will process location
        data[mapper['location']] = location_hierarchy

    data[mapper['Name']] = form_data.get('first_name')
    data['form_code'] = REGISTRATION_FORM_CODE
    data[ENTITY_TYPE_FIELD_CODE] = 'Reporter'
    return data


def _get_telephone_number(number_as_given):
    return "".join([num for num in number_as_given if num.isdigit()])


def _get_submission_data(post, key):
    if post.get(key):
        return post.get(key)
    return None


def _get_submission(post):
    data = json.loads(post.get('data'))
    return {
        'transport': _get_submission_data(data, 'transport'),
        'source': _get_submission_data(data, 'source'),
        'destination': _get_submission_data(data, 'destination'),
        'message': _get_submission_data(data, 'message')
    }


#TODO This method has to be moved into a proper place since this is used for registering entities.
@csrf_view_exempt
@csrf_response_exempt
@require_http_methods(['POST'])
@login_required(login_url='/login')
def submit(request):
    mapper = {'telephone_number': MOBILE_NUMBER_FIELD_CODE, 'geo_code': GEO_CODE, 'Name': NAME_FIELD_CODE, 'location': LOCATION_TYPE_FIELD_CODE}
    dbm = get_database_manager(request)
    post = _get_submission(request.POST)
    success = True
    try:
        web_player = WebPlayer(dbm, SubmissionHandler(dbm))
        message = {k: v for (k, v) in post.get('message').items() if not is_empty(v)}
        display_location = message.get(mapper['location'])
        geo_code = message.get(mapper['geo_code'])
        location_hierarchy = _get_location_hierarchy(display_location, geo_code)
        if location_hierarchy is  not None:
            message[mapper['location']] = location_hierarchy
        request = Request(message=message, transportInfo=TransportInfo(transport=post.get('transport'), source=post.get('source'),
                                                          destination=post.get('destination')))
        response = web_player.accept(request)
        if response.success:
            message = get_success_msg_for_registration_using(response, "Subject", "web")
        else:
            message = get_submission_error_message_for(response.errors)
        entity_id = response.datarecord_id
    except MangroveException as exception:
        message = get_exception_message_for(exception=exception, channel="web")
        success = False
        entity_id = None
    return HttpResponse(json.dumps({'success': success, 'message': message, 'entity_id': entity_id}))


def create_datasender(request):
    """

    """
    if request.method == 'GET':
        form = ReporterRegistrationForm()
        return render_to_response('entity/create_datasender.html', {'form': form},
                                  context_instance=RequestContext(request))
    if request.method == 'POST':
        dbm = get_database_manager(request)
        form, form_errors, message, success = _validate_post_data(dbm, request)
        if success:
            form = ReporterRegistrationForm()
        response = render_to_response('datasender_form.html',
                {'form': form, 'message': message, 'form_errors': form_errors, 'success': success},
                                      context_instance=RequestContext(request))
        return response


def create_type(request):
    message = ""
    success = False
    form = EntityTypeForm(request.POST)
    if form.is_valid():
        entity_name = form.cleaned_data["entity_type_create"]
        entity_name = [entity_name.lower()]
        try:
            manager = get_database_manager(request)
            define_type(manager, entity_name)
            message = "Entity definition successful"
            success=True
        except EntityTypeAlreadyDefined as type_already_defined:
            message = type_already_defined.message
            success=False
    return HttpResponse(json.dumps({'success': success, 'message': message}))

def create_subject(request):
    db_manager = get_database_manager(request)
    entity_types = get_all_entity_types(db_manager)
    project_helper.remove_reporter(entity_types)
    return render_to_response("entity/create_subject.html", {"post_url": reverse(submit), "entity_types": entity_types},
                              context_instance=RequestContext(request))


@csrf_view_exempt
@csrf_response_exempt
@login_required(login_url='/login')
@utils.is_new_user
def all_subjects(request):
    manager = get_database_manager(request)
    if request.method == 'POST':
        error_message, failure_imports, success, success_message = import_module.import_data(request,manager)
        subjects_data = import_module.load_all_subjects(request)
        return HttpResponse(json.dumps({'success': success, 'message': success_message, 'error_message': error_message,
                                        'failure_imports': failure_imports, 'all_data': subjects_data}))

    subjects_data = import_module.load_all_subjects(request)
    return render_to_response('entity/all_subjects.html', {'all_data': subjects_data},
                              context_instance=RequestContext(request))

@csrf_view_exempt
@csrf_response_exempt
@login_required(login_url='/login')
@utils.is_new_user
def all_datasenders(request):
    manager = get_database_manager(request)
    if request.method == 'POST':
        error_message, failure_imports, success, success_message = import_module.import_data(request,manager)
        all_data_senders = import_module.load_all_subjects_of_type(request)

        return HttpResponse(json.dumps({'success': success, 'message': success_message, 'error_message': error_message,
                                    'failure_imports': failure_imports, 'all_data':all_data_senders}))
    all_data_senders = import_module.load_all_subjects_of_type(request)
    return render_to_response('entity/all_datasenders.html', {'all_data': all_data_senders}, context_instance=RequestContext(request))



@csrf_view_exempt
@csrf_response_exempt
@require_http_methods(['POST'])
@login_required(login_url='/login')
def import_subjects_from_project_wizard(request):
    manager = get_database_manager(request)
    error_message, failure_imports, success, success_message = import_module.import_data(request,manager)
    return HttpResponse(json.dumps({'success': success, 'message': success_message, 'error_message': error_message,
                                    'failure_imports': failure_imports}))
