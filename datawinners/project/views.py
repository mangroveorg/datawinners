# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from collections import namedtuple
import json
import datetime
import logging
from time import mktime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext_lazy as _, ugettext_lazy
from django.utils.translation import ugettext
from django.conf import settings
from django.utils import translation
from django.core.urlresolvers import reverse
from django.contrib import messages
from datawinners.entity.helper import process_create_datasender_form
from datawinners.entity import import_data as import_module

import helper

from mangrove.datastore.data import EntityAggregration
from mangrove.datastore.queries import get_entity_count_for_type
from mangrove.errors.MangroveException import QuestionCodeAlreadyExistsException, EntityQuestionAlreadyExistsException, DataObjectAlreadyExists, DataObjectNotFound
from mangrove.form_model import form_model
from mangrove.form_model.field import field_to_json
from mangrove.form_model.form_model import get_form_model_by_code, FormModel, REGISTRATION_FORM_CODE, get_form_model_by_entity_type, REPORTER
from mangrove.transport.player.player import WebPlayer
from mangrove.transport.submissions import Submission, get_submissions, submission_count
from mangrove.utils.dates import convert_to_epoch
from mangrove.datastore import aggregrate as aggregate_module
from mangrove.utils.json_codecs import encode_json
from mangrove.utils.types import is_empty, is_string
from mangrove.transport import Channel

import datawinners.utils as utils

from datawinners.accountmanagement.views import is_datasender, is_datasender_allowed, is_new_user, project_has_web_device
from datawinners.entity.import_data import load_all_subjects_of_type, get_entity_type_fields, get_entity_type_infos
from datawinners.location.LocationTree import get_location_tree
from datawinners.main.utils import get_database_manager, include_of_type
from datawinners.messageprovider.message_handler import get_exception_message_for
from datawinners.messageprovider.messages import exception_messages, WEB
from datawinners.project.forms import BroadcastMessageForm
from datawinners.project.models import Project, ProjectState, Reminder, ReminderMode, get_all_reminder_logs_for_project, get_all_projects
from datawinners.accountmanagement.models import Organization, OrganizationSetting, NGOUserProfile
from datawinners.entity.forms import ReporterRegistrationForm
from datawinners.entity.views import import_subjects_from_project_wizard, all_datasenders, save_questionnaire as subject_save_questionnaire
from datawinners.project.wizard_view import edit_project, reminder_settings, reminders
from datawinners.location.LocationTree import get_location_hierarchy
from datawinners.project import models
from datawinners.project.web_questionnaire_form_creator import WebQuestionnaireFormCreater, SubjectQuestionFieldCreator
from datawinners.questionnaire.questionnaire_builder import QuestionnaireBuilder

logger = logging.getLogger("django")

END_OF_DAY = " 23:59:59"
START_OF_DAY = " 00:00:00"

PAGE_SIZE = 10
NUMBER_TYPE_OPTIONS = ["Latest", "Sum", "Count", "Min", "Max", "Average"]
MULTI_CHOICE_TYPE_OPTIONS = ["Latest", "sum(yes)", "percent(yes)", "sum(no)", "percent(no)"]
DATE_TYPE_OPTIONS = ["Latest"]
GEO_TYPE_OPTIONS = ["Latest"]
TEXT_TYPE_OPTIONS = ["Latest", "Most Frequent"]

def make_project_links(project, questionnaire_code):
    project_id = project.id
    project_links = {'overview_link': reverse(project_overview, args=[project_id]),
                     'activate_project_link': reverse(activate_project, args=[project_id]),
                     'delete_project_link': reverse(delete_project, args=[project_id]),
                     'questionnaire_preview_link': reverse(questionnaire_preview, args=[project_id]),
                     'current_language': translation.get_language()
    }

    if project.state == ProjectState.TEST or project.state == ProjectState.ACTIVE:
        project_links['data_analysis_link'] = reverse(project_data, args=[project_id, questionnaire_code])
        project_links['submission_log_link'] = reverse(project_results, args=[project_id, questionnaire_code])
        project_links['finish_link'] = reverse(review_and_test, args=[project_id])
        project_links['reminders_link'] = reverse(reminder_settings, args=[project_id])

        project_links.update(make_subject_links(project))
        project_links.update(make_data_sender_links(project))

        project_links['sender_registration_preview_link'] = reverse(sender_registration_form_preview, args=[project_id])
        project_links['sent_reminders_link'] = reverse(sent_reminders, args=[project_id])
        project_links['setting_reminders_link'] = reverse(reminder_settings, args=[project_id])
        project_links['broadcast_message_link'] = reverse(broadcast_message, args=[project_id])
        if 'web' in project.devices:
            project_links['test_questionnaire_link'] = reverse(web_questionnaire, args=[project_id])
        else:
            project_links['test_questionnaire_link'] = ""
    if project.state == ProjectState.ACTIVE:
        project_links['questionnaire_link'] = reverse(questionnaire, args=[project_id])

    return project_links


def make_subject_links(project):
    project_id = project.id
    subject_links = {};
    subject_links['subjects_link'] = reverse(subjects, args=[project_id])
    subject_links['subjects_edit_link'] = reverse(edit_subject, args=[project_id])
    subject_links['register_subjects_link'] = reverse('subject_questionnaire', args=[project_id])
    subject_links['registered_subjects_link'] = reverse(registered_subjects, args=[project_id])
    subject_links['subject_registration_preview_link'] = reverse(subject_registration_form_preview,
        args=[project_id])
    return subject_links


