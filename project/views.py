# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import json
import datetime
from time import mktime
from django.contrib.auth.decorators import login_required
from django.forms.forms import Form
from django import forms
from django.forms.widgets import HiddenInput
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_exempt
from datawinners.accountmanagement.views import is_datasender, is_datasender_allowed, is_new_user, project_has_web_device
from datawinners.entity.import_data import load_all_subjects_of_type
from datawinners.location.LocationTree import get_location_tree
from datawinners.main.utils import get_database_manager, include_of_type
from datawinners.messageprovider.message_handler import get_exception_message_for
from datawinners.messageprovider.messages import exception_messages, WEB
from datawinners.project.forms import ProjectProfile
from datawinners.project.models import Project, ProjectState, Reminder, ReminderMode, get_all_reminder_logs_for_project, get_all_projects
from datawinners.accountmanagement.models import Organization, OrganizationSetting
from datawinners.entity.forms import ReporterRegistrationForm, SubjectForm
from datawinners.entity.forms import SubjectUploadForm
from datawinners.entity.views import import_subjects_from_project_wizard
import helper
from datawinners.project import models
from mangrove.datastore.data import EntityAggregration
from mangrove.datastore.queries import get_entity_count_for_type
from mangrove.datastore.entity_type import get_all_entity_types
from mangrove.errors.MangroveException import QuestionCodeAlreadyExistsException, EntityQuestionAlreadyExistsException, DataObjectAlreadyExists, DataObjectNotFound
from mangrove.form_model import form_model
from mangrove.form_model.field import field_to_json, SelectField, TextField, IntegerField, GeoCodeField, DateField
from mangrove.form_model.form_model import get_form_model_by_code, FormModel, REGISTRATION_FORM_CODE
from mangrove.transport.player import player
from mangrove.transport.player.player import WebPlayer, Request, TransportInfo
from mangrove.transport.submissions import Submission, get_submissions, submission_count
from django.contrib import messages
from mangrove.utils.dates import convert_to_epoch
from mangrove.datastore import aggregrate as aggregate_module
from mangrove.utils.json_codecs import encode_json
from django.core.urlresolvers import reverse
import datawinners.utils as utils
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.conf import settings

import logging
from mangrove.utils.types import is_empty


logger = logging.getLogger("django")

END_OF_DAY = " 23:59:59"
START_OF_DAY = " 00:00:00"

PAGE_SIZE = 10
NUMBER_TYPE_OPTIONS = ["Latest", "Sum", "Count", "Min", "Max", "Average"]
MULTI_CHOICE_TYPE_OPTIONS = ["Latest", "sum(yes)", "percent(yes)", "sum(no)", "percent(no)"]
DATE_TYPE_OPTIONS = ["Latest"]
GEO_TYPE_OPTIONS = ["Latest"]
TEXT_TYPE_OPTIONS = ["Latest", "Most Frequent"]

def _make_project_links(project, questionnaire_code):
    project_id = project.id
    project_links = {'overview_link': reverse(project_overview, args=[project_id]),
                     'activate_project_link': reverse(activate_project, args=[project_id]),
                     'questionnaire_preview_link': reverse(questionnaire_preview, args=[project_id])}

    if project.state == ProjectState.TEST or project.state == ProjectState.ACTIVE:
        project_links['data_analysis_link'] = reverse(project_data, args=[project_id, questionnaire_code])
        project_links['submission_log_link'] = reverse(project_results, args=[project_id, questionnaire_code])

    if project.state == ProjectState.ACTIVE:
        project_links['questionnaire_link'] = reverse(questionnaire, args=[project_id])
        if 'web' in project.devices:
            project_links['test_questionnaire_link'] = reverse(web_questionnaire, args=[project_id])
        else:
            project_links['test_questionnaire_link'] = ""

        project_links['subjects_link'] = reverse(subjects, args=[project_id])
        project_links['registered_subjects_link'] = reverse(registered_subjects, args=[project_id])

        project_links['datasenders_link'] = reverse(datasenders, args=[project_id])
        project_links['registered_datasenders_link'] = reverse(registered_datasenders, args=[project_id])
        project_links['subject_registration_preview_link'] = reverse(subject_registration_form_preview,
                                                                     args=[project_id])
        project_links['sender_registration_preview_link'] = reverse(sender_registration_form_preview, args=[project_id])
        project_links['reminders_link'] = reverse(reminders, args=[project_id])
        project_links['sent_reminders_link'] = reverse(sent_reminders, args=[project_id])
        project_links['broadcast_message_link'] = reverse(broadcast_message, args=[project_id])
    return project_links


