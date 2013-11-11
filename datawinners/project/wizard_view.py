import json
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.translation import ugettext
from django.views.decorators.csrf import csrf_exempt
from datawinners.accountmanagement.decorators import is_datasender, session_not_expired, is_not_expired
from datawinners.accountmanagement.models import Organization, NGOUserProfile
from datawinners.accountmanagement.views import get_ngoprofiles_for_all_users_in_account
from datawinners.project import helper
from datawinners.project.forms import CreateProject, ReminderForm
from datawinners.project.models import Project, ProjectState, Reminder, ReminderMode, get_all_projects, get_all_project_names
from datawinners.main.database import get_database_manager
from mangrove.datastore.entity_type import get_all_entity_types
from mangrove.errors.MangroveException import DataObjectAlreadyExists, QuestionCodeAlreadyExistsException, EntityQuestionAlreadyExistsException, QuestionAlreadyExistsException
from django.contrib import messages
from mangrove.form_model.field import field_to_json
from mangrove.utils.types import is_string
from django.utils.translation import ugettext as _
from datawinners.utils import get_organization, generate_project_name
from mangrove.form_model.form_model import  FormModel
from datawinners.activitylog.models import UserActivityLog
from datawinners.utils import get_changed_questions
from datawinners.common.constant import CREATED_PROJECT, EDITED_PROJECT, ACTIVATED_REMINDERS, DEACTIVATED_REMINDERS, SET_DEADLINE
from datawinners.questionnaire.questionnaire_builder import QuestionnaireBuilder
from datawinners.project.helper import is_project_exist
from datawinners.project.utils import is_quota_reached

def create_questionnaire(post, manager, entity_type, name, language):
    entity_type = [entity_type] if is_string(entity_type) else entity_type
    questionnaire_code = post['questionnaire-code'].lower()
    json_string = post['question-set']
    question_set = json.loads(json_string)
    form_model = FormModel(manager, entity_type=entity_type, name=name, type='survey',
        state=post['project_state'], fields=[], form_code=questionnaire_code, language=language)
    QuestionnaireBuilder(form_model, manager).update_questionnaire_with_questions(question_set)
    return form_model


def update_questionnaire(questionnaire, post, entity_type, name, manager, language):
    questionnaire.name = name
    questionnaire.activeLanguages = [language]
    questionnaire.entity_type = [entity_type] if is_string(entity_type) else entity_type
    questionnaire.form_code = post['questionnaire-code'].lower()
    json_string = post['question-set']
    question_set = json.loads(json_string)
    QuestionnaireBuilder(questionnaire, manager).update_questionnaire_with_questions(question_set)
    questionnaire.deactivate() if post['project_state'] == ProjectState.INACTIVE else questionnaire.set_test_mode()
    return questionnaire


def get_preview_and_instruction_links():
    links = {
        'sms_preview': reverse("sms_preview"),
        'web_preview': reverse("web_preview"),
        'smart_phone_preview': reverse("smart_phone_preview"),
    }
    return links