def make_data_sender_links(project):
    project_id = project.id
    datasender_links = {};
    datasender_links['datasenders_link'] = reverse(all_datasenders)
    datasender_links['register_datasenders_link'] = reverse(create_datasender, args=[project_id])
    datasender_links['registered_datasenders_link'] = reverse(registered_datasenders, args=[project_id])
    return datasender_links


@login_required(login_url='/login')
def save_questionnaire(request):
    manager = get_database_manager(request.user)
    if request.method == 'POST':
        questionnaire_code = request.POST['questionnaire-code']
        json_string = request.POST['question-set']
        question_set = json.loads(json_string)
        pid = request.POST['pid']
        project = Project.load(manager.database, pid)
        form_model = FormModel.get(manager, project.qid)
        try:
            QuestionnaireBuilder(form_model, manager).update_questionnaire_with_questions(question_set)
        except QuestionCodeAlreadyExistsException as e:
            return HttpResponseServerError(e)
        except EntityQuestionAlreadyExistsException as e:
            return HttpResponseServerError(e.message)
        else:
            try:
                form_model.form_code = questionnaire_code.lower()
            except DataObjectAlreadyExists as e:
                if e.message.find("Form") >= 0:
                    return HttpResponseServerError("Questionnaire with this code already exists")
                return HttpResponseServerError(e.message)
            form_model.name = project.name
            form_model.entity_id = project.entity_type
            form_model.save()
            return HttpResponse(json.dumps({"response": "ok"}))


@login_required(login_url='/login')
@is_new_user
@is_datasender
def index(request):
    project_list = []
    rows = models.get_all_projects(dbm=get_database_manager(request.user))
    for row in rows:
        project_id = row['value']['_id']
        link = reverse(project_overview, args=[project_id])
        if row['value']['state'] == 'Inactive':
            link = reverse(edit_project, args=[project_id])
        activate_link = reverse(activate_project, args=[project_id])
        delete_link = reverse(delete_project, args=[project_id])
        project = dict(delete_link=delete_link, name=row['value']['name'], created=row['value']['created'],
            type=row['value']['project_type'],
            link=link, activate_link=activate_link, state=row['value']['state'])
        project_list.append(project)
    return render_to_response('project/index.html', {'projects': project_list},
        context_instance=RequestContext(request))


@login_required(login_url='/login')
@is_new_user
@is_datasender
def delete_project(request, project_id):
    manager = get_database_manager(request.user)
    project = Project.load(manager.database, project_id)
    helper.delete_project(manager, project)
    undelete_link = reverse(undelete_project, args=[project_id])
    if len(get_all_projects(manager)) > 0:
        messages.info(request, undelete_link)
    return HttpResponseRedirect(reverse(index))


def undelete_project(request, project_id):
    manager = get_database_manager(request.user)
    project = Project.load(manager.database, project_id)
    helper.delete_project(manager, project, False)
    return HttpResponseRedirect(reverse(index))


@login_required(login_url='/login')
@is_datasender
def project_overview(request, project_id=None):
    manager = get_database_manager(request.user)
    project = Project.load(manager.database, project_id)
    form_model = FormModel.get(manager, project.qid)
    questionnaire = FormModel.get(manager, project['qid'])
    number_of_questions = len(questionnaire.fields)
    project_links = make_project_links(project, questionnaire.form_code)
    map_api_key = settings.API_KEYS.get(request.META['HTTP_HOST'])
    number_data_sender = len(project.get_data_senders(manager))
    number_records = submission_count(manager, form_model.form_code, None, None)
    number_reminders = Reminder.objects.filter(project_id=project.id).count()
    links = {'registered_data_senders': reverse(registered_datasenders, args=[project_id])}
    add_data_senders_to_see_on_map_msg = _(
        "Register Data Senders to see them on this map") if number_data_sender == 0 else ""
    add_subjects_to_see_on_map_msg = _(
        "Register %s to see them on this map") % project.entity_type if get_entity_count_for_type(manager,
        project.entity_type) == 0 else ""
    in_trial_mode = _in_trial_mode(request)
    return render_to_response('project/overview.html', RequestContext(request, {
        'project': project,
        'entity_type': project['entity_type'],
        'project_links': project_links,
        'number_of_questions': number_of_questions,
        'map_api_key': map_api_key,
        'number_data_sender': number_data_sender,
        'number_records': number_records,
        'number_reminders': number_reminders,
        'links': links,
        'add_data_senders_to_see_on_map_msg': add_data_senders_to_see_on_map_msg,
        'add_subjects_to_see_on_map_msg': add_subjects_to_see_on_map_msg,
        'in_trial_mode': in_trial_mode
    }))


