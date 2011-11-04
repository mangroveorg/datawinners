import json
import urlparse
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import  HttpResponseServerError, HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from datawinners.accountmanagement.models import Organization
from datawinners.accountmanagement.views import is_datasender
from datawinners.main.utils import get_database_manager
from datawinners.project import helper
from datawinners.project.forms import CreateProject, ReminderForm
from datawinners.project.models import Project, ProjectState, Reminder
from mangrove.datastore.entity_type import get_all_entity_types
from mangrove.errors.MangroveException import DataObjectAlreadyExists, QuestionCodeAlreadyExistsException, EntityQuestionAlreadyExistsException, FormModelDoesNotExistsException
from django.contrib import messages
from mangrove.form_model.field import field_to_json
from mangrove.form_model.form_model import  FormModel, get_form_model_by_code
from mangrove.utils.types import is_string, is_empty

def create_questionnaire(post, manager, entity_type, name):
    entity_type = [entity_type] if is_string(entity_type) else entity_type
    questionnaire_code = post['questionnaire-code'].lower()
    json_string = post['question-set']
    question_set = json.loads(json_string)
    form_model = FormModel(manager, entity_type=entity_type, name=name, type='survey', state=post['state'], fields=[], form_code=questionnaire_code)
    return helper.update_questionnaire_with_questions(form_model, question_set, manager)


def update_questionnaire(questionnaire, post, entity_type, name, manager):
    json_string = post['question-set']
    question_set = json.loads(json_string)
    questionnaire = helper.update_questionnaire_with_questions(questionnaire, question_set, manager)
    questionnaire.name = name
    questionnaire.entity_type = [entity_type] if is_string(entity_type) else entity_type
    questionnaire.form_code = post['questionnaire-code'].lower()
    return questionnaire

@login_required()
def save_project(request):
    manager = get_database_manager(request.user)
    entity_list = get_all_entity_types(manager)
    entity_list = helper.remove_reporter(entity_list)

    form = CreateProject(data=dict(urlparse.parse_qsl(request.POST['profile_form'])), entity_list=entity_list)
    project_id = request.POST['pid']
    project_state = request.POST['state']
    if form.is_valid():
        entity_type = form.cleaned_data['entity_type']
        project_name = form.cleaned_data["name"]
        if is_empty(project_id):
            try:
                get_form_model_by_code(manager, request.POST['questionnaire-code'])
                return HttpResponseServerError('Questionnaire with this code already exists')
            except FormModelDoesNotExistsException:
                project = Project(name=project_name, goals=form.cleaned_data["goals"],
                              project_type='survey', entity_type=entity_type,
                              reminder_and_deadline=helper.new_deadline_and_reminder(form.cleaned_data),
                              activity_report=form.cleaned_data['activity_report'],
                              state =project_state, devices=[],language=form.cleaned_data['language'])
                try:
                    questionnaire = create_questionnaire(post=request.POST, manager=manager, entity_type=entity_type, name=project_name)
                except QuestionCodeAlreadyExistsException as e:
                    return HttpResponseServerError(e)
                except EntityQuestionAlreadyExistsException as e:
                    return HttpResponseServerError(e.message)

        else :
            project = Project.load(manager.database, project_id)
            questionnaire = FormModel.get(manager, project.qid)
            if project.state == ProjectState.INACTIVE:
                if project_state == ProjectState.TEST:
                    project.state = ProjectState.TEST
                    questionnaire.set_test_mode()
            project.reminder_and_deadline=helper.new_deadline_and_reminder(form.cleaned_data)
            project.update(form.cleaned_data)
            try:
                questionnaire = update_questionnaire(questionnaire, request.POST, entity_type, project_name, manager)
            except QuestionCodeAlreadyExistsException as e:
                return HttpResponseServerError(e)
            except EntityQuestionAlreadyExistsException as e:
                return HttpResponseServerError(e.message)
            except DataObjectAlreadyExists as e:
                if e.message.find("Form") >= 0:
                    return HttpResponseServerError("Questionnaire with this code already exists")
                return HttpResponseServerError(e.message)
        try:
            pid = project.save(manager)
            qid = questionnaire.save()
            project.qid = qid
            pid = project.save(manager)
        except DataObjectAlreadyExists as e:
            messages.error(request, e.message)
            return render_to_response('project/create_project.html', {'form': form},
                                      context_instance=RequestContext(request))
        from datawinners.project.views import project_overview, index
        if project.state == ProjectState.INACTIVE:
            return HttpResponse(json.dumps({'redirect_url': reverse(index)}))
        return HttpResponse(json.dumps({'redirect_url': reverse(project_overview, args=[pid])}))


