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

from mangrove.datastore.entity_type import get_unique_id_types
from datawinners import settings
from datawinners.project import helper
from mangrove.errors.MangroveException import DataObjectAlreadyExists, QuestionCodeAlreadyExistsException, \
    EntityQuestionAlreadyExistsException, QuestionAlreadyExistsException
from mangrove.form_model.field import field_to_json
from mangrove.transport.repository.survey_responses import survey_responses_by_form_code
from datawinners.accountmanagement.decorators import is_datasender, session_not_expired, is_not_expired
from datawinners.accountmanagement.models import Organization, NGOUserProfile
from datawinners.project.forms import ReminderForm
from datawinners.project.models import Project, Reminder, ReminderMode
from datawinners.main.database import get_database_manager, get_db_manager
from datawinners.questionnaire.library import QuestionnaireLibrary
from datawinners.tasks import app
from datawinners.activitylog.models import UserActivityLog
from datawinners.utils import get_changed_questions
from datawinners.common.constant import CREATED_PROJECT, EDITED_PROJECT, ACTIVATED_REMINDERS, DEACTIVATED_REMINDERS, \
    SET_DEADLINE
from datawinners.questionnaire.questionnaire_builder import QuestionnaireBuilder
from datawinners.project.helper import is_project_exist
from datawinners.project.utils import is_quota_reached


def create_questionnaire(post, manager, name, language, reporter_id, question_set_json=None,
                         xform=None):
    questionnaire_code = post['questionnaire-code'].lower()
    datasenders = json.loads(post.get('datasenders', "[]"))
    question_set = question_set_json if question_set_json else json.loads(post['question-set'])
    questionnaire = Project(manager, name=name,
                           fields=[], form_code=questionnaire_code, language=language,
                           devices=[u'sms', u'web', u'smartPhone'])
    if not xform:
        questionnaire.xform = xform

    if reporter_id is not None:
        questionnaire.data_senders.append(reporter_id)

    if datasenders:
        questionnaire.data_senders.extend(filter(lambda ds: ds != reporter_id, datasenders))

    QuestionnaireBuilder(questionnaire, manager)\
        .update_questionnaire_with_questions(question_set)\
        .update_reminder(json.loads(post.get('reminder_and_deadline', '{}')))

    return questionnaire


def update_questionnaire(questionnaire, post, manager, language):
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
    active_language = request.LANGUAGE_CODE
    if request.method == 'GET':
        cancel_link = reverse('dashboard') if request.GET.get('prev', None) == 'dash' else reverse('index')
        return render_to_response('project/create_project.html',
                                  {'preview_links': get_preview_and_instruction_links(),
                                   'questionnaire_code': helper.generate_questionnaire_code(manager),
                                   'is_edit': 'false',
                                   'active_language':active_language,
                                   'post_url': reverse(create_project),
                                   'unique_id_types': [unique_id_type.capitalize() for unique_id_type in
                                                       get_unique_id_types(manager)],
                                   'cancel_link': cancel_link}, context_instance=RequestContext(request))

    if request.method == 'POST':
        project_info = json.loads(request.POST['profile_form'])

        try:
            questionnaire = create_questionnaire(post=request.POST, manager=manager, name=project_info.get('name'),
                                                 language=project_info.get('language'),
                                                 reporter_id=ngo_admin.reporter_id)
        except (QuestionCodeAlreadyExistsException, QuestionAlreadyExistsException,
                EntityQuestionAlreadyExistsException) as ex:
            return HttpResponse(
                json.dumps({'success': False, 'error_message': _(ex.message), 'error_in_project_section': False}))

        code_has_errors, name_has_errors = False, False
        error_message = {}
        if not questionnaire.is_form_code_unique():
            code_has_errors = True
            error_message["code"] = _("Questionnaire with same code already exists.")
        if not questionnaire.is_project_name_unique():
            name_has_errors = True
            error_message["name"] = _("Questionnaire with same name already exists.")
        if not code_has_errors and not name_has_errors:
            questionnaire.update_doc_and_save()
            UserActivityLog().log(request, action=CREATED_PROJECT, project=questionnaire.name,
                                  detail=questionnaire.name)
            return HttpResponse(json.dumps({'success': True, 'project_id': questionnaire.id}))

        return HttpResponse(json.dumps(
            {'success': False, 'error_message': error_message,
             'error_in_project_section': False, 'code_has_errors': code_has_errors,
             'name_has_errors': name_has_errors}))

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
    dashboard_page = settings.HOME_PAGE + "?deleted=true"
    questionnaire = Project.get(manager, project_id)
    if questionnaire.is_void():
        return HttpResponseRedirect(dashboard_page)
    if request.method == 'GET':
        return render_to_response('project/create_project.html',
                                  {'preview_links': get_preview_and_instruction_links(),
                                   'questionnaire_code': questionnaire.form_code,
                                   'is_edit': 'true',
                                   'post_url': reverse(edit_project, args=[project_id])},
                                  context_instance=RequestContext(request))

    if request.method == 'POST':
        project_info = json.loads(request.POST['profile_form'])
        detail = _get_changed_data(questionnaire , project_info)
        if detail.get("Name"):
            detail.pop("Name")
        try:
            old_fields = questionnaire.fields
            old_form_code = questionnaire.form_code
            old_field_codes = questionnaire.field_codes()
            questionnaire = update_questionnaire(questionnaire, request.POST, manager,
                                                 project_info.get('language'))
            changed_questions = get_changed_questions(old_fields, questionnaire.fields, subject=False)
            detail.update(changed_questions)
            questionnaire.save()

            deleted_question_codes = _get_deleted_question_codes(old_codes=old_field_codes,
                                                                 new_codes=questionnaire.field_codes())

            update_associated_submissions.delay(manager.database_name, old_form_code,
                                                questionnaire.form_code,
                                                deleted_question_codes)
            UserActivityLog().log(request, project=questionnaire.name, action=EDITED_PROJECT, detail=json.dumps(detail))
        except (QuestionCodeAlreadyExistsException, QuestionAlreadyExistsException,
                EntityQuestionAlreadyExistsException) as ex:
            return HttpResponse(
                json.dumps({'success': False, 'error_in_project_section': False, 'error_message': _(ex.message)}))
        except DataObjectAlreadyExists:
            return HttpResponse(json.dumps({'success': False, 'error_in_project_section': False, "code_has_error":True,
                                            'error_message': ugettext('Questionnaire with same code already exists.')}))
        if request.POST['has_callback'] == 'false':
            messages.add_message(request,messages.INFO,"success")
        return HttpResponse(json.dumps({'success': True, 'project_id': project_id}))