@login_required(login_url='/login')
@is_datasender
def project_results(request, project_id=None, questionnaire_code=None):
    manager = get_database_manager(request.user)
    project = Project.load(manager.database, project_id)
    project_links = make_project_links(project, questionnaire_code)
    questionnaire = get_form_model_by_code(manager, questionnaire_code)
    if request.method == 'GET':
        count, submissions, error_message = _get_submissions(manager, questionnaire_code, request)
        submission_display = helper.adapt_submissions_for_template(questionnaire.fields, submissions)
        in_trial_mode = _in_trial_mode(request)
        return render_to_response('project/results.html',
                {'questionnaire_code': questionnaire_code, 'questions': questionnaire.fields,
                 'submissions': submission_display, 'pages': count,
                 'error_message': error_message, 'project_links': project_links, 'project': project,
                 'in_trial_mode': in_trial_mode},
            context_instance=RequestContext(request)
        )
    if request.method == "POST":
        submission_ids = json.loads(request.POST.get('id_list'))
        for submission_id in submission_ids:
            submission = Submission.get(manager, submission_id)
            submission.void()
        count, submissions, error_message = _get_submissions(manager, questionnaire_code, request)
        submission_display = helper.adapt_submissions_for_template(questionnaire.fields, submissions)
        return render_to_response('project/log_table.html',
                {'questionnaire_code': questionnaire_code, 'questions': questionnaire.fields,
                 'submissions': submission_display, 'pages': count,
                 'success_message': _("The selected records have been deleted")},
            context_instance=RequestContext(request))


def _get_submissions(manager, questionnaire_code, request, paginate=True):
    request_bag = request.GET
    start_time = request_bag.get("start_time") or ""
    end_time = request_bag.get("end_time") or ""
    start_time_epoch = convert_to_epoch(helper.get_formatted_time_string(start_time.strip() + START_OF_DAY))
    end_time_epoch = convert_to_epoch(helper.get_formatted_time_string(end_time.strip() + END_OF_DAY))
    current_page = (int(request_bag.get('page_number') or 1) - 1) if paginate else 0
    page_size = PAGE_SIZE if paginate else None
    submissions = get_submissions(manager, questionnaire_code, start_time_epoch, end_time_epoch, current_page,
        page_size)
    count = submission_count(manager, questionnaire_code, start_time_epoch, end_time_epoch)
    error_message = ugettext("No submissions present for this project") if not count else None
    return count, submissions, error_message


@login_required(login_url='/login')
def submissions(request):
    """
            Called via ajax, returns the partial HTML for the submissions made for the project, paginated.
    """
    manager = get_database_manager(request.user)
    if request.method == 'GET':
        questionnaire_code = request.GET.get('questionnaire_code')
        questionnaire = get_form_model_by_code(manager, questionnaire_code)
        count, submissions, error_message = _get_submissions(manager, questionnaire_code, request)
        submission_display = helper.adapt_submissions_for_template(questionnaire.fields, submissions)
        return render_to_response('project/log_table.html',
                {'questionnaire_code': questionnaire_code, 'questions': questionnaire.fields,
                 'submissions': submission_display, 'pages': count,
                 'error_message': error_message,
                 'success_message': ""}, context_instance=RequestContext(request))


def _format_data_for_presentation(entity_values_dict, form_model):
    headers = helper.get_headers(form_model)
    type_list = helper.get_aggregation_options_for_all_fields(form_model.fields[1:])
    field_values, grand_totals = helper.get_all_values(entity_values_dict, headers, form_model.entity_question.name)
    return field_values, headers, type_list, grand_totals


def _load_data(form_model, manager, questionnaire_code, aggregation_types=None, start_time=None, end_time=None):
    if aggregation_types is not None:
        aggregation_type_list = json.loads(aggregation_types)
    else:
        aggregation_type_list = ['latest' for field in form_model.fields[1:]]
    start_time = helper.get_formatted_time_string(start_time.strip() + START_OF_DAY) if start_time is not None else None
    end_time = helper.get_formatted_time_string(end_time.strip() + END_OF_DAY) if end_time is not None else None
    aggregates = helper.get_aggregate_list(form_model.fields[1:], aggregation_type_list)
    aggregates = [aggregate_module.aggregation_factory("latest", form_model.fields[0].name)] + aggregates
    data_dictionary = aggregate_module.aggregate_by_form_code_python(manager, questionnaire_code,
        aggregates=aggregates,
        aggregate_on=EntityAggregration(),
        starttime=start_time,
        endtime=end_time, include_grand_totals=True)
    return data_dictionary


def _get_aggregated_data(form_model, manager, questionnaire_code, request):
    if request.method == "GET":
        aaggregation_types = request.GET.get("aggregation-types")
        start_time = request.GET.get("start_time")
        end_time = request.GET.get("end_time")
    else:
        aaggregation_types = request.POST.get("aggregation-types")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")

    entity_values_dict = _load_data(form_model, manager, questionnaire_code, aaggregation_types,
        start_time, end_time)
    return _format_data_for_presentation(entity_values_dict, form_model)


@login_required(login_url='/login')
@is_datasender
def project_data(request, project_id=None, questionnaire_code=None):
    manager = get_database_manager(request.user)
    project = Project.load(manager.database, project_id)
    form_model = get_form_model_by_code(manager, questionnaire_code)

    field_values, header_list, type_list, grand_totals = _get_aggregated_data(form_model, manager, questionnaire_code,
        request)

    if request.method == "GET":
        in_trial_mode = _in_trial_mode(request)
        return render_to_response('project/data_analysis.html',
                {"entity_type": form_model.entity_type[0], "data_list": repr(encode_json(field_values)),
                 "header_list": header_list, "type_list": type_list, 'grand_totals': grand_totals, 'project_links': (
                make_project_links(project, questionnaire_code)), 'project': project, 'in_trial_mode': in_trial_mode}
            ,
            context_instance=RequestContext(request))
    if request.method == "POST":
        return HttpResponse(encode_json({'data': field_values, 'footer': grand_totals}))