@login_required(login_url='/login')
def create_project(request):
    manager = get_database_manager(request.user)
    entity_list = get_all_entity_types(manager)
    entity_list = helper.remove_reporter(entity_list)
    if request.method == 'GET':
        form = CreateProject(entity_list=entity_list)
        activity_report_questions = json.dumps(helper.get_activity_report_questions(manager), default=field_to_json)
        subject_report_questions = json.dumps(helper.get_subject_report_questions(manager), default=field_to_json)
        return render_to_response('project/create_project.html',
                {'form':form,"activity_report_questions": repr(activity_report_questions),
                 'subject_report_questions':repr(subject_report_questions),
                 'existing_questions': repr(subject_report_questions), 'questionnaire_code': helper.generate_questionnaire_code(manager)},context_instance=RequestContext(request))

@login_required(login_url='/login')
@is_datasender
def edit_project(request, project_id=None):
    manager = get_database_manager(request.user)
    entity_list = get_all_entity_types(manager)
    entity_list = helper.remove_reporter(entity_list)
    project = Project.load(manager.database, project_id)
    if request.method == 'GET':
        form = CreateProject(data=(_generate_project_info_with_deadline_and_reminders(project)), entity_list=entity_list)
        activity_report_questions = json.dumps(helper.get_activity_report_questions(manager), default=field_to_json)
        subject_report_questions = json.dumps(helper.get_subject_report_questions(manager), default=field_to_json)
        questionnaire = FormModel.get(manager, project.qid)
        fields = questionnaire.fields
        if questionnaire.entity_defaults_to_reporter():
            fields = helper.hide_entity_question(questionnaire.fields)
        existing_questions = json.dumps(fields, default=field_to_json)

        return render_to_response('project/create_project.html',
                                  {'form':form,"activity_report_questions": repr(activity_report_questions),
                 'subject_report_questions':repr(subject_report_questions),
                 'existing_questions': repr(existing_questions), 'questionnaire_code': questionnaire.form_code, 'project':project},
                                  context_instance=RequestContext(request))


def _generate_project_info_with_deadline_and_reminders(project):
    project_info = {}
    for key, value in project.items():
        project_info[key] = value
    for key, value in project['reminder_and_deadline'].items():
        project_info[key] = value
    del project_info['reminder_and_deadline']
    return project_info

@login_required(login_url='/login')
@is_datasender
def reminders(request, project_id):
    if request.method == 'GET':
        dbm = get_database_manager(request.user)
        project = Project.load(dbm.database, project_id)
        questionnaire = FormModel.get(dbm, project.qid)
        from datawinners.project.views import _make_project_links
        project_links = _make_project_links(project, questionnaire.form_code)
        reminders = Reminder.objects.filter(voided=False, project_id=project_id).order_by('id')
        profile = request.user.get_profile()
        organization = Organization.objects.get(org_id=profile.org_id)
        from datawinners.project.views import  _format_reminders, create_reminder
        return render_to_response('project/reminders.html',
                {'project': project, 
                 'reminders':_format_reminders(reminders, project_id),
                 'in_trial_mode':organization.in_trial_mode,
                 'create_reminder_link' : reverse(create_reminder, args=[project_id]),
                 'project_links': project_links},
                                  context_instance=RequestContext(request))


@login_required(login_url='/login')
@is_datasender
def reminder_settings(request, project_id):
    dbm = get_database_manager(request.user)
    project = Project.load(dbm.database, project_id)
    questionnaire = FormModel.get(dbm, project.qid)
    from datawinners.project.views import _make_project_links
    project_links = _make_project_links(project, questionnaire.form_code)
    if request.method == 'GET':
        form = ReminderForm(data=(_generate_project_info_with_deadline_and_reminders(project)))
        return render_to_response('project/reminder_settings.html',
                {'project_links': project_links,'project': project,
                 'form':form},context_instance=RequestContext(request))

    form = ReminderForm(data=request.POST)
    if form.is_valid():
        project.reminder_and_deadline=helper.deadline_and_reminder(form.cleaned_data)
        project.save(dbm)
        messages.success(request, 'Reminder settings saved successfully')
        return render_to_response('project/reminder_settings.html',
                {'project_links': project_links,'project': project,
                 'form':form},context_instance=RequestContext(request))
