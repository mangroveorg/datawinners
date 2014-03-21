import json

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.translation import ugettext
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.utils.translation import ugettext as _
from celery.task import current
from datastore.entity_type import get_unique_id_types

from datawinners import settings
from datawinners.project import helper
from mangrove.errors.MangroveException import DataObjectAlreadyExists, QuestionCodeAlreadyExistsException, EntityQuestionAlreadyExistsException, QuestionAlreadyExistsException
from mangrove.form_model.field import field_to_json
from mangrove.transport.repository.survey_responses import survey_responses_by_form_code
from mangrove.form_model.form_model import FormModel
from datawinners.accountmanagement.decorators import is_datasender, session_not_expired, is_not_expired
from datawinners.accountmanagement.models import Organization, NGOUserProfile
from datawinners.project.forms import ReminderForm
from datawinners.project.models import Project, Reminder, ReminderMode
from datawinners.main.database import get_database_manager, get_db_manager
from datawinners.questionnaire.library import QuestionnaireLibrary
from datawinners.tasks import app
from datawinners.activitylog.models import UserActivityLog
from datawinners.utils import get_changed_questions
from datawinners.common.constant import CREATED_PROJECT, EDITED_PROJECT, ACTIVATED_REMINDERS, DEACTIVATED_REMINDERS, SET_DEADLINE
from datawinners.questionnaire.questionnaire_builder import QuestionnaireBuilder
from datawinners.project.helper import is_project_exist
from datawinners.project.utils import is_quota_reached


def create_questionnaire(post, manager, name, language):
    questionnaire_code = post['questionnaire-code'].lower()
    json_string = post['question-set']
    question_set = json.loads(json_string)
    form_model = FormModel(manager, name=name, type='survey',
                          fields=[], form_code=questionnaire_code, language=language)
    QuestionnaireBuilder(form_model, manager).update_questionnaire_with_questions(question_set)
    return form_model


def update_questionnaire(questionnaire, post, name, manager, language):
    questionnaire.name = name
    questionnaire.activeLanguages = [language]
    questionnaire.form_code = post['questionnaire-code'].lower()
    json_string = post['question-set']
    question_set = json.loads(json_string)
    QuestionnaireBuilder(questionnaire, manager).update_questionnaire_with_questions(question_set)
    return questionnaire


def get_preview_and_instruction_links():
    links = {
        'sms_preview': reverse("sms_preview"),
        'web_preview': reverse("web_preview"),
        'smart_phone_preview': reverse("smart_phone_preview"),
    }
    return links


@login_required
@session_not_expired
@csrf_exempt
@is_not_expired
def get_templates(request):
    library = QuestionnaireLibrary()
    return HttpResponse(json.dumps({'categories': library.get_template_groupings(request.LANGUAGE_CODE)}),
                        content_type='application/json')

@login_required
def get_template_details(request, template_id):
    dbm = get_database_manager(request.user)
    library = QuestionnaireLibrary()
    template = library.get_questionnaire_template(template_id)
    template_details = {'template_id': template.id, 'project_name': template.get('name'),
                        'project_language': template.get('language'),
                        'questionnaire_code': template.get('form_code'),
                        'existing_questions': json.dumps(template.get('json_fields'), default=field_to_json)}
    return HttpResponse(json.dumps(template_details), content_type='application/json')


@login_required
@session_not_expired
@csrf_exempt
@is_not_expired
def create_project(request):
    manager = get_database_manager(request.user)
    ngo_admin = NGOUserProfile.objects.get(user=request.user)

    if request.method == 'GET':
        cancel_link = reverse('dashboard') if request.GET['prev'] == 'dash' else reverse('index')
        return render_to_response('project/create_project.html',
                                  {'preview_links': get_preview_and_instruction_links(),
                                   'questionnaire_code': helper.generate_questionnaire_code(manager),
                                   'is_edit': 'false',
                                   'post_url': reverse(create_project),
                                   'unique_id_types': get_unique_id_types(manager),
                                   'cancel_link': cancel_link}, context_instance=RequestContext(request))

    if request.method == 'POST':
        project_info = json.loads(request.POST['profile_form'])
        project = Project(name=project_info.get('name'), devices=[u'sms', u'web', u'smartPhone'],
                          language=project_info.get('language'))

        if ngo_admin.reporter_id is not None:
            project.data_senders.append(ngo_admin.reporter_id)

        try:
            questionnaire = create_questionnaire(post=request.POST, manager=manager, name=project_info.get('name'),
                                                 language=project_info.get('language'))
            if questionnaire.entity_type:
                project.entity_type = questionnaire.entity_type[0]
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


def _get_deleted_question_codes(new_codes, old_codes):
    diff = set(old_codes) - set(new_codes)
    return filter(diff.__contains__, old_codes)


def _get_changed_data(project, project_info):
    changed_dict = dict()
    for attr, value in project_info.iteritems():
        if getattr(project, attr) != value:
            changed_dict.update({attr.capitalize(): value})
    return changed_dict