@login_required(login_url='/login')
@is_datasender
def export_data(request):
    questionnaire_code = request.POST.get("questionnaire_code")
    manager = get_database_manager(request.user)
    form_model = get_form_model_by_code(manager, questionnaire_code)
    data_dictionary = _load_data(form_model, manager, questionnaire_code, request.POST.get("aggregation-types"),
        request.POST.get("start_time"), request.POST.get("end_time"))
    raw_data_list, header_list, type_list, grand_totals = _format_data_for_presentation(data_dictionary, form_model)
    raw_data_list.insert(0, header_list)
    file_name = request.POST.get(u"project_name") + '_analysis'
    return _create_excel_response(raw_data_list, file_name)


def _create_excel_response(raw_data_list, file_name):
    response = HttpResponse(mimetype="application/vnd.ms-excel")
    response['Content-Disposition'] = 'attachment; filename="%s.xls"' % (file_name,)
    wb = utils.get_excel_sheet(raw_data_list, 'data_log')
    wb.save(response)
    return response


@login_required(login_url='/login')
@is_datasender
def export_log(request):
    questionnaire_code = request.GET.get("questionnaire_code")
    manager = get_database_manager(request.user)
    questionnaire = get_form_model_by_code(manager, questionnaire_code)
    count, submissions, error_message = _get_submissions(manager, questionnaire_code, request, paginate=False)

    header_list = [ugettext("To"), ugettext("From"), ugettext("Date Received"), ugettext("Submission status"),
                   ugettext("Deleted Record"), ugettext("Errors")]
    header_list.extend([field.code for field in questionnaire.fields])
    raw_data_list = [header_list]
    if count:
        raw_data_list.extend(
            [[submission.destination, submission.source, submission.created, ugettext(str(submission.status)),
              ugettext(str(submission.data_record.is_void() if submission.data_record is not None else True)),
              submission.errors] + [submission.values.get(q.code.lower()) for q in questionnaire.fields] for submission
             in submissions])

    file_name = request.GET.get(u"project_name") + '_log'
    return _create_excel_response(raw_data_list, file_name)


def _format_field_description_for_data_senders(reg_form_fields):
    for field in reg_form_fields:
        if field.code == 't':
            continue
        temp = field.label.get("en")
        temp = temp.replace("subject", "data sender")
        field.label.update(en=temp)


def _get_imports_subjects_post_url(project_id=None):
    import_url = reverse(import_subjects_from_project_wizard)
    return import_url if project_id is None else ("%s?project_id=%s" % (import_url, project_id))

#todo Leaving this commented for reference
#@login_required(login_url='/login')
#def reminders_wizard(request, project_id=None):
#    if request.method == 'GET':
#        dbm = get_database_manager(request.user)
#        project = Project.load(dbm.database, project_id)
#        previous_link = reverse(datasenders_wizard, args=[project_id])
#        profile = request.user.get_profile()
#        organization = Organization.objects.get(org_id=profile.org_id)
#        context = {"previous": previous_link,
#                 'project': project,
#                 'is_reminder': project.is_reminder_enabled(),
#                 'in_trial_mode': organization.in_trial_mode,
#        }
#        return render_to_response('project/reminders_wizard.html', context, context_instance=RequestContext(request))
#    if request.method == 'POST':
#        return HttpResponseRedirect(reverse(finish, args=[project_id]))

def _format_string_for_reminder_table(value):
    return (' '.join(value.split('_'))).title()


def _make_reminder_mode(reminder_mode, day):
    if reminder_mode == ReminderMode.ON_DEADLINE:
        return _format_string_for_reminder_table(reminder_mode)
    return str(day) + ' days ' + _format_string_for_reminder_table(reminder_mode)


def _format_reminder(reminder, project_id):
    return dict(message=reminder.message, id=reminder.id,
        to=_format_string_for_reminder_table(reminder.remind_to),
        when=_make_reminder_mode(reminder.reminder_mode, reminder.day),
        delete_link=reverse(delete_reminder, args=[project_id, reminder.id]))


def _format_reminders(reminders, project_id):
    return [_format_reminder(reminder, project_id) for reminder in reminders]


@login_required(login_url='/login')
@csrf_exempt
def create_reminder(request, project_id):
    if is_empty(request.POST['id']):
        Reminder(project_id=project_id, day=request.POST.get('day', 0), message=request.POST['message'],
            reminder_mode=request.POST['reminder_mode'], remind_to=request.POST['remind_to'],
            organization=utils.get_organization(request)).save()
        messages.success(request, 'Reminder added successfully')
    else:
        reminder = Reminder.objects.filter(project_id=project_id, id=request.POST['id'])[0]
        reminder.day = request.POST.get('day', 0)
        reminder.message = request.POST['message']
        reminder.reminder_mode = request.POST['reminder_mode']
        reminder.remind_to = request.POST['remind_to']
        reminder.save()
        messages.success(request, 'Reminder updated successfully')
    return HttpResponseRedirect(reverse(reminders, args=[project_id]))


@login_required(login_url='/login')
@csrf_exempt
def get_reminder(request, project_id):
    reminder_id = request.GET['id']
    reminder = Reminder.objects.filter(project_id=project_id, id=reminder_id)[0]
    return HttpResponse(json.dumps(reminder.to_dict()))