@login_required(login_url='/login')
@session_not_expired
@csrf_exempt
@is_not_expired
def create_project(request):
    manager = get_database_manager(request.user)
    entity_list = get_all_entity_types(manager)
    entity_list = helper.remove_reporter(entity_list)
    all_projects_name = get_all_project_names(get_database_manager(request.user))
    name = generate_project_name(all_projects_name)
    project_summary = dict(name=name)
    ngo_admin = NGOUserProfile.objects.get(user=request.user)

    if request.method == 'GET':
        form = CreateProject(entity_list=entity_list, initial={'name': name})
        activity_report_questions = json.dumps(helper.get_activity_report_questions(manager), default=field_to_json)
        subject_report_questions = json.dumps(helper.get_subject_report_questions(manager), default=field_to_json)
        return render_to_response('project/create_project.html',
            {'form': form, "activity_report_questions": repr(activity_report_questions),
             'subject_report_questions': repr(subject_report_questions),
             'preview_links': get_preview_and_instruction_links(),
             'existing_questions': repr(activity_report_questions), 'project': project_summary,
             'questionnaire_code': helper.generate_questionnaire_code(manager), 'is_edit': 'false',
             'post_url': reverse(create_project)}, context_instance=RequestContext(request))

    if request.method == 'POST':
        project_info = json.loads(request.POST['profile_form'])
        form = CreateProject(entity_list, data=project_info)
        if form.is_valid():
            project = Project(name=form.cleaned_data['name'], goals=form.cleaned_data['goals'],
                project_type='survey', entity_type=form.cleaned_data['entity_type'],
                activity_report=form.cleaned_data['activity_report'],
                state=request.POST['project_state'], devices=[u'sms', u'web', u'smartPhone'],
                language=form.cleaned_data['language'])

            for profile in get_ngoprofiles_for_all_users_in_account(request.user.get_profile().org_id):
                project.data_senders.append(profile.reporter_id)

            try:
                questionnaire = create_questionnaire(post=request.POST, manager=manager,
                    entity_type=form.cleaned_data['entity_type'],
                    name=form.cleaned_data['name'], language=form.cleaned_data['language'])
            except (QuestionCodeAlreadyExistsException, QuestionAlreadyExistsException,
                    EntityQuestionAlreadyExistsException) as ex:
                return HttpResponse(
                    json.dumps({'success': False, 'error_message': _(ex.message), 'error_in_project_section': False}))

            try:
                project.qid = questionnaire.save()
            except DataObjectAlreadyExists:
                return HttpResponse(json.dumps(
                    {'success': False, 'error_message': "Questionnaire with this code already exists",
                     'error_in_project_section': False}))

            try:
                project.save(manager)
                UserActivityLog().log(request, action=CREATED_PROJECT, project=project.name, detail=project.name)
            except DataObjectAlreadyExists as ex:
                questionnaire.delete()
                message = _("%s with %s = %s already exists.") % (_(ex.data[2]), _(ex.data[0]), "'%s'" % project.name)
                return HttpResponse(
                    json.dumps({'success': False, 'error_message': message, 'error_in_project_section': True}))

            return HttpResponse(json.dumps({'success': True, 'project_id': project.id}))


def get_reporting_period_field(questionnaire):
    for question in questionnaire:
        if question.is_event_time_field:
            return question
    return None


def is_date_format_of_reporting_period_changed(old_questionnaire, questionnaire):
    old_reporting_period_question = get_reporting_period_field(old_questionnaire)
    new_reporting_period_question = get_reporting_period_field(questionnaire)
    if old_reporting_period_question and new_reporting_period_question:
        if old_reporting_period_question.date_format != new_reporting_period_question.date_format:
            return True
    return False


@login_required(login_url='/login')
@session_not_expired
@is_datasender
@csrf_exempt
@is_not_expired
@is_project_exist
def edit_project(request, project_id=None):
    manager = get_database_manager(request.user)
    entity_list = get_all_entity_types(manager)
    entity_list = helper.remove_reporter(entity_list)
    project = Project.load(manager.database, project_id)
    questionnaire = FormModel.get(manager, project.qid)
    if request.method == 'GET':
        form = CreateProject(data=project, entity_list=entity_list)
        activity_report_questions = json.dumps(helper.get_activity_report_questions(manager), default=field_to_json)
        subject_report_questions = json.dumps(helper.get_subject_report_questions(manager), default=field_to_json)
        fields = questionnaire.fields
        if questionnaire.entity_defaults_to_reporter():
            fields = helper.hide_entity_question(questionnaire.fields)
        existing_questions = json.dumps(fields, default=field_to_json)

        return render_to_response('project/create_project.html',
            {'form': form, "activity_report_questions": repr(activity_report_questions),
             'subject_report_questions': repr(subject_report_questions),
             'preview_links': get_preview_and_instruction_links(),
             'existing_questions': repr(existing_questions), 'questionnaire_code': questionnaire.form_code,
             'project': project, 'is_edit': 'true', 'post_url': reverse(edit_project, args=[project_id])},
            context_instance=RequestContext(request))

    if request.method == 'POST':
        project_info = json.loads(request.POST['profile_form'])
        form = CreateProject(entity_list, data=project_info)
        if form.is_valid():
            detail = dict()
            for key, changed in enumerate(form.changed_data):
                if getattr(project, changed) != form.cleaned_data.get(changed):
                    detail.update({changed.capitalize(): form.cleaned_data.get(changed)})
            project.update(form.cleaned_data)
            try:
                old_fields = questionnaire.fields
                questionnaire = update_questionnaire(questionnaire, request.POST, form.cleaned_data['entity_type'],
                    form.cleaned_data['name'], manager, form.cleaned_data['language'])
                changed_questions = get_changed_questions(old_fields, questionnaire.fields, subject=False)
                detail.update(changed_questions)
                project.state = request.POST['project_state']
                project.qid = questionnaire.save()
                UserActivityLog().log(request, project=project.name, action=EDITED_PROJECT, detail=json.dumps(detail))
            except (QuestionCodeAlreadyExistsException, QuestionAlreadyExistsException,
                    EntityQuestionAlreadyExistsException) as ex:
                return HttpResponse(
                    json.dumps({'success': False, 'error_in_project_section': False, 'error_message': _(ex.message)}))
            except DataObjectAlreadyExists:
                return HttpResponse(json.dumps({'success': False, 'error_in_project_section': False,
                                                'error_message': 'Questionnaire with this code already exists'}))

            try:
                project.save(manager)
            except DataObjectAlreadyExists as ex:
                message = _("%s with %s = %s already exists.") % (_(ex.data[2]), _(ex.data[0]), "'%s'" % project.name)
                return HttpResponse(
                    json.dumps({'success': False, 'error_message': message, 'error_in_project_section': True}))

            return HttpResponse(json.dumps({'success': True, 'project_id': project.id}))