@login_required(login_url='/login')
def questionnaire_wizard(request, project_id=None):
    manager = get_database_manager(request.user)
    if request.method == 'GET':
        previous_link = reverse(subjects_wizard, args=[project_id])
        project = Project.load(manager.database, project_id)
        form_model = FormModel.get(manager, project.qid)
        fields = form_model.fields
        if form_model.entity_defaults_to_reporter():
            fields = helper.hide_entity_question(form_model.fields)
        existing_questions = json.dumps(fields, default=field_to_json)
        return render_to_response('project/questionnaire_wizard.html',
                {"existing_questions": repr(existing_questions), 'questionnaire_code': form_model.form_code,
                 "previous": previous_link, 'project': project, "use_ordered_sms_parser" : settings.USE_ORDERED_SMS_PARSER}, context_instance=RequestContext(request))


@login_required(login_url='/login')
def create_profile(request):
    manager = get_database_manager(request.user)
    entity_list = get_all_entity_types(manager)
    entity_list = helper.remove_reporter(entity_list)
    project_summary = dict(name='New Project')
    is_trial_account = Organization.objects.get(org_id=request.user.get_profile().org_id).in_trial_mode
    if request.method == 'GET':
        form = ProjectProfile(entity_list=entity_list, initial={'activity_report': 'yes'})
        return render_to_response('project/profile.html', {'form': form, 'project': project_summary, 'edit': False, 'is_trial_account': is_trial_account
        },
                                  context_instance=RequestContext(request))

    form = ProjectProfile(data=request.POST, entity_list=entity_list)
    if form.is_valid():
        entity_type = form.cleaned_data['entity_type']
        project = Project(name=form.cleaned_data["name"], goals=form.cleaned_data["goals"],
                          project_type=form.cleaned_data['project_type'], entity_type=entity_type,
                          devices=form.cleaned_data['devices'], activity_report=form.cleaned_data['activity_report'],
                          sender_group=form.cleaned_data['sender_group'],
                          reminder_and_deadline=helper.deadline_and_reminder(form.cleaned_data),
                          language=form.cleaned_data['language'])
        form_model = helper.create_questionnaire(post=form.cleaned_data, dbm=manager)
        try:
            pid = project.save(manager)
            qid = form_model.save()
            project.qid = qid
            pid = project.save(manager)
        except DataObjectAlreadyExists as e:
            messages.error(request, e.message)
            return render_to_response('project/profile.html', {'form': form, 'project': project_summary, 'edit': False, 'is_trial_account': is_trial_account },
                                      context_instance=RequestContext(request))
        return HttpResponseRedirect(reverse(subjects_wizard, args=[pid]))
    else:
        return render_to_response('project/profile.html', {'form': form, 'project': project_summary, 'edit': False, 'is_trial_account': is_trial_account},
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
def edit_profile(request, project_id=None):
    manager = get_database_manager(request.user)
    entity_list = get_all_entity_types(manager)
    entity_list = helper.remove_reporter(entity_list)
    project = Project.load(manager.database, project_id)
    is_trial_account = Organization.objects.get(org_id=request.user.get_profile().org_id).in_trial_mode
    if request.method == 'GET':
        form = ProjectProfile(data=(_generate_project_info_with_deadline_and_reminders(project)), entity_list=entity_list)
        return render_to_response('project/profile.html', {'form': form, 'project': project, 'edit': True, 'is_trial_account':is_trial_account},
                                  context_instance=RequestContext(request))

    form = ProjectProfile(data=request.POST, entity_list=entity_list)
    if form.is_valid():
        older_entity_type = project.entity_type
        if older_entity_type != form.cleaned_data["entity_type"]:
            new_questionnaire = helper.create_questionnaire(form.cleaned_data, manager)
            new_qid = new_questionnaire.save()
            project.qid = new_qid
        project.reminder_and_deadline=helper.deadline_and_reminder(form.cleaned_data)
        project.update(form.cleaned_data)
        project.update_questionnaire(manager)

        try:
            pid = project.save(manager)
        except DataObjectAlreadyExists as e:
            messages.error(request, e.message)
            return render_to_response('project/profile.html', {'form': form, 'project': project, 'edit': True},
                                      context_instance=RequestContext(request))
        return HttpResponseRedirect(reverse(subjects_wizard, args=[pid]))
    else:
        return render_to_response('project/profile.html', {'form': form, 'project': project, 'edit': True},
                                  context_instance=RequestContext(request))


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
            form_model = helper.update_questionnaire_with_questions(form_model, question_set, manager)
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
        activate_link = reverse(activate_project, args=[project_id])
        delete_link = reverse(delete_project, args=[project_id])
        project = dict(delete_link=delete_link,name=row['value']['name'], created=row['value']['created'], type=row['value']['project_type'],
                       link=link, activate_link=activate_link, state=row['value']['state'])
        project["created"] = project["created"].strftime("%d %B, %Y")
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
def project_overview(request, project_id=None):
    manager = get_database_manager(request.user)
    project = Project.load(manager.database, project_id)
    link = reverse(edit_profile, args=[project_id])
    questionnaire = FormModel.get(manager, project['qid'])
    number_of_questions = len(questionnaire.fields)
    project_links = _make_project_links(project, questionnaire.form_code)
    map_api_key = settings.API_KEYS.get(request.META['HTTP_HOST'])
    return render_to_response('project/overview.html',
            {'project': project, 'entity_type': project['entity_type'], 'project_links': project_links
             , 'project_profile_link': link, 'number_of_questions': number_of_questions, 'map_api_key': map_api_key},
                              context_instance=RequestContext(request))


@login_required(login_url='/login')
@is_datasender
def project_results(request, project_id=None, questionnaire_code=None):
    manager = get_database_manager(request.user)
    project = Project.load(manager.database, project_id)
    project_links = _make_project_links(project, questionnaire_code)
    questionnaire = get_form_model_by_code(manager, questionnaire_code)
    if request.method == 'GET':
        count, submissions, error_message = _get_submissions(manager, questionnaire_code, request)
        submission_display = helper.adapt_submissions_for_template(questionnaire.fields, submissions)
        return render_to_response('project/results.html',
                {'questionnaire_code': questionnaire_code, 'questions': questionnaire.fields, 'submissions': submission_display, 'pages': count,
                 'error_message': error_message, 'project_links': project_links, 'project': project},
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
                {'questionnaire_code': questionnaire_code, 'questions': questionnaire.fields, 'submissions': submission_display, 'pages': count,
                 'success_message': _("The selected records have been deleted")}, context_instance=RequestContext(request))

def _get_submissions(manager, questionnaire_code, request, paginate=True):
    request_bag = request.GET
    start_time = request_bag.get("start_time") or ""
    end_time = request_bag.get("end_time") or ""
    start_time_epoch = convert_to_epoch(helper.get_formatted_time_string(start_time.strip() + START_OF_DAY))
    end_time_epoch = convert_to_epoch(helper.get_formatted_time_string(end_time.strip() + END_OF_DAY))
    current_page = (int(request_bag.get('page_number') or 1) - 1) if paginate else 0
    page_size = PAGE_SIZE if paginate else None
    submissions = get_submissions(manager, questionnaire_code, start_time_epoch, end_time_epoch, current_page, page_size)
    count = submission_count(manager, questionnaire_code, start_time_epoch, end_time_epoch)
    error_message = "No submissions present for this project" if not count else None
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
                {'questionnaire_code': questionnaire_code, 'questions': questionnaire.fields, 'submissions': submission_display, 'pages': count,
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
        return render_to_response('project/data_analysis.html',
                {"entity_type": form_model.entity_type[0], "data_list": repr(encode_json(field_values)),
                 "header_list": header_list, "type_list": type_list, 'grand_totals': grand_totals, 'project_links': (
                _make_project_links(project, questionnaire_code)), 'project': project}
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
    response = HttpResponse(mimetype="application/ms-excel")
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

    header_list = [ugettext("To"), ugettext("From"), ugettext("Date Received"), ugettext("Submission status"), ugettext("Deleted Record"), ugettext("Errors")]
    header_list.extend([field.code for field in questionnaire.fields])
    raw_data_list = [header_list]
    if count:
        raw_data_list.extend([[submission.destination, submission.source, submission.created, ugettext(str(submission.status)),
                                   ugettext(str(submission.data_record.is_void() if submission.data_record is not None else True)), submission.errors] + [submission.values.get(q.code.lower()) for q in questionnaire.fields] for submission in submissions])

    file_name = request.GET.get(u"project_name") + '_log'
    return _create_excel_response(raw_data_list, file_name)


@login_required(login_url='/login')
@is_datasender
def subjects_wizard(request, project_id=None):
    if request.method == 'GET':
        manager = get_database_manager(request.user)
        reg_form = get_form_model_by_code(manager, REGISTRATION_FORM_CODE)
        previous_link = reverse(edit_profile, args=[project_id])
        entity_types = get_all_entity_types(manager)
        project = Project.load(manager.database, project_id)
        helper.remove_reporter(entity_types)
        import_subject_form = SubjectUploadForm()
        create_subject_form = SubjectForm()
        return render_to_response('project/subjects_wizard.html',
                {'fields': reg_form.fields, "previous": previous_link, "entity_types": entity_types,
                 'import_subject_form': import_subject_form,
                 'form': create_subject_form,
                 'post_url': reverse(import_subjects_from_project_wizard), 'project': project, 'step': 'subjects'},
                                  context_instance=RequestContext(request))

    if request.method == 'POST':
        return HttpResponseRedirect(reverse(questionnaire_wizard, args=[project_id]))


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


@login_required(login_url='/login')
@is_datasender
def datasenders_wizard(request, project_id=None):
    if request.method == 'GET':
        manager = get_database_manager(request.user)
        reg_form = get_form_model_by_code(manager, REGISTRATION_FORM_CODE)
        previous_link = reverse(questionnaire_wizard, args=[project_id])
        project = Project.load(manager.database, project_id)
        import_reporter_form = ReporterRegistrationForm(initial={'project_id': project_id})
        _format_field_description_for_data_senders(reg_form.fields)
        cleaned_up_fields = _get_questions_for_datasenders_registration_for_wizard(reg_form.fields)
        return render_to_response('project/datasenders_wizard.html',
                {'fields': cleaned_up_fields, "previous": previous_link,
                 'form': import_reporter_form,
                 'post_url': _get_imports_subjects_post_url(project_id), 'project': project, 'step': 'datasenders'},
                                  context_instance=RequestContext(request))

    if request.method == 'POST':
        return HttpResponseRedirect(reverse(reminders_wizard, args=[project_id]))


@login_required(login_url='/login')
def reminders_wizard(request, project_id=None):
    if request.method == 'GET':
        dbm = get_database_manager(request.user)
        project = Project.load(dbm.database, project_id)
        previous_link = reverse(datasenders_wizard, args=[project_id])
        return render_to_response('project/reminders_wizard.html',
                {"previous": previous_link, 'project': project, 'is_reminder': project.is_reminder_enabled()},
                                  context_instance=RequestContext(request))
    if request.method == 'POST':
        return HttpResponseRedirect(reverse(finish, args=[project_id]))

def _format_string_for_reminder_table(value):
    return (' '.join(value.split('_'))).title()


def _make_reminder_mode(reminder_mode, day):
    if reminder_mode == ReminderMode.ON_DEADLINE:
        return _format_string_for_reminder_table(reminder_mode)
    return str(day) + ' days ' + _format_string_for_reminder_table(reminder_mode)


def _format_reminder(reminder, project_id):
    return dict(message=reminder.message, id=reminder.id,
                to = _format_string_for_reminder_table(reminder.remind_to),
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
                     reminder_mode=reminder['reminderMode'], organization=utils.get_organization(request), remind_to=reminder['targetDataSenders']).save()
        return HttpResponse("Reminders has been saved")

@login_required(login_url='/login')
@is_datasender
def sent_reminders(request, project_id):
    dbm = get_database_manager(request.user)
    project = Project.load(dbm.database, project_id)
    questionnaire = FormModel.get(dbm, project.qid)
    return render_to_response('project/sent_reminders.html',
                {'project': project, "project_links": _make_project_links(project, questionnaire.form_code),
                 'reminders':get_all_reminder_logs_for_project(project_id, dbm),
                 'create_reminder_link' : reverse(create_reminder, args=[project_id])},
                                  context_instance=RequestContext(request))

@login_required(login_url='/login')
@is_datasender
def broadcast_message(request, project_id):
    dbm = get_database_manager(request.user)
    project = Project.load(dbm.database, project_id)
    questionnaire = FormModel.get(dbm, project.qid)
    return render_to_response('project/broadcast_message.html',
                {'project': project, "project_links": _make_project_links(project, questionnaire.form_code)},
                                  context_instance=RequestContext(request))

@login_required(login_url='/login')
@is_datasender
def reminders(request, project_id):
    if request.method == 'GET':
        dbm = get_database_manager(request.user)
        project = Project.load(dbm.database, project_id)
        questionnaire = FormModel.get(dbm, project.qid)
        reminders = Reminder.objects.filter(voided=False, project_id=project_id).order_by('id')
        return render_to_response('project/reminders.html',
                {'project': project, "project_links": _make_project_links(project, questionnaire.form_code),
                 'reminders':_format_reminders(reminders, project_id),
                 'create_reminder_link' : reverse(create_reminder, args=[project_id])},
                                  context_instance=RequestContext(request))

@login_required(login_url='/login')
@is_datasender
def activate_project(request, project_id=None):
    manager = get_database_manager(request.user)
    project = Project.load(manager.database, project_id)
    project.activate(manager)
    form_model = FormModel.get(manager, project.qid)
    oneDay = datetime.timedelta(days=1)
    tomorrow = datetime.datetime.now() + oneDay
    submissions = get_submissions(manager, form_model.form_code, from_time = 0, to_time=int(mktime(tomorrow.timetuple())) * 1000, page_size=None)
    for submission in submissions:
        submission.void()
    return HttpResponseRedirect(reverse(project_overview, args=[project_id]))


def _make_links_for_finish_page(project_id, form_model):
    project_links = {'edit_link': reverse(edit_profile, args=[project_id]),
                     'subject_link': reverse(subjects_wizard, args=[project_id]),
                     'questionnaire_link': reverse(questionnaire_wizard, args=[project_id]),
                     'data_senders_link': reverse(datasenders_wizard, args=[project_id]),
                     'log_link': reverse(project_results, args=[project_id, form_model.form_code]),
                     'questionnaire_preview_link': reverse(questionnaire_preview, args=[project_id]),
                     'subject_registration_preview_link': reverse(subject_registration_form_preview, args=[project_id]),
                     'sender_registration_preview_link': reverse(sender_registration_form_preview, args=[project_id]),
                     'reminder_link': reverse(reminders_wizard, args=[project_id])
    }
    return project_links


@login_required(login_url='/login')
def finish(request, project_id=None):
    manager = get_database_manager(request.user)
    project = Project.load(manager.database, project_id)
    form_model = FormModel.get(manager, project.qid)
    if request.method == 'GET':
        project.to_test_mode(manager)
        number_of_registered_subjects = get_entity_count_for_type(manager, project.entity_type)
        number_of_registered_datasenders = get_entity_count_for_type(manager, 'reporter')
        previous_link = reverse(reminders_wizard, args=[project_id])
        fields = form_model.fields
        if form_model.entity_defaults_to_reporter():
            fields = helper.hide_entity_question(form_model.fields)
        is_reminder = "enabled" if project.reminder_and_deadline['reminders_enabled'] == 'True' else "disabled"
        devices = ",".join(project.devices)
        return render_to_response('project/finish_and_test.html', {'project': project, 'fields': fields,
                                                                   'project_links': _make_links_for_finish_page(
                                                                       project_id, form_model),
                                                                   'number_of_datasenders': number_of_registered_datasenders
                                                                   ,
                                                                   'number_of_subjects': number_of_registered_subjects,
                                                                   "previous": previous_link,
                                                                   "is_reminder": is_reminder,
                                                                   "devices": devices},
                                  context_instance=RequestContext(request))
    if request.method == 'POST':
        return HttpResponseRedirect(reverse(project_overview, args=[project_id]))


def _get_project_and_project_link(manager, project_id):
    project = Project.load(manager.database, project_id)
    questionnaire = FormModel.get(manager, project.qid)
    project_links = _make_project_links(project, questionnaire.form_code)
    return project, project_links


@login_required(login_url='/login')
def subjects(request, project_id=None):
    manager = get_database_manager(request.user)
    project, project_links = _get_project_and_project_link(manager, project_id)
    reg_form = get_form_model_by_code(manager, REGISTRATION_FORM_CODE)
    return render_to_response('project/subjects.html',
            {'fields': reg_form.fields, 'project': project, 'project_links': project_links},
                              context_instance=RequestContext(request))


@login_required(login_url='/login')
def registered_subjects(request, project_id=None):
    manager = get_database_manager(request.user)
    project, project_links = _get_project_and_project_link(manager, project_id)
    all_data = load_all_subjects_of_type(manager, filter_entities=include_of_type, type=project.entity_type)
    return render_to_response('project/registered_subjects.html',
            {'project': project, 'project_links': project_links, 'all_data': all_data},
                              context_instance=RequestContext(request))




@login_required(login_url='/login')
def registered_datasenders(request, project_id=None):
    manager = get_database_manager(request.user)
    project, project_links = _get_project_and_project_link(manager, project_id)
    return render_to_response('project/registered_datasenders.html',
            {'project': project, 'project_links': project_links, 'all_data': (
            helper.get_project_data_senders(manager, project))},
                              context_instance=RequestContext(request))


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
    return [questions[1], questions[3], questions[4], questions[6]]


@login_required(login_url='/login')
@is_datasender
def datasenders(request, project_id=None):
    manager = get_database_manager(request.user)
    project, project_links = _get_project_and_project_link(manager, project_id)
    reg_form = get_form_model_by_code(manager, REGISTRATION_FORM_CODE)
    _format_field_description_for_data_senders(reg_form.fields)
    cleaned_up_fields = _get_questions_for_datasenders_registration_for_print_preview(reg_form.fields)
    return render_to_response('project/datasenders.html',
            {'fields': cleaned_up_fields, 'project': project, 'project_links': project_links},
                              context_instance=RequestContext(request))


@login_required(login_url='/login')
def questionnaire(request, project_id=None):
    manager = get_database_manager(request.user)
    if request.method == 'GET':
        previous_link = reverse(subjects_wizard, args=[project_id])
        project = Project.load(manager.database, project_id)
        form_model = FormModel.get(manager, project.qid)
        fields = form_model.fields
        if form_model.entity_defaults_to_reporter():
            fields = helper.hide_entity_question(form_model.fields)
        existing_questions = json.dumps(fields, default=field_to_json)
        project_links = _make_project_links(project, form_model.form_code)
        return render_to_response('project/questionnaire.html',
                {"existing_questions": repr(existing_questions), 'questionnaire_code': form_model.form_code,
                 "previous": previous_link, 'project': project, 'project_links': project_links},
                                  context_instance=RequestContext(request))


def _make_project_context(form_model, project):
    return {'form_model': form_model, 'project': project,
            'project_links': _make_project_links(project,
                                                 form_model.form_code)}


def _create_submission_request(form_model, request):
    submission_request = dict(request.POST)
    submission_request["form_code"] = form_model.form_code
    return submission_request


def _make_form_context(questionnaire_form, project, form_code, disable_link_class):
    return {'questionnaire_form': questionnaire_form, 'project': project,
            'project_links': _make_project_links(project, form_code),
            'disable_link_class': disable_link_class}


def _create_select_field(field, choices):
    if field.single_select_flag:
        return forms.ChoiceField(choices=choices, required=field.is_required(), label=field.name, initial=field.value, help_text=field.instruction)
    return forms.MultipleChoiceField(label=field.name, widget=forms.CheckboxSelectMultiple, choices=choices,
                                  initial=field.value, required=field.is_required(), help_text=field.instruction)


def _create_choices(field):
    choice_list = [('', '--None--')] if field.single_select_flag else []
    choice_list.extend([(option['val'], option['text']['en']) for option in field.options])
    choices = tuple(choice_list)
    return choices


def _get_django_field(field):
    if isinstance(field, SelectField):
        return  _create_select_field(field, _create_choices(field))
    display_field = forms.CharField(label=field.name, initial=field.value, required=field.is_required(), help_text=field.instruction)
    display_field.widget.attrs["watermark"] = field.get_constraint_text()
    display_field.widget.attrs['style'] = 'padding-top: 7px;'
    #    display_field.widget.attrs["watermark"] = "18 - 1"
    return display_field


def _create_django_form_from_form_model(form_model):
    properties = {field.code: _get_django_field(field) for field in form_model.fields}
    properties.update({'form_code': forms.CharField(widget=HiddenInput, initial=form_model.form_code)})
    return type('QuestionnaireForm', (Form, ), properties)


def _to_list(errors, fields):
    error_dict = dict()
    for key, value in errors.items():
        error_dict.update({key: [value] if not isinstance(value, list) else value})
    return translate_messages(error_dict, fields)

def translate_messages(error_dict, fields):
    errors = dict()

    for field in fields:
        if field.code in error_dict:
            error = error_dict[field.code][0]
            if type(field) == TextField:
                text, code = error.split(' ')[1], field.code
                errors[code] = [_("Answer %s for question %s is longer than allowed.") % (text, code)]
            if type(field) == IntegerField:
                number, error_context = error.split(' ')[1], error.split(' ')[6]
                errors[field.code] = [_("Answer %s for question %s is %s than allowed.") % (number, field.code, _(error_context),)]
            if type(field) == GeoCodeField:
                errors[field.code] = [_("Incorrect GPS format. The GPS coordinates must be in the following format: xx.xxxx yy.yyyy. Example -18.8665 47.5315")]
            if type(field) == DateField:
                answer, format = error.split(' ')[1], field.date_format
                errors[field.code] = [_("Answer %s for question %s is invalid. Expected date in %s format") % (answer, field.code, format)]
            
    return errors


def _create_request(questionnaire_form, username):
    return Request(message=questionnaire_form.cleaned_data,
                   transportInfo=
                   TransportInfo(transport="web",
                                 source=username,
                                 destination=""
                   ))


def _get_response(form_code, project, questionnaire_form, request, disable_link_class):
    return render_to_response('project/web_questionnaire.html',
                              _make_form_context(questionnaire_form, project, form_code, disable_link_class),
                              context_instance=RequestContext(request))


@login_required(login_url='/login')
@is_datasender_allowed
@project_has_web_device
def web_questionnaire(request, project_id=None):
    manager = get_database_manager(request.user)
    project = Project.load(manager.database, project_id)
    form_model = FormModel.get(manager, project.qid)

    QuestionnaireForm = _create_django_form_from_form_model(form_model)
    disable_link_class = "disable_link" if request.user.groups.filter(name="Data Senders").count() > 0 else ""
    if request.method == 'GET':
        questionnaire_form = QuestionnaireForm()
        return _get_response(form_model.form_code, project, questionnaire_form, request, disable_link_class)

    if request.method == 'POST':
        questionnaire_form = QuestionnaireForm(request.POST)
        if not questionnaire_form.is_valid():
            return _get_response(form_model.form_code, project, questionnaire_form, request, disable_link_class)

        success_message = None
        error_message = None
        try:
            response = WebPlayer(manager, get_location_tree()).accept(_create_request(questionnaire_form, request.user.username))
            if response.success:
                success_message = _("Successfully submitted")
                questionnaire_form = QuestionnaireForm()
            else:
                questionnaire_form._errors = _to_list(response.errors, form_model.fields)
                return _get_response(form_model.form_code, project, questionnaire_form, request, disable_link_class)

        except DataObjectNotFound as exception:
            message = exception_messages.get(DataObjectNotFound).get(WEB)
            error_message = _(message) % (form_model.entity_type[0], form_model.entity_type[0])
        except Exception as exception:
            logger.exception('Web Submission failure:-')
            error_message = _(get_exception_message_for(exception=exception, channel=player.Channel.WEB))

        _project_context = _make_form_context(questionnaire_form, project, form_model.form_code, disable_link_class)
        _project_context.update({'success_message': success_message, 'error_message': error_message})
        return render_to_response('project/web_questionnaire.html', _project_context,
                                  context_instance=RequestContext(request))


@login_required(login_url='/login')
def questionnaire_preview(request, project_id=None):
    manager = get_database_manager(request.user)
    if request.method == 'GET':
        previous_link = reverse(subjects_wizard, args=[project_id])
        project = Project.load(manager.database, project_id)
        form_model = FormModel.get(manager, project.qid)
        fields = form_model.fields
        if form_model.entity_defaults_to_reporter():
            fields = helper.hide_entity_question(form_model.fields)
        project_links = _make_project_links(project, form_model.form_code)
        questions = []
        for field in fields:
            question = helper.get_preview_for_field(field)
            questions.append(question)
        example_sms = "%s .%s <%s> .... .%s <%s>" % (
            form_model.form_code, fields[0].code, _('answer'), fields[len(fields) - 1].code, _('answer'))
        return render_to_response('project/questionnaire_preview.html',
                {"questions": questions, 'questionnaire_code': form_model.form_code,
                 "previous": previous_link, 'project': project, 'project_links': project_links,
                 'example_sms': example_sms, 'org_number': _get_organization_telephone_number(request.user)},
                                  context_instance=RequestContext(request))


def _get_preview_for_field_in_registration_questionnaire(field):
    return {"description": field.label.get('en'), "code": field.code, "type": field.type,
            "constraints": field.instruction, "instruction": field.instruction}


def _get_registration_form(manager, project, project_id, type_of_subject='subject'):
    previous_link = reverse(subjects_wizard, args=[project_id])
    registration_questionnaire = form_model.get_form_model_by_code(manager, REGISTRATION_FORM_CODE)
    fields = registration_questionnaire.fields
    project_links = _make_project_links(project, registration_questionnaire.form_code)
    questions = []
    for field in fields:
        question = _get_preview_for_field_in_registration_questionnaire(field)
        question = {k: v.replace('subject', type_of_subject) for (k, v) in question.items()}
        questions.append(question)
    return fields, previous_link, project_links, questions, registration_questionnaire


def get_example_sms_message(fields, registration_questionnaire):
    example_sms = "%s <answer> .... <answer>" % (registration_questionnaire.form_code)
    if(not USE_ORDERED_SMS_PARSER):
        example_sms = "%s .%s <answer> .... .%s <answer>" % (
            registration_questionnaire.form_code, fields[0].code, fields[len(fields) - 1].code)
    return example_sms


@login_required(login_url='/login')
def subject_registration_form_preview(request, project_id=None):
    manager = get_database_manager(request.user)
    project = Project.load(manager.database, project_id)
    if request.method == "GET":
        fields, previous_link, project_links, questions, registration_questionnaire = _get_registration_form(manager,
                                                                                                             project,
                                                                                                          project_id)
        example_sms = get_example_sms_message(fields, registration_questionnaire)
        return render_to_response('project/questionnaire_preview.html',
                {"questions": questions, 'questionnaire_code': registration_questionnaire.form_code,
                 "previous": previous_link, 'project': project, 'project_links': project_links,
                 'example_sms': example_sms, 'org_number': _get_organization_telephone_number(request.user)},
                                  context_instance=RequestContext(request))


@login_required(login_url='/login')
def sender_registration_form_preview(request, project_id=None):
    manager = get_database_manager(request.user)
    project = Project.load(manager.database, project_id)
    if request.method == "GET":
        fields, previous_link, project_links, questions, registration_questionnaire = _get_registration_form(manager,
                                                                                                             project,
                                                                                                             project_id,
                                                                                                             type_of_subject='Data sender')
        example_sms = "%s .%s <%s> .... .%s <%s>" % (
            registration_questionnaire.form_code, fields[0].code, _('answer'), fields[len(fields) - 1].code, _('answer'))
        datasender_questions = _get_questions_for_datasenders_registration_for_print_preview(questions)
        return render_to_response('project/questionnaire_preview.html',
                {"questions": datasender_questions, 'questionnaire_code': registration_questionnaire.form_code,
                 "previous": previous_link, 'project': project, 'project_links': project_links,
                 'example_sms': example_sms, 'org_number': _get_organization_telephone_number(request.user)},
                                  context_instance=RequestContext(request))

def _get_organization_telephone_number(user):
    profile = user.get_profile()
    organization = Organization.objects.get(org_id=profile.org_id)
    organization_settings = OrganizationSetting.objects.get(organization=organization)
    return organization_settings.get_organisation_sms_number()