@login_required(login_url='/login')
@csrf_exempt
def delete_reminder(request, project_id, reminder_id):
    Reminder.objects.filter(project_id=project_id, id=reminder_id)[0].delete()
    messages.success(request, 'Reminder deleted')
    return HttpResponseRedirect(reverse(reminders, args=[project_id]))


@login_required(login_url='/login')
@csrf_exempt
def manage_reminders(request, project_id):
    if request.method == 'GET':
        reminders = Reminder.objects.filter(project_id=project_id, voided=False)
        return HttpResponse(json.dumps([reminder.to_dict() for reminder in reminders]))

    if request.method == 'POST':
        reminders = json.loads(request.POST['reminders'])
        Reminder.objects.filter(project_id=project_id).delete()
        for reminder in reminders:
            Reminder(project_id=project_id, day=reminder['day'], message=reminder['message'],
                reminder_mode=reminder['reminderMode'], organization=utils.get_organization(request),
                remind_to=reminder['targetDataSenders']).save()
        return HttpResponse("Reminders has been saved")


@login_required(login_url='/login')
@is_datasender
def sent_reminders(request, project_id):
    dbm = get_database_manager(request.user)
    project = Project.load(dbm.database, project_id)
    questionnaire = FormModel.get(dbm, project.qid)
    organization = Organization.objects.get(org_id=request.user.get_profile().org_id)
    is_trial_account = organization.in_trial_mode
    html = 'project/reminders_trial.html' if organization.in_trial_mode else 'project/sent_reminders.html'
    return render_to_response(html,
            {'project': project, "project_links": make_project_links(project, questionnaire.form_code),
             'reminders': get_all_reminder_logs_for_project(project_id, dbm),
             'in_trial_mode': is_trial_account,
             'create_reminder_link': reverse(create_reminder, args=[project_id])},
        context_instance=RequestContext(request))


def _get_data_senders(dbm, form, project):
    data_senders = []
    if form.cleaned_data['to'] == "All":
        data_senders = _get_all_data_senders(dbm)
    elif form.cleaned_data['to'] == "Associated":
        data_senders = project.get_data_senders(dbm)
    return data_senders


@login_required(login_url='/login')
@is_datasender
def broadcast_message(request, project_id):
    dbm = get_database_manager(request.user)
    project = Project.load(dbm.database, project_id)
    questionnaire = FormModel.get(dbm, project.qid)
    organization = utils.get_organization(request)
    if request.method == 'GET':
        form = BroadcastMessageForm()
        html = 'project/broadcast_message_trial.html' if organization.in_trial_mode else 'project/broadcast_message.html'
        return render_to_response(html, {'project': project,
                                         "project_links": make_project_links(project, questionnaire.form_code),
                                         "form": form},
            context_instance=RequestContext(request))
    if request.method == 'POST':
        form = BroadcastMessageForm(request.POST)
        if form.is_valid():
            data_senders = _get_data_senders(dbm, form, project)
            organization_setting = OrganizationSetting.objects.get(organization=organization)
            current_month = datetime.date(datetime.datetime.now().year, datetime.datetime.now().month, 1)
            message_tracker = organization._get_message_tracker(current_month)
            other_numbers = form.cleaned_data['others']
            helper.broadcast_message(data_senders, form.cleaned_data['text'],
                organization_setting.get_organisation_sms_number(), other_numbers, message_tracker)
            form = BroadcastMessageForm()
            return render_to_response('project/broadcast_message.html',
                    {'project': project,
                     "project_links": make_project_links(project, questionnaire.form_code), "form": form,
                     'success': True},
                context_instance=RequestContext(request))

        return render_to_response('project/broadcast_message.html',
                {'project': project,
                 "project_links": make_project_links(project, questionnaire.form_code), "form": form,
                 'success': False},
            context_instance=RequestContext(request))


def _get_all_data_senders(dbm):
    data_senders, fields, labels = load_all_subjects_of_type(dbm)
    return [dict(zip(fields, data["cols"])) for data in data_senders]


@login_required(login_url='/login')
@is_datasender
def activate_project(request, project_id=None):
    manager = get_database_manager(request.user)
    project = Project.load(manager.database, project_id)
    project.activate(manager)
    form_model = FormModel.get(manager, project.qid)
    oneDay = datetime.timedelta(days=1)
    tomorrow = datetime.datetime.now() + oneDay
    submissions = get_submissions(manager, form_model.form_code, from_time=0,
        to_time=int(mktime(tomorrow.timetuple())) * 1000, page_size=None)
    for submission in submissions:
        submission.void()
    return HttpResponseRedirect(reverse(project_overview, args=[project_id]))


@login_required(login_url='/login')
def review_and_test(request, project_id=None):
    manager = get_database_manager(request.user)
    project = Project.load(manager.database, project_id)
    form_model = FormModel.get(manager, project.qid)
    if request.method == 'GET':
        number_of_registered_subjects = get_entity_count_for_type(manager, project.entity_type)
        number_of_registered_datasenders = get_entity_count_for_type(manager, 'reporter')
        fields = form_model.fields
        if form_model.entity_defaults_to_reporter():
            fields = helper.hide_entity_question(form_model.fields)
        is_reminder = "enabled" if project['reminder_and_deadline']['has_deadline'] else "disabled"
        devices = ",".join(project.devices)
        in_trial_mode = _in_trial_mode(request)
        return render_to_response('project/review_and_test.html', {'project': project, 'fields': fields,
                                                                   'project_links': make_project_links(project,
                                                                       form_model.form_code),
                                                                   'number_of_datasenders': number_of_registered_datasenders
            ,
                                                                   'number_of_subjects': number_of_registered_subjects,
                                                                   "is_reminder": is_reminder,
                                                                   "in_trial_mode": in_trial_mode,
                                                                   "devices": devices},
            context_instance=RequestContext(request))