@login_required(login_url='/login')
@session_not_expired
@is_datasender
@is_not_expired
def reminders(request, project_id):
    if request.method == 'GET':
        dbm = get_database_manager(request.user)
        project = Project.load(dbm.database, project_id)
        questionnaire = FormModel.get(dbm, project.qid)
        from datawinners.project.views import make_project_links

        project_links = make_project_links(project, questionnaire.form_code)
        reminders = Reminder.objects.filter(voided=False, project_id=project_id).order_by('id')
        organization = get_organization(request)
        from datawinners.project.views import  _format_reminders, create_reminder

        return render_to_response('project/reminders.html',
            {'project': project,
             'reminders': _format_reminders(reminders, project_id),
             'in_trial_mode': organization.in_trial_mode,
             'create_reminder_link': reverse(create_reminder, args=[project_id]),
             'project_links': project_links, 'is_quota_reached':is_quota_reached(request, organization=organization)},
            context_instance=RequestContext(request))


@login_required(login_url='/login')
@session_not_expired
@is_datasender
@is_not_expired
def reminder_settings(request, project_id):
    dbm = get_database_manager(request.user)
    project = Project.load(dbm.database, project_id)
    questionnaire = FormModel.get(dbm, project.qid)
    from datawinners.project.views.views import make_project_links

    project_links = make_project_links(project, questionnaire.form_code)
    org_id = (NGOUserProfile.objects.get(user=request.user)).org_id
    organization = Organization.objects.get(org_id=org_id)
    html = 'project/reminders_trial.html' if organization.in_trial_mode else 'project/reminder_settings.html'
    if request.method == 'GET':
        form = ReminderForm(data=(_reminder_info_about_project(project)))
        return render_to_response(html,
            {'project_links': project_links, 'is_quota_reached':is_quota_reached(request, organization=organization),
             'project': project,'form': form}, context_instance=RequestContext(request))

    if request.method == 'POST':
        form = ReminderForm(data=request.POST.copy())
        if form.is_valid():
            org_id = NGOUserProfile.objects.get(user=request.user).org_id
            organization = Organization.objects.get(org_id=org_id)
            reminder_list = Reminder.objects.filter(project_id=project.id)
            action = _get_activity_log_action(reminder_list, form.cleaned_data)
            project, set_deadline = _add_reminder_info_to_project(form.cleaned_data, project, organization,
                reminder_list=reminder_list)
            project.save(dbm)
            if action is not None:
                UserActivityLog().log(request, action=action, project=project.name)
            if set_deadline:
                UserActivityLog().log(request, action=SET_DEADLINE, project=project.name)
            messages.success(request, _("Reminder settings saved successfully."))
            return HttpResponseRedirect('')
        else:
            return render_to_response(html,
                {'project_links': project_links, 'is_quota_reached':is_quota_reached(request, organization=organization),
                 'project': project, 'form': form}, context_instance=RequestContext(request))


