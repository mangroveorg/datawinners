# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from copy import copy
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
from datawinners.entity.import_data import load_all_subjects_of_type
from datawinners.initializer import TEST_REPORTER_MOBILE_NUMBER
from datawinners.main.utils import get_database_manager, include_of_type
from datawinners.messageprovider.message_handler import get_exception_message_for
from datawinners.project.forms import ProjectProfile, ReminderForm
from datawinners.project.models import Project, ProjectState, Reminder
from datawinners.accountmanagement.models import Organization, OrganizationSetting
from datawinners.entity.forms import ReporterRegistrationForm
from datawinners.entity.forms import SubjectUploadForm
from datawinners.entity.views import import_subjects_from_project_wizard
import helper
from datawinners.project import models
from mangrove.datastore.documents import DataRecordDocument
from mangrove.datastore.data import EntityAggregration
from mangrove.datastore.entity import get_all_entity_types, get_entity_count_for_type
from mangrove.errors.MangroveException import QuestionCodeAlreadyExistsException, EntityQuestionAlreadyExistsException, DataObjectAlreadyExists
from mangrove.form_model import form_model
from mangrove.form_model.field import field_to_json, SelectField
from mangrove.form_model.form_model import get_form_model_by_code, FormModel, REGISTRATION_FORM_CODE
from mangrove.transport.player import player
from mangrove.transport.player.player import WebPlayer, Request, TransportInfo
from mangrove.transport.submissions import get_submissions_made_for_form, SubmissionLogger, get_submission_count_for_form
from django.contrib import messages
from mangrove.utils.dates import convert_to_epoch
from mangrove.datastore import aggregrate as aggregate_module
from mangrove.utils.json_codecs import encode_json
from django.core.urlresolvers import reverse
import datawinners.utils as utils

import logging

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
                     'activate_project_link': reverse(activate_project, args=[project_id])}

    if project.state == ProjectState.TEST or project.state == ProjectState.ACTIVE:
        project_links['data_analysis_link'] = reverse(project_data, args=[project_id, questionnaire_code])
        project_links['submission_log_link'] = reverse(project_results, args=[project_id, questionnaire_code])

    if project.state == ProjectState.ACTIVE:
        project_links['questionnaire_link'] = reverse(questionnaire, args=[project_id])
        project_links['test_questionnaire_link'] = reverse(web_questionnaire, args=[project_id])

        project_links['subjects_link'] = reverse(subjects, args=[project_id])
        project_links['registered_subjects_link'] = reverse(registered_subjects, args=[project_id])

        project_links['datasenders_link'] = reverse(datasenders, args=[project_id])
        project_links['registered_datasenders_link'] = reverse(registered_datasenders, args=[project_id])
        project_links['questionnaire_preview_link'] = reverse(questionnaire_preview, args=[project_id])
        project_links['subject_registration_preview_link'] = reverse(subject_registration_form_preview,
                                                                     args=[project_id])
        project_links['sender_registration_preview_link'] = reverse(sender_registration_form_preview, args=[project_id])
        project_links['reminders_link'] = reverse(reminders, args=[project_id])
    return project_links


@login_required(login_url='/login')
def questionnaire_wizard(request, project_id=None):
    manager = get_database_manager(request.user)
    if request.method == 'GET':
        previous_link = reverse(subjects_wizard, args=[project_id])
        project = models.get_project(project_id, manager)
        form_model = helper.load_questionnaire(manager, project.qid)
        fields = form_model.fields
        if form_model.entity_defaults_to_reporter():
            fields = helper.hide_entity_question(form_model.fields)
        existing_questions = json.dumps(fields, default=field_to_json)
        return render_to_response('project/questionnaire_wizard.html',
                {"existing_questions": repr(existing_questions), 'questionnaire_code': form_model.form_code,
                 "previous": previous_link, 'project': project}, context_instance=RequestContext(request))