def _get_project_and_project_link(manager, project_id):
    project = Project.load(manager.database, project_id)
    questionnaire = FormModel.get(manager, project.qid)
    project_links = make_project_links(project, questionnaire.form_code)
    return project, project_links


@login_required(login_url='/login')
def subjects(request, project_id=None):
    manager = get_database_manager(request.user)
    project, project_links = _get_project_and_project_link(manager, project_id)
    fields, project_links_with_subject_questionare, questions, reg_form = _get_registration_form(manager, project,
        type_of_subject='subject')
    example_sms = get_example_sms_message(fields, reg_form)
    subject = get_entity_type_infos(project.entity_type, manager=manager)
    return render_to_response('project/subjects.html',
            {'project': project,
             'project_links': project_links,
             'questions': questions,
             'questionnaire_code': reg_form.form_code,
             'example_sms': example_sms,
             'org_number': _get_organization_telephone_number(request),
             'current_language': translation.get_language(),
             'subject': subject},
        context_instance=RequestContext(request))


@login_required(login_url='/login')
def registered_subjects(request, project_id=None):
    manager = get_database_manager(request.user)
    project, project_links = _get_project_and_project_link(manager, project_id)
    all_data, fields, labels = load_all_subjects_of_type(manager, filter_entities=include_of_type,
        type=project.entity_type)
    subject = get_entity_type_infos(project.entity_type, manager=manager)
    in_trial_mode = _in_trial_mode(request)
    return render_to_response('project/registered_subjects.html',
            {'project': project, 'project_links': project_links, 'all_data': all_data, "labels": labels,
             "subject": subject, 'in_trial_mode': in_trial_mode},
        context_instance=RequestContext(request))


@login_required(login_url='/login')
@csrf_exempt
def registered_datasenders(request, project_id=None):
    manager = get_database_manager(request.user)
    project, project_links = _get_project_and_project_link(manager, project_id)
    if request.method == 'GET':
        fields, old_labels, codes = get_entity_type_fields(manager)
        labels = []
        for label in old_labels:
            if label != "What is the mobile number associated with the subject?":
                labels.append(_(label.replace('subject', 'Data Sender')))
            else:
                labels.append(_("What is the Data Sender's mobile number?"))
        in_trial_mode = _in_trial_mode(request)
        return render_to_response('project/registered_datasenders.html',
                {'project': project, 'project_links': project_links, 'all_data': (
                helper.get_project_data_senders(manager, project)), "labels": labels,
                 'current_language': translation.get_language(), 'in_trial_mode': in_trial_mode},
            context_instance=RequestContext(request))
    if request.method == 'POST':
        error_message, failure_imports, success_message, imported_entities = import_module.import_data(request, manager)
        all_data_senders, fields, labels = import_module.load_all_subjects_of_type(manager)
        project.data_senders.extend([id for id in imported_entities.keys()])
        project.save(manager)
        return HttpResponse(json.dumps(
                {'success': error_message is None and is_empty(failure_imports), 'message': success_message,
                 'error_message': error_message,
                 'failure_imports': failure_imports, 'all_data_senders': all_data_senders,
                 'imported_entities': imported_entities,
                 'associated_datasenders': project.data_senders}))


@login_required(login_url='/login')
@csrf_exempt
def disassociate_datasenders(request):
    manager = get_database_manager(request.user)
    project = Project.load(manager.database, request.POST['project_id'])
    [project.data_senders.remove(id) for id in request.POST['ids'].split(';') if id in project.data_senders]
    project.save(manager)
    return HttpResponse(reverse(registered_datasenders, args=(project.id,)))


def _get_questions_for_datasenders_registration_for_print_preview(questions):
    cleaned_qestions = _get_questions_for_datasenders_registration_for_wizard(questions)
    cleaned_qestions.insert(0, questions[0])
    return cleaned_qestions


def _get_questions_for_datasenders_registration_for_wizard(questions):
    return [questions[1], questions[2], questions[3], questions[4], questions[5]]


@login_required(login_url='/login')
@is_datasender
def datasenders(request, project_id=None):
    manager = get_database_manager(request.user)
    project, project_links = _get_project_and_project_link(manager, project_id)
    fields, project_links, questions, reg_form = _get_registration_form(manager, project)
    questions = _get_questions_for_datasenders_registration_for_print_preview(questions)
    example_sms = get_example_sms_message(questions, reg_form)
    return render_to_response('project/datasenders.html',
            {'project': project,
             'project_links': project_links,
             'questions': questions,
             'questionnaire_code': reg_form.form_code,
             'example_sms': example_sms,
             'org_number': _get_organization_telephone_number(request),
             'current_language': translation.get_language()},
        context_instance=RequestContext(request))


