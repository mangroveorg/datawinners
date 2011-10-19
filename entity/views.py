# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from collections import defaultdict
import json
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_view_exempt, csrf_response_exempt
from django.views.decorators.http import require_http_methods
from django.utils.translation import ugettext as _
from datawinners.accountmanagement.models import NGOUserProfile, DataSenderOnTrialAccount,Organization
from datawinners.accountmanagement.views import is_datasender, is_new_user
from datawinners.entity import helper
from datawinners.location.LocationTree import get_location_tree
from datawinners.main.utils import get_database_manager
from datawinners.messageprovider.message_handler import get_success_msg_for_registration_using, get_submission_error_message_for, get_exception_message_for
from datawinners.project.models import Project
from mangrove.datastore.entity_type import get_all_entity_types, define_type
from datawinners.project import helper as project_helper, models
from datawinners.entity.forms import EntityTypeForm, ReporterRegistrationForm
from mangrove.errors.MangroveException import EntityTypeAlreadyDefined, MangroveException
from mangrove.form_model.form_model import REGISTRATION_FORM_CODE, MOBILE_NUMBER_FIELD_CODE, GEO_CODE, NAME_FIELD_CODE, LOCATION_TYPE_FIELD_CODE, ENTITY_TYPE_FIELD_CODE, REPORTER
from mangrove.transport.player.player import Request, WebPlayer, TransportInfo
from datawinners.entity import import_data as import_module
from mangrove.utils.types import is_empty

COUNTRY = ',MADAGASCAR'

def _associate_data_sender_to_project(dbm, project_id, response):
    project = Project.load(dbm.database, project_id)
    project.data_senders.append(response.short_code)
    project.save(dbm)


def _add_data_sender_to_trial_organization(telephone_number, org_id):
    data_sender = DataSenderOnTrialAccount.objects.model(mobile_number=telephone_number,
                                                         organization=Organization.objects.get(org_id=org_id))
    data_sender.save()


def _process_form(dbm, form, org_id):
    message = None
    if form.is_valid():
        telephone_number = form.cleaned_data["telephone_number"]
        
        if not helper.unique(dbm, telephone_number):
            form._errors['telephone_number'] = form.error_class([(u"Sorry, the telephone number %s has already been registered") % (telephone_number,)])
            return message

        organization = Organization.objects.get(org_id=org_id)
        if organization.in_trial_mode:
            if DataSenderOnTrialAccount.objects.filter(mobile_number=telephone_number).exists():
                form._errors['telephone_number'] = form.error_class([(u"Sorry, this number has already been used for a different DataWinners trial account.")])
                return message
            else:
                _add_data_sender_to_trial_organization(telephone_number,org_id)


        try:
            web_player = WebPlayer(dbm, get_location_tree())
            response = web_player.accept(Request(message=_get_data(form.cleaned_data),
                                                 transportInfo=TransportInfo(transport='web', source='web', destination='mangrove')))
            message = get_success_msg_for_registration_using(response, "web")
            project_id = form.cleaned_data["project_id"]
            if not is_empty(project_id):
                _associate_data_sender_to_project(dbm, project_id, response)
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
        web_player = WebPlayer(dbm, get_location_tree())
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
        message = _("Please add subject type and then add a subject") if message == "t should be present" else message
        success = False
        entity_id = None
    return HttpResponse(json.dumps({'success': success, 'message': message, 'entity_id': entity_id}))

@login_required(login_url='/login')
def create_datasender(request):
    if request.method == 'GET':
        form = ReporterRegistrationForm()
        return render_to_response('entity/create_datasender.html', {'form': form},
                                  context_instance=RequestContext(request))
    if request.method == 'POST':
        dbm = get_database_manager(request.user)
        form = ReporterRegistrationForm(request.POST)
        org_id = request.user.get_profile().org_id
        message= _process_form(dbm, form, org_id)
        if message is not None:
            form = ReporterRegistrationForm()
        return render_to_response('datasender_form.html',
                {'form': form, 'message': message},
                                      context_instance=RequestContext(request))


@login_required(login_url='/login')
def create_type(request):
    success = False
    form = EntityTypeForm(request.POST)
    if form.is_valid():
        entity_name = form.cleaned_data["entity_type_regex"]
        entity_name = [entity_name.lower()]
        try:
            manager = get_database_manager(request.user)
            define_type(manager, entity_name)
            message = _("Entity definition successful")
            success = True
        except EntityTypeAlreadyDefined:
            message = _("%s already registered as a subject type. Please select %s from the drop down menu.") %  (entity_name[0], entity_name[0])
    else:
        message = form.fields['entity_type_regex'].error_messages['invalid']
    return HttpResponse(json.dumps({'success': success, 'message': _(message)}))

@login_required(login_url='/login')
def create_subject(request):
    db_manager = get_database_manager(request.user)
    entity_types = get_all_entity_types(db_manager)
    project_helper.remove_reporter(entity_types)
    return render_to_response("entity/create_subject.html", {"post_url": reverse(submit), "entity_types": entity_types},
                              context_instance=RequestContext(request))