@login_required
@session_not_expired
@is_datasender
@is_not_expired
def reminder_settings(request, project_id):
    dbm = get_database_manager(request.user)
    questionnaire = Project.get(dbm, project_id)
    dashboard_page = settings.HOME_PAGE + "?deleted=true"
    if questionnaire.is_void():
        return HttpResponseRedirect(dashboard_page)
    from datawinners.project.views.views import make_project_links

    project_links = make_project_links(questionnaire)
    org_id = (NGOUserProfile.objects.get(user=request.user)).org_id
    organization = Organization.objects.get(org_id=org_id)
    html = 'project/reminders_trial.html' if organization.in_trial_mode else 'project/reminder_settings.html'
    if request.method == 'GET':
        form = ReminderForm(data=(_reminder_info_about_project(questionnaire)))
        return render_to_response(html,
                                  {'project_links': project_links,
                                   'is_quota_reached': is_quota_reached(request, organization=organization),
                                   'project': questionnaire,
                                   'form': form,
                                   'questionnaire_code': questionnaire.form_code
                                  }, context_instance=RequestContext(request))

    if request.method == 'POST':
        form = ReminderForm(data=request.POST.copy())
        if form.is_valid():
            org_id = NGOUserProfile.objects.get(user=request.user).org_id
            organization = Organization.objects.get(org_id=org_id)
            reminder_list = Reminder.objects.filter(project_id=questionnaire.id)
            action = _get_activity_log_action(reminder_list, form.cleaned_data)
            questionnaire, set_deadline = _add_reminder_info_to_project(form.cleaned_data, questionnaire, organization,
                                                                  reminder_list=reminder_list)
            questionnaire.save()
            if action is not None:
                UserActivityLog().log(request, action=action, project=questionnaire.name)
            if set_deadline:
                UserActivityLog().log(request, action=SET_DEADLINE, project=questionnaire.name)
            messages.success(request, _("Reminder settings saved successfully."))
            return HttpResponseRedirect('')
        else:
            return render_to_response(html,
                                      {'project_links': project_links,
                                       'is_quota_reached': is_quota_reached(request, organization=organization),
                                       'project': questionnaire, 'form': form}, context_instance=RequestContext(request))


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
    if project.reminder_and_deadline.get('has_deadline'):
        project.reminder_and_deadline['frequency_period'] = cleaned_data['frequency_period']
        if cleaned_data['frequency_period'] == 'month':
            if project.reminder_and_deadline.get('deadline_week'):
                del project['reminder_and_deadline']['deadline_week']
                set_deadline = True
            project.reminder_and_deadline['deadline_month'] = cleaned_data['deadline_month']
        else:
            if project.reminder_and_deadline.get('deadline_month'):
                del project.reminder_and_deadline['deadline_month']
                set_deadline = True
            project.reminder_and_deadline['deadline_week'] = cleaned_data['deadline_week']
        if project.reminder_and_deadline.get('deadline_type') != cleaned_data['deadline_type']:
            set_deadline = True
        project.reminder_and_deadline['deadline_type'] = cleaned_data['deadline_type']

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

        project.reminder_and_deadline['should_send_reminder_to_all_ds'] = not cleaned_data['whom_to_send_message']
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


def remove_deleted_questions_from_submissions(manager, old_form_code, deleted_question_codes):
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
        remove_deleted_questions_from_submissions(manager, new_form_code, deleted_question_codes)
    except Exception as e:
        current.retry(exc=e)