@login_required(login_url='/login')
def questionnaire(request, project_id=None):
    manager = get_database_manager(request.user)
    if request.method == 'GET':
        project = Project.load(manager.database, project_id)
        form_model = FormModel.get(manager, project.qid)
        fields = form_model.fields
        if form_model.entity_defaults_to_reporter():
            fields = helper.hide_entity_question(form_model.fields)
        existing_questions = json.dumps(fields, default=field_to_json)
        project_links = make_project_links(project, form_model.form_code)
        in_trial_mode = _in_trial_mode(request)
        return render_to_response('project/questionnaire.html',
                {"existing_questions": repr(existing_questions), 'questionnaire_code': form_model.form_code,
                 'project': project, 'project_links': project_links, 'in_trial_mode': in_trial_mode},
            context_instance=RequestContext(request))


def _make_project_context(form_model, project):
    return {'form_model': form_model, 'project': project,
            'project_links': make_project_links(project,
                form_model.form_code)}


def _create_submission_request(form_model, request):
    submission_request = dict(request.POST)
    submission_request["form_code"] = form_model.form_code
    return submission_request


def _make_form_context(questionnaire_form, project, form_code, disable_link_class):
    return {'questionnaire_form': questionnaire_form, 'project': project,
            'project_links': make_project_links(project, form_code),
            'disable_link_class': disable_link_class,
            }


def _get_response(template, form_code, project, questionnaire_form, request, disable_link_class):
    form_context = _make_form_context(questionnaire_form, project, form_code, disable_link_class)
    subject = get_entity_type_infos(project.entity_type, manager=get_database_manager(request.user))
    form_context.update({'subject': subject, 'add_link': add_link(project)})
    return render_to_response(template, form_context,
        context_instance=RequestContext(request))


@login_required(login_url='/login')
@is_datasender_allowed
@project_has_web_device
def web_questionnaire(request, project_id=None, subject=False):
    manager = get_database_manager(request.user)
    project = Project.load(manager.database, project_id)
    if subject:
        template = 'project/register_subject.html'
        form_model = _get_subject_form_model(manager, project.entity_type)
    else:
        template = 'project/web_questionnaire.html'
        form_model = FormModel.get(manager, project.qid)
    QuestionnaireForm = WebQuestionnaireFormCreater(SubjectQuestionFieldCreator(manager, project),
        form_model=form_model).create()
    disable_link_class = "disable_link" if request.user.get_profile().reporter else ""
    if request.method == 'GET':
        questionnaire_form = QuestionnaireForm()
        return _get_response(template, form_model.form_code, project, questionnaire_form, request, disable_link_class)

    if request.method == 'POST':
        questionnaire_form = QuestionnaireForm(country=utils.get_organization_country(request), data=request.POST)
        if not questionnaire_form.is_valid():
            return _get_response(template, form_model.form_code, project, questionnaire_form, request,
                disable_link_class)

        success_message = None
        error_message = None
        try:
            response = WebPlayer(manager, get_location_tree(), get_location_hierarchy).accept(
                helper.create_request(questionnaire_form, request.user.username))
            if response.success:
                if subject:
                    success_message = (_("Successfully submitted. Unique identification number(ID) is:") + " %s") % (
                        response.short_code,)
                else:
                    success_message = _("Successfully submitted")
                questionnaire_form = QuestionnaireForm()
            else:
                questionnaire_form._errors = helper.errors_to_list(response.errors, form_model.fields)
                return _get_response(template, form_model.form_code, project, questionnaire_form, request,
                    disable_link_class)

        except DataObjectNotFound as exception:
            message = exception_messages.get(DataObjectNotFound).get(WEB)
            error_message = _(message) % (form_model.entity_type[0], form_model.entity_type[0])
        except Exception as exception:
            logger.exception('Web Submission failure:-')
            error_message = _(get_exception_message_for(exception=exception, channel=Channel.WEB))

        subject = get_entity_type_infos(project.entity_type, manager=get_database_manager(request.user))
        _project_context = _make_form_context(questionnaire_form, project, form_model.form_code, disable_link_class)
        _project_context.update(
                {'success_message': success_message, 'error_message': error_message, 'add_link': add_link(project), "subject": subject})
        return render_to_response(template, _project_context,
            context_instance=RequestContext(request))


def get_example_sms(fields):
    example_sms = ""
    for field in fields:
        example_sms = example_sms + " " + unicode(_('answer')) + str(fields.index(field) + 1)
    return example_sms


@login_required(login_url='/login')
def questionnaire_preview(request, project_id=None):
    manager = get_database_manager(request.user)
    if request.method == 'GET':
        project = Project.load(manager.database, project_id)
        form_model = FormModel.get(manager, project.qid)
        fields = form_model.fields
        if form_model.entity_defaults_to_reporter():
            fields = helper.hide_entity_question(form_model.fields)
        project_links = make_project_links(project, form_model.form_code)
        questions = []
        for field in fields:
            question = helper.get_preview_for_field(field)
            questions.append(question)
        example_sms = "%s" % (
            form_model.form_code)
        example_sms += get_example_sms(fields)
        return render_to_response('project/questionnaire_preview.html',
                {"questions": questions, 'questionnaire_code': form_model.form_code,
                 'project': project, 'project_links': project_links,
                 'example_sms': example_sms, 'org_number': _get_organization_telephone_number(request)},
            context_instance=RequestContext(request))


def _get_preview_for_field_in_registration_questionnaire(field, language):
    return {"description": field.label.get(language), "code": field.code, "type": field.type,
            "constraints": field.get_constraint_text(), "instruction": field.instruction}