@csrf_view_exempt
@csrf_response_exempt
@login_required(login_url='/login')
@is_new_user
@is_datasender
def all_subjects(request):
    manager = get_database_manager(request.user)
    if request.method == 'POST':
        error_message, failure_imports, success_message, imported_entities = import_module.import_data(request, manager)
        subjects_data = import_module.load_all_subjects(request)
        return HttpResponse(json.dumps({'success': error_message is None and is_empty(failure_imports), 'message': success_message, 'error_message': error_message,
                                        'failure_imports': failure_imports, 'all_data': subjects_data}))

    subjects_data = import_module.load_all_subjects(request)
    return render_to_response('entity/all_subjects.html', {'all_data': subjects_data},
                                  context_instance=RequestContext(request))


def _get_project_association(projects):
    project_association = defaultdict(list)
    for project in projects:
        for datasender in project['value']['data_senders']:
            project_association[datasender].append(project['value']['name'])
    return project_association


def _get_all_datasenders(manager, projects, user):
    all_data_senders = import_module.load_all_subjects_of_type(manager)
    project_association = _get_project_association(projects)
    for datasender in all_data_senders:
        org_id = NGOUserProfile.objects.get(user=user).org_id
        user_profile = NGOUserProfile.objects.filter(reporter_id=datasender['short_name'], org_id = org_id)
        datasender['email'] = user_profile[0].user.email if len(user_profile) > 0 else "--"
        association = project_association.get(datasender['short_name'])
        datasender['projects'] = ' ,'.join(association) if association is not None else '--'
    return all_data_senders

@login_required(login_url='/login')
@csrf_view_exempt
def create_web_users(request):
    org_id = request.user.get_profile().org_id
    if request.method == 'POST':
        errors = []
        post_data = json.loads(request.POST['post_data'])
        for data in post_data:
            users  = User.objects.filter(email=data['email'])
            if len(users) > 0:
                errors.append("User with email %s already exists" % data['email'])
        if len(errors) > 0:
            return HttpResponseBadRequest(json.dumps(errors))

        for data in post_data:
            user = User.objects.create_user(data['email'], data['email'], 'test123')
            user.first_name = user.email
            group = Group.objects.filter(name="Data Senders")[0]
            user.groups.add(group)
            user.save()
            profile = NGOUserProfile(user=user, org_id=org_id, title="Mr", reporter_id=data['reporter_id'])
            profile.save()
            reset_form = PasswordResetForm({"email": user.email})
            reset_form.is_valid()
            reset_form.save()

        return HttpResponse(json.dumps("Users has been created"))


@csrf_view_exempt
@csrf_response_exempt
@login_required(login_url='/login')
@is_new_user
@is_datasender
def all_datasenders(request):
    manager = get_database_manager(request.user)
    projects = models.get_all_projects(manager)
    if request.method == 'POST':
        error_message, failure_imports, success_message, imported_entities = import_module.import_data(request, manager)
        all_data_senders = _get_all_datasenders(manager, projects, request.user)
        return HttpResponse(json.dumps({'success': error_message is None and is_empty(failure_imports), 'message': success_message, 'error_message': error_message,
                                        'failure_imports': failure_imports, 'all_data': all_data_senders}))
    all_data_senders = _get_all_datasenders(manager, projects, request.user)
    return render_to_response('entity/all_datasenders.html', {'all_data': all_data_senders, 'projects':projects},
                              context_instance=RequestContext(request))

@csrf_view_exempt
@csrf_response_exempt
@login_required(login_url='/login')
@is_new_user
def disassociate_datasenders(request):
    manager = get_database_manager(request.user)
    projects = [Project.load(manager.database, project_id) for project_id in request.POST.get('project_id').split(';')]
    for project in projects:
        [project.data_senders.remove(id) for id in request.POST['ids'].split(';') if id in project.data_senders]
        project.save(manager)
    return HttpResponse(reverse(all_datasenders))

@csrf_view_exempt
@csrf_response_exempt
@login_required(login_url='/login')
@is_new_user
def associate_datasenders(request):
    manager = get_database_manager(request.user)
    projects = [Project.load(manager.database, project_id) for project_id in request.POST.get('project_id').split(';')]
    for project in projects:
        project.data_senders.extend([id for id in request.POST['ids'].split(';') if not id in project.data_senders])
        project.save(manager)
    return HttpResponse(reverse(all_datasenders))

def _associate_data_senders_to_project(imported_entities, manager, project_id):
    project = Project.load(manager.database, project_id)
    project.data_senders.extend([k for k, v in imported_entities.items() if v == REPORTER])
    project.save(manager)


@csrf_view_exempt
@csrf_response_exempt
@require_http_methods(['POST'])
@login_required(login_url='/login')
def import_subjects_from_project_wizard(request):
    manager = get_database_manager(request.user)
    project_id = request.GET.get('project_id')
    error_message, failure_imports, success_message, imported_entities = import_module.import_data(request, manager)
    if project_id is not None:
        _associate_data_senders_to_project(imported_entities, manager, project_id)
    return HttpResponse(json.dumps({'success': error_message is None and is_empty(failure_imports), 'message': success_message, 'error_message': error_message,
                                    'failure_imports': failure_imports}))