@login_required
@session_not_expired
@is_datasender
@csrf_exempt
@is_not_expired
@is_project_exist
def edit_project(request, project_id):
    manager = get_database_manager(request.user)
    project = Project.load(manager.database, project_id)
    dashboard_page = settings.HOME_PAGE + "?deleted=true"
    if project.is_deleted():
        return HttpResponseRedirect(dashboard_page)
    questionnaire = FormModel.get(manager, project.qid)
    if request.method == 'GET':
        return render_to_response('project/create_project.html',
                                  {'preview_links': get_preview_and_instruction_links(),
                                   'questionnaire_code': questionnaire.form_code,
                                   'is_edit': 'true',
                                   'post_url': reverse(edit_project, args=[project_id])},
                                  context_instance=RequestContext(request))

    if request.method == 'POST':
        project_info = json.loads(request.POST['profile_form'])
        detail = _get_changed_data(project, project_info)
        is_project_name_changed = project_info.get('name') != questionnaire.name
        project.update(project_info)
        try:
            old_fields = questionnaire.fields
            old_form_code = questionnaire.form_code
            old_field_codes = questionnaire.field_codes()
            questionnaire = update_questionnaire(questionnaire, request.POST, project_info.get('name'), manager,
                                                 project_info.get('language'))
            changed_questions = get_changed_questions(old_fields, questionnaire.fields, subject=False)
            detail.update(changed_questions)
            project.qid = questionnaire.save()

            deleted_question_codes = _get_deleted_question_codes(old_codes=old_field_codes,
                                                                 new_codes=questionnaire.field_codes())

            update_associated_submissions.delay(manager.database_name, old_form_code,
                                                questionnaire.form_code,
                                                deleted_question_codes)
            UserActivityLog().log(request, project=project.name, action=EDITED_PROJECT, detail=json.dumps(detail))
        except (QuestionCodeAlreadyExistsException, QuestionAlreadyExistsException,
                EntityQuestionAlreadyExistsException) as ex:
            return HttpResponse(
                json.dumps({'success': False, 'error_in_project_section': False, 'error_message': _(ex.message)}))
        except DataObjectAlreadyExists:
            return HttpResponse(json.dumps({'success': False, 'error_in_project_section': False,
                                            'error_message': 'Questionnaire with this code already exists'}))

        try:

            project.save(manager, process_post_update=is_project_name_changed)
        except DataObjectAlreadyExists as ex:
            message = _("%s with %s = %s already exists.") % (_(ex.data[2]), _(ex.data[0]), "'%s'" % project.name)
            return HttpResponse(
                json.dumps({'success': False, 'error_message': message, 'error_in_project_section': True}))

        return HttpResponse(json.dumps({'success': True, 'project_id': project.id}))

@login_required
@session_not_expired
@is_datasender
@is_not_expired
def reminder_settings(request, project_id):
    dbm = get_database_manager(request.user)
    project = Project.load(dbm.database, project_id)
    dashboard_page = settings.HOME_PAGE + "?deleted=true"
    if project.is_deleted():
        return HttpResponseRedirect(dashboard_page)
    questionnaire = FormModel.get(dbm, project.qid)
    from datawinners.project.views.views import make_project_links

    project_links = make_project_links(project, questionnaire.form_code)
    org_id = (NGOUserProfile.objects.get(user=request.user)).org_id
    organization = Organization.objects.get(org_id=org_id)
    html = 'project/reminders_trial.html' if organization.in_trial_mode else 'project/reminder_settings.html'
    if request.method == 'GET':
        form = ReminderForm(data=(_reminder_info_about_project(project)))
        return render_to_response(html,
                                  {'project_links': project_links,
                                   'is_quota_reached': is_quota_reached(request, organization=organization),
                                   'project': project,
                                   'form': form,
                                   'questionnaire_code': questionnaire.form_code
                                  }, context_instance=RequestContext(request))

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
                                      {'project_links': project_links,
                                       'is_quota_reached': is_quota_reached(request, organization=organization),
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
        if reminder_before_deadline.count() > 0:
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


def update_submissions_for_form_code_change(manager, new_form_code, old_form_code):
    if old_form_code != new_form_code:
        survey_responses = survey_responses_by_form_code(manager, old_form_code)
        documents = []
        for survey_response in survey_responses:
            survey_response.form_code = new_form_code
            documents.append(survey_response._doc)
        manager._save_documents(documents)


def update_submissions_for_form_field_change(manager, old_form_code, deleted_question_codes):
    if deleted_question_codes:
        survey_responses = survey_responses_by_form_code(manager, old_form_code)
        for survey_response in survey_responses:
            for code in deleted_question_codes:
                survey_response._doc.values.pop(code, None)
            survey_response.save()


@app.task(max_retries=3, throw=False)
def update_associated_submissions(database_name, old_form_code, new_form_code, deleted_question_codes):
    try:
        manager = get_db_manager(database_name)
        update_submissions_for_form_code_change(manager, new_form_code, old_form_code)
        update_submissions_for_form_field_change(manager, old_form_code, deleted_question_codes)
    except Exception as e:
        current.retry(exc=e)