def _get_registration_form(manager, project, type_of_subject='reporter'):
    if type_of_subject == 'reporter':
        registration_questionnaire = form_model.get_form_model_by_code(manager, REGISTRATION_FORM_CODE)
    else:
        entity_type = [project.entity_type]
        registration_questionnaire = get_form_model_by_entity_type(manager, entity_type)
        if registration_questionnaire is None:
            registration_questionnaire = form_model.get_form_model_by_code(manager, REGISTRATION_FORM_CODE)
    fields = registration_questionnaire.fields
    project_links = make_project_links(project, registration_questionnaire.form_code)
    questions = []
    for field in fields:
        question = _get_preview_for_field_in_registration_questionnaire(field,
            registration_questionnaire.activeLanguages[0])
        questions.append(question)
    return fields, project_links, questions, registration_questionnaire


def get_example_sms_message(fields, registration_questionnaire):
    example_sms = "%s %s" % (registration_questionnaire.form_code, get_example_sms(fields))
    return example_sms


@login_required(login_url='/login')
def subject_registration_form_preview(request, project_id=None):
    manager = get_database_manager(request.user)
    project = Project.load(manager.database, project_id)
    if request.method == "GET":
        fields, project_links, questions, registration_questionnaire = _get_registration_form(manager,
            project, project.entity_type)
        example_sms = get_example_sms_message(fields, registration_questionnaire)
        return render_to_response('project/questionnaire_preview.html',
                {"questions": questions, 'questionnaire_code': registration_questionnaire.form_code,
                 'project': project, 'project_links': project_links,
                 'example_sms': example_sms, 'org_number': _get_organization_telephone_number(request)},
            context_instance=RequestContext(request))


@login_required(login_url='/login')
def sender_registration_form_preview(request, project_id=None):
    manager = get_database_manager(request.user)
    project = Project.load(manager.database, project_id)
    if request.method == "GET":
        fields, project_links, questions, registration_questionnaire = _get_registration_form(manager,
            project,
            type_of_subject='reporter')
        datasender_questions = _get_questions_for_datasenders_registration_for_print_preview(questions)
        example_sms = get_example_sms_message(datasender_questions, registration_questionnaire)
        return render_to_response('project/questionnaire_preview.html',
                {"questions": datasender_questions, 'questionnaire_code': registration_questionnaire.form_code,
                 'project': project, 'project_links': project_links,
                 'example_sms': example_sms, 'org_number': _get_organization_telephone_number(request)},
            context_instance=RequestContext(request))


def _get_organization_telephone_number(request):
    organization_settings = utils.get_organization_settings_from_request(request)
    return organization_settings.get_organisation_sms_number()


def _get_subject_form_model(manager, entity_type):
    if is_string(entity_type):
        entity_type = [entity_type]
    return get_form_model_by_entity_type(manager, entity_type)


@login_required(login_url='/login')
def edit_subject(request, project_id=None):
    manager = get_database_manager(request.user)
    project, project_links = _get_project_and_project_link(manager, project_id)

    reg_form = _get_subject_form_model(manager, project.entity_type)
    if reg_form is None:
        reg_form = form_model.get_form_model_by_code(manager, REGISTRATION_FORM_CODE)
    fields = reg_form.fields
    existing_questions = json.dumps(fields, default=field_to_json)
    subject = get_entity_type_infos(project.entity_type, manager=manager)
    return render_to_response('project/subject_questionnaire.html',
            {'project': project,
             'project_links': project_links,
             'existing_questions': repr(existing_questions),
             'questionnaire_code': reg_form.form_code,
             'language': reg_form.activeLanguages[0],
             'entity_type': project.entity_type,
             'subject': subject,
             'post_url': reverse(subject_save_questionnaire)},
        context_instance=RequestContext(request))


@login_required(login_url='/login')
@is_datasender_allowed
@project_has_web_device
def create_datasender(request, project_id=None):
    manager = get_database_manager(request.user)
    project, project_links = _get_project_and_project_link(manager, project_id)
    in_trial_mode = _in_trial_mode(request)

    if request.method == 'GET':
        form = ReporterRegistrationForm(initial={'project_id': project_id})
        return render_to_response('project/register_datasender.html', {
            'project': project, 'project_links': project_links, 'form': form,
            'in_trial_mode': in_trial_mode},
            context_instance=RequestContext(request))

    if request.method == 'POST':
        form = ReporterRegistrationForm(request.POST)
        org_id = request.user.get_profile().org_id
        message = process_create_datasender_form(manager, form, org_id, Project)
        if message is not None:
            form = ReporterRegistrationForm(initial={'project_id': form.cleaned_data['project_id']})
        return render_to_response('datasender_form.html',
                {'form': form, 'message': message, 'in_trial_mode': in_trial_mode},
            context_instance=RequestContext(request))


def _in_trial_mode(request):
    return utils.get_organization(request).in_trial_mode


def add_link(project):
    add_link_named_tuple = namedtuple("Add_Link", ['url', 'text'])
    if project.entity_type == REPORTER:
        text = _("Add a datasender")
        url = make_data_sender_links(project)['register_datasenders_link']
        return add_link_named_tuple(url=url, text=text)
    else:
        text = _("Register a %s") % (project.entity_type)
        url = make_subject_links(project)['register_subjects_link']
        return add_link_named_tuple(url=url, text=text)
