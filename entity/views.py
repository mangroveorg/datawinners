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
from datawinners.main.utils import get_database_manager
from datawinners.messageprovider.message_handler import get_success_msg_for_registration_using, get_submission_error_message_for, get_exception_message_for
from mangrove.datastore.entity import get_all_entity_types, define_type
from datawinners.project import helper as project_helper
from datawinners.entity.forms import EntityTypeForm, ReporterRegistrationForm
from mangrove.errors.MangroveException import EntityTypeAlreadyDefined, MangroveException, MultipleReportersForANumberException
from mangrove.form_model.form_model import REGISTRATION_FORM_CODE, MOBILE_NUMBER_FIELD_CODE, GEO_CODE, NAME_FIELD_CODE, LOCATION_TYPE_FIELD_CODE, ENTITY_TYPE_FIELD_CODE
from mangrove.transport.player.player import Request, WebPlayer, TransportInfo
from mangrove.utils.types import is_empty
from datawinners.entity import import_data as import_module

COUNTRY = ',MADAGASCAR'

def _validate_form(dbm, form):
    message = None
    if form.is_valid():
        telephone_number = form.cleaned_data["telephone_number"]
        if not helper.unique(dbm, telephone_number):
            form._errors['telephone_number'] = form.error_class([(u"Sorry, the telephone number %s has already been registered") % (telephone_number,)])
            return message

        try:
            web_player = WebPlayer(dbm)
            response = web_player.accept(Request(message=_get_data(form.cleaned_data),
                        transportInfo=TransportInfo(transport='web', source='web', destination='mangrove')))
            message = get_success_msg_for_registration_using(response, "web")
        except MangroveException as exception:
            message = exception.message

    return message


def _get_data(form_data):
    #TODO need to refactor this code. The master dictionary should be maintained by the registration form  model
    mapper = {'telephone_number': MOBILE_NUMBER_FIELD_CODE, 'geo_code': GEO_CODE, 'Name': NAME_FIELD_CODE,
              'location': LOCATION_TYPE_FIELD_CODE}
    data = dict()
    data[mapper['telephone_number']] = form_data.get('telephone_number')
    data[mapper['location']] = form_data.get('location') + COUNTRY if form_data.get('location') is not None else None
    data[mapper['geo_code']] = form_data.get('geo_code')
    data[mapper['Name']] = form_data.get('first_name')
    data['form_code'] = REGISTRATION_FORM_CODE
    data[ENTITY_TYPE_FIELD_CODE] = 'Reporter'
    return data

#TODO This method has to be moved into a proper place since this is used for registering entities.
@csrf_view_exempt
@csrf_response_exempt
@require_http_methods(['POST'])
@login_required(login_url='/login')
def submit(request):
    dbm = get_database_manager(request.user)
    post = json.loads(request.POST['data'])
    success = True
    try:
        web_player = WebPlayer(dbm)
        message = post['message']
        if message.get(LOCATION_TYPE_FIELD_CODE) is not None:
            message[LOCATION_TYPE_FIELD_CODE] += COUNTRY
        request = Request(message=message,
                          transportInfo=TransportInfo(transport=post.get('transport'), source=post.get('source'),
                                                      destination=post.get('destination')))
        response = web_player.accept(request)
        if response.success:
            message = get_success_msg_for_registration_using(response, "web")
        else:
            message = get_submission_error_message_for(response.errors)
        entity_id = response.datarecord_id
    except MangroveException as exception:
        message = get_exception_message_for(exception=exception, channel="web")
        success = False
        entity_id = None
    return HttpResponse(json.dumps({'success': success, 'message': message, 'entity_id': entity_id}))


def create_datasender(request):
    if request.method == 'GET':
        form = ReporterRegistrationForm()
        return render_to_response('entity/create_datasender.html', {'form': form},
                                  context_instance=RequestContext(request))
    if request.method == 'POST':
        dbm = get_database_manager(request.user)
        form = ReporterRegistrationForm(request.POST)
        message= _validate_form(dbm, form)
        return render_to_response('datasender_form.html',
                {'form': form, 'message': message},
                                      context_instance=RequestContext(request))

def create_type(request):
    success = False
    form = EntityTypeForm(request.POST)
    if form.is_valid():
        entity_name = form.cleaned_data["entity_type_regex"]
        entity_name = [entity_name.lower()]
        try:
            manager = get_database_manager(request.user)
            define_type(manager, entity_name)
            message = "Entity definition successful"
            success = True
        except EntityTypeAlreadyDefined:
            message = "This subject has already been added."
    else:
        message = form.fields['entity_type_regex'].error_messages['invalid']
    return HttpResponse(json.dumps({'success': success, 'message': message}))


def create_subject(request):
    db_manager = get_database_manager(request.user)
    entity_types = get_all_entity_types(db_manager)
    project_helper.remove_reporter(entity_types)
    return render_to_response("entity/create_subject.html", {"post_url": reverse(submit), "entity_types": entity_types},
                              context_instance=RequestContext(request))


@csrf_view_exempt
@csrf_response_exempt
@login_required(login_url='/login')
@utils.is_new_user
def all_subjects(request):
    manager = get_database_manager(request.user)
    if request.method == 'POST':
        error_message, failure_imports, success, success_message = import_module.import_data(request, manager)
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
    manager = get_database_manager(request.user)
    if request.method == 'POST':
        error_message, failure_imports, success, success_message = import_module.import_data(request, manager)
        all_data_senders = import_module.load_all_subjects_of_type(manager)

        return HttpResponse(json.dumps({'success': success, 'message': success_message, 'error_message': error_message,
                                        'failure_imports': failure_imports, 'all_data': all_data_senders}))
    all_data_senders = import_module.load_all_subjects_of_type(manager)
    return render_to_response('entity/all_datasenders.html', {'all_data': all_data_senders},
                              context_instance=RequestContext(request))


@csrf_view_exempt
@csrf_response_exempt
@require_http_methods(['POST'])
@login_required(login_url='/login')
def import_subjects_from_project_wizard(request,project_id=None):
    manager = get_database_manager(request.user)
    error_message, failure_imports, success, success_message = import_module.import_data(request, manager)
    return HttpResponse(json.dumps({'success': success, 'message': success_message, 'error_message': error_message,
                                    'failure_imports': failure_imports}))