@login_required(login_url='/login')
def create_profile(request):
    manager = get_database_manager(request.user)
    entity_list = get_all_entity_types(manager)
    entity_list = helper.remove_reporter(entity_list)
    project_summary = dict(name='New Project')
    if request.method == 'GET':
        form = ProjectProfile(entity_list=entity_list, initial={'activity_report': 'yes'})
        return render_to_response('project/profile.html', {'form': form, 'project': project_summary, 'edit': False},
                                  context_instance=RequestContext(request))

    form = ProjectProfile(data=request.POST, entity_list=entity_list)
    if form.is_valid():
        entity_type = form.cleaned_data['entity_type']
        project = Project(name=form.cleaned_data["name"], goals=form.cleaned_data["goals"],
                          project_type=form.cleaned_data['project_type'], entity_type=entity_type,
                          devices=form.cleaned_data['devices'], activity_report=form.cleaned_data['activity_report'],
                          sender_group=form.cleaned_data['sender_group'],
                          reminder_and_deadline=helper.deadline_and_reminder(form.cleaned_data))
        form_model = helper.create_questionnaire(post=form.cleaned_data, dbm=manager)
        try:
            pid = project.save(manager)
            qid = form_model.save()
            project.qid = qid
            pid = project.save(manager)
        except DataObjectAlreadyExists as e:
            messages.error(request, e.message)
            return render_to_response('project/profile.html', {'form': form, 'project': project_summary, 'edit': False},
                                      context_instance=RequestContext(request))
        return HttpResponseRedirect(reverse(subjects_wizard, args=[pid]))
    else:
        return render_to_response('project/profile.html', {'form': form, 'project': project_summary, 'edit': False},
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
def edit_profile(request, project_id=None):
    manager = get_database_manager(request.user)
    entity_list = get_all_entity_types(manager)
    entity_list = helper.remove_reporter(entity_list)
    project = models.get_project(project_id, dbm=manager)
    if request.method == 'GET':
        form = ProjectProfile(data=(_generate_project_info_with_deadline_and_reminders(project)), entity_list=entity_list)
        return render_to_response('project/profile.html', {'form': form, 'project': project, 'edit': True},
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
        project = models.get_project(pid, dbm=manager)
        form_model = manager.get(project.qid, FormModel)
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
@utils.is_new_user
def index(request):
    project_list = []
    rows = models.get_all_projects(dbm=get_database_manager(request.user))
    for row in rows:
        project_id = row['value']['_id']
        link = reverse(project_overview, args=[project_id])
        activate_link = reverse(activate_project, args=[project_id])
        project = dict(name=row['value']['name'], created=row['value']['created'], type=row['value']['project_type'],
                       link=link, activate_link=activate_link, state=row['value']['state'])
        project["created"] = project["created"].strftime("%d %B, %Y")
        project_list.append(project)
    return render_to_response('project/index.html', {'projects': project_list},
                              context_instance=RequestContext(request))


@login_required(login_url='/login')
def project_overview(request, project_id=None):
    manager = get_database_manager(request.user)
    project = models.get_project(project_id, dbm=manager)
    link = reverse(edit_profile, args=[project_id])
    questionnaire = helper.load_questionnaire(manager, project['qid'])
    number_of_questions = len(questionnaire.fields)
    project_links = _make_project_links(project, questionnaire.form_code)
    return render_to_response('project/overview.html',
            {'project': project, 'entity_type': project['entity_type'], 'project_links': project_links
             , 'project_profile_link': link, 'number_of_questions': number_of_questions},
                              context_instance=RequestContext(request))


def _get_submissions_for_display(current_page, dbm, questionnaire_code, questions, pagination, start_time=None,
                                 end_time=None):
    if pagination:
        submissions, ids = get_submissions_made_for_form(dbm, questionnaire_code, start_time=start_time,
                                                         end_time=end_time, page_number=current_page,
                                                         page_size=PAGE_SIZE)
    else:
        submissions, ids = get_submissions_made_for_form(dbm, questionnaire_code, start_time=start_time,
                                                         end_time=end_time, page_number=current_page,
                                                         page_size=None)
    submissions = helper.get_submissions(questions, submissions)
    return submissions, ids


def _load_submissions(current_page, manager, questionnaire_code, pagination=True, start_time=None, end_time=None):
    form_model = get_form_model_by_code(manager, questionnaire_code)
    questionnaire = (questionnaire_code, form_model.name)
    fields = form_model.fields
    if form_model.entity_defaults_to_reporter():
        fields = form_model.fields[1:]
    questions = helper.get_code_and_title(fields)
    count = get_submission_count_for_form(manager, questionnaire_code, start_time, end_time)
    results = {'questionnaire': questionnaire,
               'questions': questions}
    if count:
        submissions, ids = _get_submissions_for_display(current_page - 1, manager, questionnaire_code, copy(questions),
                                                        pagination, start_time=start_time, end_time=end_time)
        results.update(submissions=zip(submissions, ids))
    return count, results

#TODO- Refactoring needed for results and data related views.


@login_required(login_url='/login')
def project_results(request, project_id=None, questionnaire_code=None):
    manager = get_database_manager(request.user)
    project = models.get_project(project_id, dbm=manager)
    project_links = _make_project_links(project, questionnaire_code)
    if request.method == 'GET':
        count, results, error_message = _get_submissions(manager, questionnaire_code, request)
        return render_to_response('project/results.html',
                {'questionnaire_code': questionnaire_code, 'results': results, 'pages': count,
                 'error_message': error_message, 'project_links': project_links, 'project': project},
                                  context_instance=RequestContext(request)
        )
    if request.method == "POST":
        data_record_ids = json.loads(request.POST.get('id_list'))
        for each in data_record_ids:
            data_record = manager._load_document(each, DataRecordDocument)
            manager.invalidate(each)
            SubmissionLogger(manager).void_data_record(data_record.submission.get("submission_id"))
        current_page = request.POST.get('current_page')
        count, results = _load_submissions(int(current_page), manager, questionnaire_code)
        return render_to_response('project/log_table.html',
                {'questionnaire_code': questionnaire_code, 'results': results, 'pages': count,
                 'success_message': "The selected records have been deleted"}, context_instance=RequestContext(request))


def _load_submissions_for_page(manager, current_page, questionnaire_code, start_time_epoch, end_time_epoch):
    count, results = _load_submissions(current_page, manager, questionnaire_code, True, start_time_epoch,
                                       end_time_epoch)
    return count, results


def _load_all_submissions(manager, questionnaire_code, start_time_epoch, end_time_epoch):
    count, results = _load_submissions(1, manager, questionnaire_code, False, start_time_epoch,
                                       end_time_epoch)
    return count, results


def _get_submissions(manager, questionnaire_code, request, paginate=True):
    request_bag = request.GET
    start_time = request_bag.get("start_time") or ""
    end_time = request_bag.get("end_time") or ""
    start_time_epoch = convert_to_epoch(helper.get_formatted_time_string(start_time.strip() + START_OF_DAY))
    end_time_epoch = convert_to_epoch(helper.get_formatted_time_string(end_time.strip() + END_OF_DAY))
    if paginate:
        current_page = int(request_bag.get('page_number') or 1)
        count, results = _load_submissions_for_page(manager, current_page, questionnaire_code,
                                                    start_time_epoch, end_time_epoch)
    else:
        count, results = _load_all_submissions(manager, questionnaire_code, start_time_epoch, end_time_epoch)

    error_message = "No submissions present for this project" if not count else None
    return count, results, error_message


@login_required(login_url='/login')
def submissions(request):
    """
            Called via ajax, returns the partial HTML for the submissions made for the project, paginated.
    """
    manager = get_database_manager(request.user)
    if request.method == 'GET':
        questionnaire_code = request.GET.get('questionnaire_code')
        count, results, error_message = _get_submissions(manager, questionnaire_code, request)
        return render_to_response('project/log_table.html',
                {'questionnaire_code': questionnaire_code, 'results': results, 'pages': count,
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
def project_data(request, project_id=None, questionnaire_code=None):
    manager = get_database_manager(request.user)
    project = models.get_project(project_id, dbm=manager)
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
def export_log(request):
    questionnaire_code = request.GET.get("questionnaire_code")
    manager = get_database_manager(request.user)

    count, results, error_message = _get_submissions(manager, questionnaire_code, request, paginate=False)

    header_list = ["To", "From", "Date Received", "Submission status", "Deleted Record", "Errors"]
    header_list.extend([each[1] for each in results['questions']])
    raw_data_list = [header_list]
    if count:
        submissions, ids = zip(*results['submissions'])
        raw_data_list.extend([list(each) for each in submissions])

    file_name = request.GET.get(u"project_name") + '_log'
    return _create_excel_response(raw_data_list, file_name)


@login_required(login_url='/login')
def subjects_wizard(request, project_id=None):
    if request.method == 'GET':
        manager = get_database_manager(request.user)
        reg_form = get_form_model_by_code(manager, REGISTRATION_FORM_CODE)
        previous_link = reverse(edit_profile, args=[project_id])
        entity_types = get_all_entity_types(manager)
        project = models.get_project(project_id, manager)
        helper.remove_reporter(entity_types)
        import_subject_form = SubjectUploadForm()
        return render_to_response('project/subjects_wizard.html',
                {'fields': reg_form.fields, "previous": previous_link, "entity_types": entity_types,
                 'import_subject_form': import_subject_form,
                 'post_url': reverse(import_subjects_from_project_wizard), 'project': project, 'step': 'subjects'},
                                  context_instance=RequestContext(request))

    if request.method == 'POST':
        return HttpResponseRedirect(reverse(questionnaire_wizard, args=[project_id]))


def _format_field_description_for_data_senders(reg_form_fields):
    for field in reg_form_fields:
        if field.code == 't':
            continue
        temp = field.label.get("eng")
        temp = temp.replace("subject", "data sender")
        field.label.update(eng=temp)


def _get_imports_subjects_post_url(project_id=None):
    import_url = reverse(import_subjects_from_project_wizard)
    return import_url if project_id is None else ("%s?project_id=%s" % (import_url, project_id))


@login_required(login_url='/login')
def datasenders_wizard(request, project_id=None):
    if request.method == 'GET':
        manager = get_database_manager(request.user)
        reg_form = get_form_model_by_code(manager, REGISTRATION_FORM_CODE)
        previous_link = reverse(questionnaire_wizard, args=[project_id])
        project = models.get_project(project_id, manager)
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
        project = models.get_project(project_id, dbm)
        previous_link = reverse(datasenders_wizard, args=[project_id])
        return render_to_response('project/reminders_wizard.html',
                {"previous": previous_link, 'project_id': project_id, 'is_reminder': project.reminders,
                 'form': ReminderForm(
                     initial={'is_reminder': project.reminders})},
                                  context_instance=RequestContext(request))
    if request.method == 'POST':
        return HttpResponseRedirect(reverse(finish, args=[project_id]))


@login_required(login_url='/login')
def reminders(request, project_id):
    if request.method == 'GET':
        dbm = get_database_manager(request.user)
        project = models.get_project(project_id, dbm)
        questionnaire = helper.load_questionnaire(dbm, project.qid)
        return render_to_response('project/reminders.html',
                {'project': project, "project_links": _make_project_links(project, questionnaire.form_code),
                 'project_id': project_id, 'form': ReminderForm(initial={'is_reminder': project.reminders}),
                 'is_reminder': project.reminders},
                                  context_instance=RequestContext(request))


@login_required(login_url='/login')
@csrf_exempt
def manage_reminders(request, project_id):
    if request.method == 'GET':
        reminders = Reminder.objects.filter(project_id=project_id)
        return HttpResponse(json.dumps([reminder.to_dict() for reminder in reminders]))

    if request.method == 'POST':
        reminders = json.loads(request.POST['reminders'])
        Reminder.objects.filter(project_id=project_id).delete()
        for reminder in reminders:
            Reminder(project_id=project_id, day_of_the_month=reminder['day'], message=reminder['message'],
                     organization=utils.get_organization(request)).save()
        return HttpResponse("Reminders has been saved")


@csrf_exempt
def enable_reminders_in_project(request, project_id=None):
    if request.method == 'POST':
        dbm = get_database_manager(request.user)
        project = models.get_project(project_id, dbm)
        project.reminders = True if request.POST['is_reminder'] == 'True' else False
        project.save(dbm)
        return HttpResponse("The status of reminder for project %s is %d" % (project.name, project.reminders))


@login_required(login_url='/login')
def activate_project(request, project_id=None):
    manager = get_database_manager(request.user)
    project = models.get_project(project_id, manager)
    project.activate(manager)
    form_model = helper.load_questionnaire(manager, project.qid)
    oneDay = datetime.timedelta(days=1)
    tomorrow = datetime.datetime.now() + oneDay
    submissions, ids = get_submissions_made_for_form(manager, form_model.form_code, start_time=0,
                                                     end_time=int(mktime(tomorrow.timetuple())) * 1000,
                                                     page_size=None)
    for each in ids:
        if each is not None:
            data_record = manager._load_document(each, DataRecordDocument)
            manager.invalidate(each)
            SubmissionLogger(manager).void_data_record(data_record.submission.get("submission_id"))
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
    project = models.get_project(project_id, manager)
    form_model = helper.load_questionnaire(manager, project.qid)
    if request.method == 'GET':
        project.to_test_mode(manager)
        number_of_registered_subjects = get_entity_count_for_type(manager, project.entity_type)
        number_of_registered_datasenders = get_entity_count_for_type(manager, 'reporter')
        profile = request.user.get_profile()
        organization = Organization.objects.get(org_id=profile.org_id)
        from_number = TEST_REPORTER_MOBILE_NUMBER
        organization_settings = OrganizationSetting.objects.get(organization=organization)
        to_number = organization_settings.sms_tel_number
        previous_link = reverse(reminders_wizard, args=[project_id])
        fields = form_model.fields[1:] if form_model.entity_defaults_to_reporter() else form_model.fields
        is_reminder = "enabled" if project.reminders else "disabled"
        return render_to_response('project/finish_and_test.html', {'from_number': from_number, 'to_number': to_number,
                                                                   'project': project, 'fields': fields,
                                                                   'project_links': _make_links_for_finish_page(
                                                                       project_id, form_model),
                                                                   'number_of_datasenders': number_of_registered_datasenders
                                                                   ,
                                                                   'number_of_subjects': number_of_registered_subjects,
                                                                   "previous": previous_link,
                                                                   "is_reminder": is_reminder},
                                  context_instance=RequestContext(request))
    if request.method == 'POST':
        return HttpResponseRedirect(reverse(project_overview, args=[project_id]))


def _get_project_and_project_link(manager, project_id):
    project = models.get_project(project_id, manager)
    questionnaire = helper.load_questionnaire(manager, project.qid)
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


def _get_associated_data_senders(all_data, project):
    return [data for data in all_data if data['short_name'] in project.data_senders]


@login_required(login_url='/login')
def registered_datasenders(request, project_id=None):
    manager = get_database_manager(request.user)
    project, project_links = _get_project_and_project_link(manager, project_id)
    all_data = load_all_subjects_of_type(manager)
    associated_datasenders = _get_associated_data_senders(all_data, project)
    return render_to_response('project/registered_datasenders.html',
            {'project': project, 'project_links': project_links, 'all_data': associated_datasenders},
                              context_instance=RequestContext(request))


@login_required(login_url='/login')
@csrf_exempt
def disassociate_datasenders(request):
    manager = get_database_manager(request.user)
    project = models.get_project(request.POST['project_id'], manager)
    ids = request.POST['ids[]']
    project.data_senders = [datasender for datasender in project.data_senders if datasender not in ids]
    project.save(manager)
    return HttpResponse(reverse(registered_datasenders, args=(project.id,)))


def _get_questions_for_datasenders_registration_for_print_preview(questions):
    cleaned_qestions = _get_questions_for_datasenders_registration_for_wizard(questions)
    cleaned_qestions.insert(0, questions[0])
    return cleaned_qestions


def _get_questions_for_datasenders_registration_for_wizard(questions):
    return [questions[1], questions[3], questions[4], questions[6]]


@login_required(login_url='/login')
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
        project = models.get_project(project_id, manager)
        form_model = helper.load_questionnaire(manager, project.qid)
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


def _make_form_context(questionnaire_form, project, form_code):
    return {'questionnaire_form': questionnaire_form, 'project': project,
            'project_links': _make_project_links(project, form_code)}


def _create_select_field(field, choices):
    if field.single_select_flag:
        return forms.ChoiceField(choices=choices, required=False, label=field.name, initial=field.value)
    return forms.MultipleChoiceField(choices=choices, widget=forms.SelectMultiple(
        attrs={'class': 'multiple_select', 'size': len(choices)}), required=False, label=field.name,
                                     initial=field.value)


def _create_choices(field):
    choice_list = [('', '--None--')]
    for option in field.options:
        choice_list.append((option['val'], option['text']['eng']))
    choices = tuple(choice_list)
    return choices


def _get_django_field(field):
    if isinstance(field, SelectField):
        return  _create_select_field(field, _create_choices(field))
    display_field = forms.CharField(label=field.name, initial=field.value, required=False)
    display_field.widget.attrs["watermark"] = field.get_constraint_text()
    #    display_field.widget.attrs["watermark"] = "18 - 1"
    return display_field


def _create_django_form_from_form_model(form_model):
    properties = {field.code.lower(): _get_django_field(field) for field in form_model.fields}
    properties.update({'form_code': forms.CharField(widget=HiddenInput, initial=form_model.form_code)})
    return type('QuestionnaireForm', (Form, ), properties)


def _to_list(errors):
    error_dict = dict()
    for key, value in errors.items():
        error_dict.update({key: [value] if not isinstance(value, list) else value})
    return error_dict


def _create_request(questionnaire_form, username):
    return Request(message=questionnaire_form.cleaned_data,
                   transportInfo=
                   TransportInfo(transport="web",
                                 source=username,
                                 destination=""
                   ))


def _get_response(form_code, project, questionnaire_form, request):
    return render_to_response('project/web_questionnaire.html',
                              _make_form_context(questionnaire_form, project, form_code),
                              context_instance=RequestContext(request))


@login_required(login_url='/login')
def web_questionnaire(request, project_id=None):
    manager = get_database_manager(request.user)
    project = models.get_project(project_id, manager)
    form_model = helper.load_questionnaire(manager, project.qid)

    QuestionnaireForm = _create_django_form_from_form_model(form_model)

    if request.method == 'GET':
        questionnaire_form = QuestionnaireForm()
        return _get_response(form_model.form_code, project, questionnaire_form, request)

    if request.method == 'POST':
        questionnaire_form = QuestionnaireForm(request.POST)
        if not questionnaire_form.is_valid():
            return _get_response(form_model.form_code, project, questionnaire_form, request)

        success_message = None
        error_message = None
        try:
            response = WebPlayer(manager).accept(_create_request(questionnaire_form, request.user.username))
            if response.success:
                success_message = "Successfully submitted"
                questionnaire_form = QuestionnaireForm()
            else:
                questionnaire_form._errors = _to_list(response.errors)
                return _get_response(form_model.form_code, project, questionnaire_form, request)
        except Exception as exception:
            logger.exception('Web Submission failure:-')
            error_message = get_exception_message_for(exception=exception, channel=player.Channel.WEB)

        _project_context = _make_form_context(questionnaire_form, project, form_model.form_code)
        _project_context.update({'success_message': success_message, 'error_message': error_message})
        return render_to_response('project/web_questionnaire.html', _project_context,
                                  context_instance=RequestContext(request))


@login_required(login_url='/login')
def questionnaire_preview(request, project_id=None):
    manager = get_database_manager(request.user)
    if request.method == 'GET':
        previous_link = reverse(subjects_wizard, args=[project_id])
        project = models.get_project(project_id, manager)
        form_model = helper.load_questionnaire(manager, project.qid)
        fields = form_model.fields
        if form_model.entity_defaults_to_reporter():
            fields = helper.hide_entity_question(form_model.fields)
        project_links = _make_project_links(project, form_model.form_code)
        questions = []
        for field in fields:
            question = helper.get_preview_for_field(field)
            questions.append(question)
        example_sms = "%s +%s <answer> .... +%s <answer>" % (
            form_model.form_code, fields[0].code, fields[len(fields) - 1].code)
        return render_to_response('project/questionnaire_preview.html',
                {"questions": questions, 'questionnaire_code': form_model.form_code,
                 "previous": previous_link, 'project': project, 'project_links': project_links,
                 'example_sms': example_sms},
                                  context_instance=RequestContext(request))


def _get_preview_for_field_in_registration_questionnaire(field):
    return {"description": field.label.get('eng'), "code": field.code, "type": field.type,
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


@login_required(login_url='/login')
def subject_registration_form_preview(request, project_id=None):
    manager = get_database_manager(request.user)
    project = models.get_project(project_id, manager)
    if request.method == "GET":
        fields, previous_link, project_links, questions, registration_questionnaire = _get_registration_form(manager,
                                                                                                             project,
                                                                                                             project_id)

        example_sms = "%s +%s <answer> .... +%s <answer>" % (
            registration_questionnaire.form_code, fields[0].code, fields[len(fields) - 1].code)
        return render_to_response('project/questionnaire_preview.html',
                {"questions": questions, 'questionnaire_code': registration_questionnaire.form_code,
                 "previous": previous_link, 'project': project, 'project_links': project_links,
                 'example_sms': example_sms},
                                  context_instance=RequestContext(request))


@login_required(login_url='/login')
def sender_registration_form_preview(request, project_id=None):
    manager = get_database_manager(request.user)
    project = models.get_project(project_id, manager)
    if request.method == "GET":
        fields, previous_link, project_links, questions, registration_questionnaire = _get_registration_form(manager,
                                                                                                             project,
                                                                                                             project_id,
                                                                                                             type_of_subject='Data sender')
        example_sms = "%s +%s <answer> .... +%s <answer>" % (
            registration_questionnaire.form_code, fields[0].code, fields[len(fields) - 1].code)
        datasender_questions = _get_questions_for_datasenders_registration_for_print_preview(questions)
        return render_to_response('project/questionnaire_preview.html',
                {"questions": datasender_questions, 'questionnaire_code': registration_questionnaire.form_code,
                 "previous": previous_link, 'project': project, 'project_links': project_links,
                 'example_sms': example_sms},
                                  context_instance=RequestContext(request))