def _reminder_info_about_project(project):
    data = {}
    deadline_information = project.reminder_and_deadline
    data['has_deadline'] = deadline_information['has_deadline']
    if deadline_information['has_deadline']:
        data['frequency_period'] = deadline_information['frequency_period']
        if deadline_information['frequency_period'] == 'month':
            data['deadline_month'] = deadline_information['deadline_month']
        else:
            data['deadline_week'] = deadline_information['deadline_week']
        data['deadline_type'] = deadline_information['deadline_type']
        reminder_before_deadline = Reminder.objects.filter(reminder_mode=ReminderMode.BEFORE_DEADLINE,
            project_id=project.id)
        if  reminder_before_deadline.count() > 0:
            data['should_send_reminders_before_deadline'] = True
            data['number_of_days_before_deadline'] = reminder_before_deadline[0].day
            data['reminder_text_before_deadline'] = reminder_before_deadline[0].message
        else:
            data['should_send_reminders_before_deadline'] = False
            data['number_of_days_before_deadline'] = 2
            data['reminder_text_before_deadline'] = ugettext("Reports are due in 2 days. Please submit soon.")

        reminder_on_deadline = Reminder.objects.filter(reminder_mode=ReminderMode.ON_DEADLINE, project_id=project.id)
        if reminder_on_deadline.count() > 0:
            data['should_send_reminders_on_deadline'] = True
            data['reminder_text_on_deadline'] = reminder_on_deadline[0].message
        else:
            data['should_send_reminders_on_deadline'] = False
            data['reminder_text_on_deadline'] = ugettext("Reports are due today. Please submit soon.")

        reminder_after_deadline = Reminder.objects.filter(reminder_mode=ReminderMode.AFTER_DEADLINE,
            project_id=project.id)
        if reminder_after_deadline.count() > 0:
            data['should_send_reminders_after_deadline'] = True
            data['number_of_days_after_deadline'] = reminder_after_deadline[0].day
            data['reminder_text_after_deadline'] = reminder_after_deadline[0].message
        else:
            data['should_send_reminders_after_deadline'] = False
            data['number_of_days_after_deadline'] = 2
            data['reminder_text_after_deadline'] = ugettext("Reports are over due. Please submit immediately.")

    data['whom_to_send_message'] = not project.reminder_and_deadline['should_send_reminder_to_all_ds']

    return data


def _add_reminder_info_to_project(cleaned_data, project, organization, reminder_list=None):
    set_deadline = False
    if project['reminder_and_deadline']['has_deadline']:
        project['reminder_and_deadline']['frequency_period'] = cleaned_data['frequency_period']
        if cleaned_data['frequency_period'] == 'month':
            if project['reminder_and_deadline'].get('deadline_week'):
                del project['reminder_and_deadline']['deadline_week']
                set_deadline = True
            project['reminder_and_deadline']['deadline_month'] = cleaned_data['deadline_month']
        else:
            if project['reminder_and_deadline'].get('deadline_month'):
                del project['reminder_and_deadline']['deadline_month']
                set_deadline = True
            project['reminder_and_deadline']['deadline_week'] = cleaned_data['deadline_week']
        if project['reminder_and_deadline']['deadline_type'] != cleaned_data['deadline_type']:
            set_deadline = True
        project['reminder_and_deadline']['deadline_type'] = cleaned_data['deadline_type']

        if reminder_list is None:
            reminder_list = Reminder.objects.filter(project_id=project.id)
        reminder_list.delete()

        if cleaned_data['should_send_reminders_before_deadline']:
            Reminder(project_id=project.id, day=cleaned_data['number_of_days_before_deadline'],
                message=cleaned_data['reminder_text_before_deadline'],
                reminder_mode=ReminderMode.BEFORE_DEADLINE, organization=organization).save()

        if cleaned_data['should_send_reminders_on_deadline']:
            Reminder(project_id=project.id, day=0, message=cleaned_data['reminder_text_on_deadline'],
                reminder_mode=ReminderMode.ON_DEADLINE, organization=organization).save()

        if cleaned_data['should_send_reminders_after_deadline']:
            Reminder(project_id=project.id, day=cleaned_data['number_of_days_after_deadline'],
                message=cleaned_data['reminder_text_after_deadline'],
                reminder_mode=ReminderMode.AFTER_DEADLINE, organization=organization).save()

        project['reminder_and_deadline']['should_send_reminder_to_all_ds'] = not cleaned_data['whom_to_send_message']
    else:
        reminder_list = Reminder.objects.filter(project_id=project.id)
        reminder_list.delete()

    return project, set_deadline


def _get_activity_log_action(reminder_list, new_value):
    action = None
    if reminder_list.count() == 0 and (new_value['should_send_reminders_after_deadline'] or
                                       new_value['should_send_reminders_on_deadline'] or
                                       new_value['should_send_reminders_before_deadline']):
        action = ACTIVATED_REMINDERS
    if reminder_list.count() > 0 and not (new_value['should_send_reminders_after_deadline'] or
                                          new_value['should_send_reminders_on_deadline'] or
                                          new_value['should_send_reminders_before_deadline']):
        action = DEACTIVATED_REMINDERS
    return action
