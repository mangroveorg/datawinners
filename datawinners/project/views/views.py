# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import json
import datetime
import logging
from time import mktime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.utils import translation
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from datawinners.accountmanagement.decorators import is_datasender_allowed, is_datasender, session_not_expired, is_not_expired, is_new_user, project_has_web_device, valid_web_user

from datawinners.feeds.database import get_feeds_database
from datawinners.feeds.mail_client import mail_feed_errors
from datawinners.main.database import get_database_manager
from datawinners.project.submission.util import submission_stats
from datawinners.project.web_questionnaire_form import SubjectRegistrationForm, SurveyResponseForm
from datawinners.scheduler.smsclient import NoSMSCException
from mangrove.datastore.entity import get_by_short_code
from datawinners.alldata.helper import get_visibility_settings_for
from datawinners.custom_report_router.report_router import ReportRouter
from datawinners.entity.helper import process_create_data_sender_form, get_organization_telephone_number
from datawinners.entity import import_data as import_module
from datawinners.submission.location import LocationBridge
from datawinners.utils import get_organization, get_map_key
from mangrove.datastore.queries import get_entity_count_for_type, get_non_voided_entity_count_for_type
from mangrove.errors.MangroveException import QuestionCodeAlreadyExistsException, EntityQuestionAlreadyExistsException, DataObjectAlreadyExists, DataObjectNotFound, QuestionAlreadyExistsException
from mangrove.form_model import form_model
from mangrove.form_model.field import field_to_json
from mangrove.form_model.form_model import get_form_model_by_code, FormModel, REGISTRATION_FORM_CODE, get_form_model_by_entity_type, REPORTER, header_fields, get_form_code_by_entity_type
from mangrove.transport.player.player import WebPlayer
from mangrove.transport.services.survey_response_service import SurveyResponseService
from mangrove.utils.json_codecs import encode_json
from mangrove.utils.types import is_empty, is_string
from mangrove.transport.contract.transport_info import Channel
import datawinners.utils as utils
from datawinners.entity.import_data import load_all_entities_of_type, get_entity_type_info
from datawinners.location.LocationTree import get_location_tree
from datawinners.messageprovider.message_handler import get_exception_message_for
from datawinners.messageprovider.messages import exception_messages, WEB
from datawinners.project.forms import BroadcastMessageForm
from datawinners.project.models import Project, Reminder, ReminderMode, get_all_reminder_logs_for_project, get_all_projects
from datawinners.accountmanagement.models import Organization, OrganizationSetting, NGOUserProfile
from datawinners.entity.forms import ReporterRegistrationForm
from datawinners.entity.views import save_questionnaire as subject_save_questionnaire, create_single_web_user, viewable_questionnaire, initialize_values, get_example_sms_message, get_example_sms
# from datawinners.project.wizard_view import reminders
from datawinners.location.LocationTree import get_location_hierarchy
from datawinners.project import models
from datawinners.project.subject_question_creator import SubjectQuestionFieldCreator
from datawinners.project import helper
from datawinners.project.utils import make_project_links
from datawinners.project.helper import is_project_exist, get_feed_dictionary
from datawinners.activitylog.models import UserActivityLog
from datawinners.common.constant import DELETED_PROJECT, ACTIVATED_PROJECT, REGISTERED_SUBJECT, REGISTERED_DATA_SENDER, EDITED_PROJECT
from datawinners.questionnaire.questionnaire_builder import QuestionnaireBuilder
from datawinners.project.views.utils import get_form_context, get_project_details_dict_for_feed
from mangrove.transport.player.new_players import WebPlayerV2
from mangrove.transport.repository.survey_responses import survey_response_count, get_survey_responses
from datawinners.project.utils import is_quota_reached
from datawinners.submission.views import check_quotas_and_update_users


logger = logging.getLogger("django")
performance_logger = logging.getLogger("performance")
websubmission_logger = logging.getLogger("websubmission")

END_OF_DAY = " 23:59:59"
START_OF_DAY = " 00:00:00"

PAGE_SIZE = 10
NUMBER_TYPE_OPTIONS = ["Latest", "Sum", "Count", "Min", "Max", "Average"]
MULTI_CHOICE_TYPE_OPTIONS = ["Latest", "sum(yes)", "percent(yes)", "sum(no)", "percent(no)"]
DATE_TYPE_OPTIONS = ["Latest"]
GEO_TYPE_OPTIONS = ["Latest"]
TEXT_TYPE_OPTIONS = ["Latest", "Most Frequent"]

XLS_TUPLE_FORMAT = "%s (%s)"


@login_required(login_url='/login')
@is_not_expired
def save_questionnaire(request):
    manager = get_database_manager(request.user)
    if request.method == 'POST':
        questionnaire_code = request.POST['questionnaire-code']
        json_string = request.POST['question-set']
        question_set = json.loads(json_string)
        pid = request.POST['pid']
        project = Project.load(manager.database, pid)
        form_model = FormModel.get(manager, project.qid)
        old_fields = form_model.fields
        try:
            QuestionnaireBuilder(form_model, manager).update_questionnaire_with_questions(question_set)
        except QuestionCodeAlreadyExistsException as e:
            return HttpResponseServerError(e)
        except QuestionAlreadyExistsException as e:
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
            detail = utils.get_changed_questions(old_fields, form_model.fields, subject=False)
            form_model.save()
            UserActivityLog().log(request, project=project.name, action=EDITED_PROJECT, detail=json.dumps(detail))
            return HttpResponse(json.dumps({"response": "ok"}))


@login_required(login_url='/login')
@session_not_expired
@is_new_user
@is_datasender
@is_not_expired
def index(request):
    project_list = []
    rows = models.get_all_projects(dbm=get_database_manager(request.user))
    for row in rows:
        project_id = row['value']['_id']
        link = reverse('project-overview', args=[project_id])
        if row['value']['state'] == 'Inactive':
            link = reverse('edit_project', args=[project_id])
        activate_link = reverse('activate_project', args=[project_id])
        delete_link = reverse('delete_project', args=[project_id])
        project = dict(delete_link=delete_link, name=row['value']['name'], created=row['value']['created'],
                       type=row['value']['project_type'],
                       link=link, activate_link=activate_link, state=row['value']['state'])
        project_list.append(project)
    return render_to_response('project/index.html', {'projects': project_list},
                              context_instance=RequestContext(request))


@login_required(login_url='/login')
@session_not_expired
@is_new_user
@is_datasender
@is_not_expired
def delete_project(request, project_id):
    manager = get_database_manager(request.user)
    project = Project.load(manager.database, project_id)
    helper.delete_project(manager, project)
    undelete_link = reverse(undelete_project, args=[project_id])
    if len(get_all_projects(manager)) > 0:
        messages.info(request, undelete_link)
    UserActivityLog().log(request, action=DELETED_PROJECT, project=project.name)
    return HttpResponseRedirect(reverse(index))


def undelete_project(request, project_id):
    manager = get_database_manager(request.user)
    project = Project.load(manager.database, project_id)
    helper.delete_project(manager, project, void=False)
    return HttpResponseRedirect(reverse(index))


@login_required(login_url='/login')
@session_not_expired
@is_datasender
@is_not_expired
@is_project_exist
def project_overview(request, project_id=None):
    manager = get_database_manager(request.user)
    project = Project.load(manager.database, project_id)
    questionnaire = FormModel.get(manager, project.qid)
    number_of_questions = len(questionnaire.fields)
    questionnaire_code = questionnaire.form_code
    project_links = make_project_links(project, questionnaire_code)
    map_api_key = get_map_key(request.META['HTTP_HOST'])
    number_data_sender = len(project.data_senders)
    number_records = survey_response_count(manager, questionnaire_code, None, None)
    number_reminders = Reminder.objects.filter(project_id=project.id).count()
    links = {'registered_data_senders': reverse("registered_datasenders", args=[project_id]),
             'web_questionnaire_list': reverse('web_questionnaire', args=[project_id])}
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
        'is_quota_reached': is_quota_reached(request),
        'number_of_questions': number_of_questions,
        'map_api_key': map_api_key,
        'number_data_sender': number_data_sender,
        'number_records': number_records,
        'number_reminders': number_reminders,
        'links': links,
        'add_data_senders_to_see_on_map_msg': add_data_senders_to_see_on_map_msg,
        'add_subjects_to_see_on_map_msg': add_subjects_to_see_on_map_msg,
        'in_trial_mode': in_trial_mode,
        'questionnaire_code': questionnaire_code,
        'org_number':get_organization_telephone_number(request)
    }))


def _to_name_id_string(value, delimiter='</br>'):
    if not isinstance(value, tuple): return value
    assert len(value) >= 2
    if not value[1]: return value[0]

    return "%s%s(%s)" % (value[0], delimiter, value[1])


def formatted_data(field_values, delimiter='</br>'):
    return [[_to_name_id_string(each, delimiter) for each in row] for row in field_values]


def _format_string_for_reminder_table(value):
    return (' '.join(value.split('_'))).title()


def _make_reminder_mode(reminder_mode, day):
    if reminder_mode == ReminderMode.ON_DEADLINE:
        return _format_string_for_reminder_table(reminder_mode)
    return str(day) + ' days ' + _format_string_for_reminder_table(reminder_mode)


def _format_reminder(reminder, project_id):
    return dict(message=reminder.message, id=reminder.id,
                to=_format_string_for_reminder_table(reminder.remind_to),
                when=_make_reminder_mode(reminder.reminder_mode, reminder.day))
                # delete_link=reverse('delete_reminder', args=[project_id, reminder.id]))


def _format_reminders(reminders, project_id):
    return [_format_reminder(reminder, project_id) for reminder in reminders]


# @login_required(login_url='/login')
# @session_not_expired
# @csrf_exempt
# @is_not_expired
# def create_reminder(request, project_id):
#     if is_empty(request.POST['id']):
#         Reminder(project_id=project_id, day=request.POST.get('day', 0), message=request.POST['message'],
#                  reminder_mode=request.POST['reminder_mode'], remind_to=request.POST['remind_to'],
#                  organization=utils.get_organization(request)).save()
#         messages.success(request, 'Reminder added successfully')
#     else:
#         reminder = Reminder.objects.filter(project_id=project_id, id=request.POST['id'])[0]
#         reminder.day = request.POST.get('day', 0)
#         reminder.message = request.POST['message']
#         reminder.reminder_mode = request.POST['reminder_mode']
#         reminder.remind_to = request.POST['remind_to']
#         reminder.save()
#         messages.success(request, 'Reminder updated successfully')
#     return HttpResponseRedirect(reverse(reminders, args=[project_id]))


# @login_required(login_url='/login')
# @session_not_expired
# @csrf_exempt
# @is_not_expired
# def get_reminder(request, project_id):
#     reminder_id = request.GET['id']
#     reminder = Reminder.objects.filter(project_id=project_id, id=reminder_id)[0]
#     return HttpResponse(json.dumps(reminder.to_dict()))


# @login_required(login_url='/login')
# @session_not_expired
# @csrf_exempt
# @is_not_expired
# def delete_reminder(request, project_id, reminder_id):
#     Reminder.objects.filter(project_id=project_id, id=reminder_id)[0].delete()
#     messages.success(request, 'Reminder deleted')
#     return HttpResponseRedirect(reverse(reminders, args=[project_id]))


# @login_required(login_url='/login')
# @csrf_exempt
# @is_not_expired
# def manage_reminders(request, project_id):
#     if request.method == 'GET':
#         reminders = Reminder.objects.filter(project_id=project_id, voided=False)
#         return HttpResponse(json.dumps([reminder.to_dict() for reminder in reminders]))
#
#     if request.method == 'POST':
#         reminders = json.loads(request.POST['reminders'])
#         Reminder.objects.filter(project_id=project_id).delete()
#         for reminder in reminders:
#             Reminder(project_id=project_id, day=reminder['day'], message=reminder['message'],
#                      reminder_mode=reminder['reminderMode'], organization=utils.get_organization(request),
#                      remind_to=reminder['targetDataSenders']).save()
#         return HttpResponse("Reminders has been saved")


@login_required(login_url='/login')
@session_not_expired
@is_datasender
@is_not_expired
def sent_reminders(request, project_id):
    dbm = get_database_manager(request.user)
    project = Project.load(dbm.database, project_id)
    questionnaire = FormModel.get(dbm, project.qid)
    organization = Organization.objects.get(org_id=request.user.get_profile().org_id)
    is_trial_account = organization.in_trial_mode
    html = 'project/reminders_trial.html' if organization.in_trial_mode else 'project/sent_reminders.html'
    return render_to_response(html,
                              {'project': project,
                               "project_links": make_project_links(project, questionnaire.form_code),
                               'is_quota_reached': is_quota_reached(request, organization=organization),
                               'reminders': get_all_reminder_logs_for_project(project_id, dbm),
                               'in_trial_mode': is_trial_account},
                               # 'create_reminder_link': reverse(create_reminder, args=[project_id])},
                              context_instance=RequestContext(request))


def _get_data_senders(dbm, form, project):
    data_senders = []
    if form.cleaned_data['to'] == "All":
        data_senders = _get_all_data_senders(dbm)
    elif form.cleaned_data['to'] == "Associated":
        data_senders = project.get_data_senders(dbm)
    return data_senders


@login_required(login_url='/login')
@session_not_expired
@is_datasender
@is_not_expired
def broadcast_message(request, project_id):
    dbm = get_database_manager(request.user)
    project = Project.load(dbm.database, project_id)
    number_associated_ds = len(project.data_senders)
    number_of_ds = len(import_module.load_all_entities_of_type(dbm, type=REPORTER)[0]) - 1
    questionnaire = FormModel.get(dbm, project.qid)
    organization = utils.get_organization(request)
    if request.method == 'GET':
        form = BroadcastMessageForm(associated_ds=number_associated_ds, number_of_ds=number_of_ds)
        html = 'project/broadcast_message_trial.html' if organization.in_trial_mode else 'project/broadcast_message.html'
        return render_to_response(html, {'project': project,
                                         "project_links": make_project_links(project, questionnaire.form_code),
                                         'is_quota_reached': is_quota_reached(request, organization=organization),
                                         "form": form, "ong_country": organization.country,
                                         "success": None},
                                  context_instance=RequestContext(request))
    if request.method == 'POST':
        form = BroadcastMessageForm(associated_ds=number_associated_ds, number_of_ds=number_of_ds, data=request.POST)
        if form.is_valid():
            no_smsc = False
            data_senders = _get_data_senders(dbm, form, project)
            organization_setting = OrganizationSetting.objects.get(organization=organization)
            current_month = datetime.date(datetime.datetime.now().year, datetime.datetime.now().month, 1)
            message_tracker = organization._get_message_tracker(current_month)
            other_numbers = form.cleaned_data['others']
            failed_numbers = []
            try:
                failed_numbers = helper.broadcast_message(data_senders, form.cleaned_data['text'],
                                                          organization_setting.get_organisation_sms_number()[0],
                                                          other_numbers,
                                                          message_tracker,
                                                          country_code=organization.get_phone_country_code())
            except NoSMSCException as e:
                no_smsc = True
            success = not no_smsc and len(failed_numbers) == 0

            if success:
                form = BroadcastMessageForm(associated_ds=number_associated_ds, number_of_ds=number_of_ds)
            else:
                form = BroadcastMessageForm(associated_ds=number_associated_ds, number_of_ds=number_of_ds,
                                            data=request.POST)
            return render_to_response('project/broadcast_message.html',
                                      {'project': project,
                                       "project_links": make_project_links(project, questionnaire.form_code),
                                       'is_quota_reached': is_quota_reached(request, organization=organization),
                                       "form": form,
                                       "ong_country": organization.country, "no_smsc": no_smsc,
                                       'failed_numbers': ",".join(failed_numbers), "success": success},
                                      context_instance=RequestContext(request))

        return render_to_response('project/broadcast_message.html',
                                  {'project': project,
                                   "project_links": make_project_links(project, questionnaire.form_code), "form": form,
                                   'is_quota_reached': is_quota_reached(request, organization=organization),
                                   'success': None, "ong_country": organization.country},
                                  context_instance=RequestContext(request))


def _get_all_data_senders(dbm):
    data_senders, fields, labels = load_all_entities_of_type(dbm)
    return [dict(zip(fields, data["cols"])) for data in data_senders]


@login_required(login_url='/login')
@session_not_expired
@is_datasender
@is_not_expired
def activate_project(request, project_id=None):
    manager = get_database_manager(request.user)
    project = Project.load(manager.database, project_id)
    project.activate(manager)
    form_model = FormModel.get(manager, project.qid)
    oneDay = datetime.timedelta(days=1)
    tomorrow = datetime.datetime.now() + oneDay
    survey_responses = get_survey_responses(manager, form_model.form_code, from_time=0,
                                            to_time=int(mktime(tomorrow.timetuple())) * 1000, page_size=None)
    feeds_dbm = get_feeds_database(request.user)
    service = SurveyResponseService(manager, logger, feeds_dbm)
    additional_feed_dictionary = get_project_details_dict_for_feed(project)
    for survey_response in survey_responses:
        service.delete_survey(survey_response, additional_feed_dictionary)
    UserActivityLog().log(request, action=ACTIVATED_PROJECT, project=project.name)
    return HttpResponseRedirect(reverse('project-overview', args=[project_id]))


@valid_web_user
def review_and_test(request, project_id=None):
    manager = get_database_manager(request.user)
    project = Project.load(manager.database, project_id)
    form_model = FormModel.get(manager, project.qid)
    if request.method == 'GET':
        number_of_registered_subjects = get_non_voided_entity_count_for_type(manager, project.entity_type)
        number_of_registered_data_senders = len(project.data_senders)
        fields = form_model.fields
        if form_model.is_entity_type_reporter():
            fields = helper.hide_entity_question(form_model.fields)
        is_reminder = "enabled" if len(Reminder.objects.filter(project_id=project.id)) != 0 else "disabled"

        project_devices = project.devices
        devices = ", ".join(project_devices).replace('sms', 'SMS').replace('web', 'Web').replace('smartPhone',
                                                                                                 'Smartphone')

        in_trial_mode = _in_trial_mode(request)
        return render_to_response('project/review_and_test.html', {'project': project, 'fields': fields,
                                                                   'project_links': make_project_links(project,
                                                                                                       form_model.form_code),
                                                                   'is_quota_reached': is_quota_reached(request),
                                                                   'number_of_datasenders': number_of_registered_data_senders
            ,
                                                                   'number_of_subjects': number_of_registered_subjects,
                                                                   "is_reminder": is_reminder,
                                                                   "in_trial_mode": in_trial_mode,
                                                                   "devices": devices},
                                  context_instance=RequestContext(request))


def _get_project_and_project_link(manager, project_id, reporter_id=None):
    project = Project.load(manager.database, project_id)
    questionnaire = FormModel.get(manager, project.qid)
    project_links = make_project_links(project, questionnaire.form_code, reporter_id)
    return project, project_links


@valid_web_user
def registered_subjects(request, project_id=None):
    manager = get_database_manager(request.user)
    project, project_links = _get_project_and_project_link(manager, project_id)
    subject = get_entity_type_info(project.entity_type, manager=manager)
    in_trial_mode = _in_trial_mode(request)
    form_model = get_form_model_by_entity_type(manager, [subject.get('entity')])
    return render_to_response('project/subjects/registered_subjects_list.html',
                              {'project': project,
                               'project_links': project_links,
                               'is_quota_reached': is_quota_reached(request),
                               "subject": subject,
                               'in_trial_mode': in_trial_mode,
                               'project_id': project_id,
                               'entity_type': subject.get('entity'),
                               'subject_headers': header_fields(form_model),
                               'form_code': subject.get('code')}, context_instance=RequestContext(request))


def _get_questions_for_datasenders_registration_for_print_preview(questions):
    cleaned_qestions = _get_questions_for_datasenders_registration_for_wizard(questions)
    cleaned_qestions.insert(0, questions[0])
    return cleaned_qestions


def _get_questions_for_datasenders_registration_for_wizard(questions):
    return [questions[1], questions[2], questions[3], questions[4], questions[5]]


def get_preview_and_instruction_links_for_questionnaire():
    return {'sms_preview': reverse("questionnaire_sms_preview"),
            'web_preview': reverse("questionnaire_web_preview"),
            'smart_phone_preview': reverse("smart_phone_preview"), }


@valid_web_user
@is_project_exist
def questionnaire(request, project_id=None):
    manager = get_database_manager(request.user)
    if request.method == 'GET':
        project = Project.load(manager.database, project_id)
        form_model = FormModel.get(manager, project.qid)
        fields = form_model.fields
        if form_model.is_entity_type_reporter():
            fields = helper.hide_entity_question(form_model.fields)
        existing_questions = json.dumps(fields, default=field_to_json)
        project_links = make_project_links(project, form_model.form_code)
        in_trial_mode = _in_trial_mode(request)
        return render_to_response('project/questionnaire.html',
                                  {"existing_questions": repr(existing_questions),
                                   'questionnaire_code': form_model.form_code,
                                   'project': project,
                                   'project_links': project_links,
                                   'is_quota_reached': is_quota_reached(request),
                                   'in_trial_mode': in_trial_mode,
                                   'preview_links': get_preview_and_instruction_links_for_questionnaire()},
                                  context_instance=RequestContext(request))


# def _make_project_context(form_model, project):
#     return {'form_model': form_model, 'project': project,
#             'project_links': make_project_links(project,
#                                                 form_model.form_code)}


# def _create_submission_request(form_model, request):
#     submission_request = dict(request.POST)
#     submission_request["form_code"] = form_model.form_code
#     return submission_request


# def _make_form_context(questionnaire_form, project, form_code, hide_link_class, disable_link_class):
#     return {'questionnaire_form': questionnaire_form,
#             'project': project,
#             'project_links': make_project_links(project, form_code),
#             'hide_link_class': hide_link_class,
#             'disable_link_class': disable_link_class,
#             'back_to_project_link': reverse("alldata_index"),
#             'smart_phone_instruction_link': reverse("smart_phone_instruction"),
#     }


def _get_form_code(manager, project):
    return FormModel.get(manager, project.qid).form_code


class SubjectWebQuestionnaireRequest():
    def __init__(self, request, project_id):
        self.request = request
        self._initialize(project_id)

    def _initialize(self, project_id):
        self.manager = get_database_manager(self.request.user)
        self.project = Project.load(self.manager.database, project_id)
        self.is_data_sender = self.request.user.get_profile().reporter
        self.disable_link_class, self.hide_link_class = get_visibility_settings_for(self.request.user)
        self.form_code = _get_form_code(self.manager, self.project)
        self.form_model = _get_subject_form_model(self.manager, self.project.entity_type)
        self.subject_registration_code = get_form_code_by_entity_type(self.manager, [self.project.entity_type])

    def form(self, initial_data=None, country=None):
        return SubjectRegistrationForm(self.form_model, data=initial_data, country=country)

    @property
    def template(self):
        return 'entity/subject/registration.html'


    def player_response(self, created_request):
        location_bridge = LocationBridge(location_tree=get_location_tree(), get_loc_hierarchy=get_location_hierarchy)
        return WebPlayer(self.manager, location_bridge).accept(created_request, logger=websubmission_logger)


    def success_message(self, response_short_code):
        detail_dict = dict({"Subject Type": self.project.entity_type.capitalize(), "Unique ID": response_short_code})
        UserActivityLog().log(self.request, action=REGISTERED_SUBJECT, project=self.project.name,
                              detail=json.dumps(detail_dict))
        return (_("Successfully submitted. Unique identification number(ID) is:") + " %s") % (response_short_code,)


    def response_for_get_request(self, initial_data=None, is_update=False):
        questionnaire_form = self.form(initial_data=initial_data)
        form_context = get_form_context(self.form_code, self.project, questionnaire_form,
                                        self.manager, self.hide_link_class, self.disable_link_class, is_update)
        self._update_form_context(form_context, questionnaire_form,
                                  web_view_enabled=self.request.GET.get("web_view", False))
        form_context.update({'is_quota_reached': is_quota_reached(self.request)})
        return render_to_response(self.template, form_context, context_instance=RequestContext(self.request))


    def _update_form_context(self, form_context, questionnaire_form, web_view_enabled=True):
        form_context.update({'extension_template': 'project/subjects.html',
                             'form_code': self.subject_registration_code,
                             'entity_type': self.project.entity_type,
                             "questionnaire_form": questionnaire_form,
                             "questions": self.form_model.fields,
                             "org_number": get_organization_telephone_number(self.request),
                             "example_sms": get_example_sms_message(self.form_model.fields,
                                                                    self.subject_registration_code),
                             "web_view": web_view_enabled,
                             "back_link": reverse("registered_subjects", args=[self.project.id]),
                             "edit_subject_questionnaire_link": reverse('edit_my_subject_questionnaire',
                                                                        args=[self.project.id]),
                             "register_subjects_link": reverse('subject_questionnaire',
                                                               args=[self.project.id]) + "?web_view=True"}
        )

    def invalid_data_response(self, questionnaire_form, is_update):
        form_context = get_form_context(self.form_code, self.project, questionnaire_form,
                                        self.manager, self.hide_link_class, self.disable_link_class, is_update)
        self._update_form_context(form_context, questionnaire_form)
        return render_to_response(self.template, form_context,
                                  context_instance=RequestContext(self.request))

    def success_resposne(self, is_update, organization, questionnaire_form):
        success_message = None
        error_message = None
        try:
            created_request = helper.create_request(questionnaire_form, self.request.user.username, is_update=is_update)
            response = self.player_response(created_request)
            if response.success:
                ReportRouter().route(organization.org_id, response)
                success_message = _("Your changes have been saved.") if is_update else self.success_message(
                    response.short_code)
            if not is_update:
                questionnaire_form = self.form(country=organization.country_name())
            else:
                questionnaire_form._errors = helper.errors_to_list(response.errors, self.form_model.fields)
        except DataObjectNotFound as exception:
            logger.exception(exception)
            message = exception_messages.get(DataObjectNotFound).get(WEB)
            error_message = _(message) % (self.form_model.entity_type[0], self.form_model.entity_type[0])
        except Exception as exception:
            logger.exception('Web Submission failure:-')
            error_message = _(get_exception_message_for(exception=exception, channel=Channel.WEB))
        _project_context = get_form_context(self.form_code, self.project, questionnaire_form,
                                            self.manager, self.hide_link_class, self.disable_link_class,
                                            is_update=is_update)
        _project_context.update({'success_message': success_message, 'error_message': error_message})
        self._update_form_context(_project_context, questionnaire_form)
        return render_to_response(self.template, _project_context,
                                  context_instance=RequestContext(self.request))

    def post(self, is_update=None):
        organization = get_organization(self.request)
        questionnaire_form = self.form(self.request.POST, organization.country_name())
        if not questionnaire_form.is_valid():
            return self.invalid_data_response(questionnaire_form, is_update)

        return self.success_resposne(is_update, organization, questionnaire_form)


class SurveyWebQuestionnaireRequest():
    def __init__(self, request, project_id=None):
        self.request = request
        self.manager = get_database_manager(self.request.user)
        self.project = Project.load(self.manager.database, project_id)
        self.form_model = FormModel.get(self.manager, self.project.qid)
        self.form_code = self.form_model.form_code
        self.feeds_dbm = get_feeds_database(request.user)
        self.subject_field_creator = SubjectQuestionFieldCreator(self.manager, self.project)
        self.is_data_sender = self.request.user.get_profile().reporter
        self.disable_link_class, self.hide_link_class = get_visibility_settings_for(self.request.user)

    def form(self, initial_data=None):
        return SurveyResponseForm(self.form_model, self.subject_field_creator,
                                  data=initial_data, is_datasender=self.is_data_sender)

    @property
    def template(self):
        return 'project/data_submission.html' if self.is_data_sender else "project/web_questionnaire.html"

    def response_for_get_request(self, initial_data=None, is_update=False):
        questionnaire_form = self.form(initial_data=initial_data)
        form_context = get_form_context(self.form_model.form_code, self.project, questionnaire_form,
                                        self.manager, self.hide_link_class, self.disable_link_class, is_update)
        form_context.update({'is_quota_reached': is_quota_reached(self.request)})
        return render_to_response(self.template, form_context, context_instance=RequestContext(self.request))


    def player_response(self, created_request):
        user_profile = NGOUserProfile.objects.get(user=self.request.user)
        if self.project.entity_type == u"reporter":
            reporter_id = created_request.message.get('eid')
        else:
            reporter_id = user_profile.reporter_id

        additional_feed_dictionary = get_feed_dictionary(self.project)
        web_player = WebPlayerV2(self.manager, self.feeds_dbm, user_profile.reporter_id)
        response = web_player.add_survey_response(created_request, reporter_id, additional_feed_dictionary,
                                                  websubmission_logger)
        mail_feed_errors(response, self.manager.database_name)
        if response.success and not created_request.is_update:
            organization = Organization.objects.get(org_id=user_profile.org_id)
            organization.increment_message_count_for(incoming_web_count=1)
            check_quotas_and_update_users(organization)
        return response

    def response_for_post_request(self, is_update=None):
        questionnaire_form = self.form(self.request.POST)
        quota_reached = is_quota_reached(self.request)
        if not questionnaire_form.is_valid() or quota_reached:
            form_context = get_form_context(self.form_code, self.project, questionnaire_form,
                                            self.manager, self.hide_link_class, self.disable_link_class)
            form_context.update({'is_quota_reached': quota_reached})
            return render_to_response(self.template, form_context,
                                      context_instance=RequestContext(self.request))

        success_message = None
        error_message = None
        if self.is_data_sender:
            questionnaire_form.cleaned_data['eid'] = self.request.user.get_profile().reporter_id
        try:
            created_request = helper.create_request(questionnaire_form, self.request.user.username, is_update=is_update)
            response = self.player_response(created_request)
            if response.success:
                ReportRouter().route(get_organization(self.request).org_id, response)
                success_message = _("Successfully submitted")
            else:
                questionnaire_form._errors = helper.errors_to_list(response.errors, self.form_model.fields)
        except DataObjectNotFound as exception:
            logger.exception(exception)
            message = exception_messages.get(DataObjectNotFound).get(WEB)
            error_message = _(message) % (self.form_model.entity_type[0], self.form_model.entity_type[0])
        except Exception as exception:
            logger.exception('Web Submission failure:-')
            error_message = _(get_exception_message_for(exception=exception, channel=Channel.WEB))

        _project_context = get_form_context(self.form_code, self.project, questionnaire_form,
                                            self.manager, self.hide_link_class, self.disable_link_class,
                                            is_update=is_update)

        _project_context.update({'success_message': success_message, 'error_message': error_message,
                                 'questionnaire_form':self.form(), })

        return render_to_response(self.template, _project_context,
                                  context_instance=RequestContext(self.request))


@login_required(login_url='/login')
@session_not_expired
@is_datasender_allowed
@project_has_web_device
@is_not_expired
@is_project_exist
def survey_web_questionnaire(request, project_id=None):
    survey_request = SurveyWebQuestionnaireRequest(request, project_id)
    if request.method == 'GET':
        return survey_request.response_for_get_request()
    elif request.method == 'POST':
        return survey_request.response_for_post_request()


@login_required(login_url='/login')
@session_not_expired
@is_datasender_allowed
@project_has_web_device
@is_not_expired
@is_project_exist
def subject_web_questionnaire(request, project_id=None):
    subject_request = SubjectWebQuestionnaireRequest(request, project_id)
    if request.method == 'GET':
        return subject_request.response_for_get_request()
    elif request.method == 'POST':
        return subject_request.post()


@valid_web_user
@is_project_exist
# TODO : TW_BLR : what happens in case of POST?
def questionnaire_preview(request, project_id=None, sms_preview=False):
    manager = get_database_manager(request.user)
    if request.method == 'GET':
        project = Project.load(manager.database, project_id)
        form_model = FormModel.get(manager, project.qid)
        fields = form_model.fields
        if form_model.is_entity_type_reporter():
            fields = helper.hide_entity_question(form_model.fields)
        project_links = make_project_links(project, form_model.form_code)
        questions = []
        for field in fields:
            question = helper.get_preview_for_field(field)
            questions.append(question)
        example_sms = "%s" % (
            form_model.form_code)
        example_sms += get_example_sms(fields)

    template = 'project/questionnaire_preview.html' if sms_preview else 'project/questionnaire_preview_list.html'
    return render_to_response(template,
                              {"questions": questions, 'questionnaire_code': form_model.form_code,
                               'project': project, 'project_links': project_links,
                               'is_quota_reached': is_quota_reached(request),
                               'example_sms': example_sms, 'org_number': get_organization_telephone_number(request)},
                              context_instance=RequestContext(request))


def _get_registration_form(manager, project, type_of_subject='reporter'):
    if type_of_subject == 'reporter':
        registration_questionnaire = form_model.get_form_model_by_code(manager, REGISTRATION_FORM_CODE)
    else:
        entity_type = [project.entity_type]
        registration_questionnaire = get_form_model_by_entity_type(manager, entity_type)
        if registration_questionnaire is None:
            registration_questionnaire = form_model.get_form_model_by_code(manager, REGISTRATION_FORM_CODE)
    questions = viewable_questionnaire(registration_questionnaire)
    project_links = make_project_links(project, registration_questionnaire.form_code)
    return registration_questionnaire.fields, project_links, questions, registration_questionnaire


@valid_web_user
def subject_registration_form_preview(request, project_id=None):
    manager = get_database_manager(request.user)
    project = Project.load(manager.database, project_id)
    if request.method == "GET":
        fields, project_links, questions, registration_questionnaire = _get_registration_form(manager,
                                                                                              project,
                                                                                              project.entity_type)
        example_sms = get_example_sms_message(fields, registration_questionnaire.form_code)
        return render_to_response('project/questionnaire_preview_list.html',
                                  {"questions": questions, 'questionnaire_code': registration_questionnaire.form_code,
                                   'project': project, 'project_links': project_links,
                                   'is_quota_reached': is_quota_reached(request),
                                   'example_sms': example_sms,
                                   'org_number': get_organization_telephone_number(request)},
                                  context_instance=RequestContext(request))


@valid_web_user
def sender_registration_form_preview(request, project_id=None):
    manager = get_database_manager(request.user)
    project = Project.load(manager.database, project_id)
    if request.method == "GET":
        fields, project_links, questions, registration_questionnaire = _get_registration_form(manager,
                                                                                              project,
                                                                                              type_of_subject='reporter')
        datasender_questions = _get_questions_for_datasenders_registration_for_print_preview(questions)
        example_sms = get_example_sms_message(datasender_questions, registration_questionnaire.form_code)
        return render_to_response('project/questionnaire_preview_list.html',
                                  {"questions": datasender_questions,
                                   'questionnaire_code': registration_questionnaire.form_code,
                                   'project': project, 'project_links': project_links,
                                   'is_quota_reached': is_quota_reached(request),
                                   'example_sms': example_sms,
                                   'org_number': get_organization_telephone_number(request)},
                                  context_instance=RequestContext(request))


def _get_subject_form_model(manager, entity_type):
    if is_string(entity_type):
        entity_type = [entity_type]
    return get_form_model_by_entity_type(manager, entity_type)


@valid_web_user
def edit_my_subject_questionnaire(request, project_id=None):
    manager = get_database_manager(request.user)
    project, project_links = _get_project_and_project_link(manager, project_id)

    reg_form = _get_subject_form_model(manager, project.entity_type)
    if reg_form is None:
        reg_form = form_model.get_form_model_by_code(manager, REGISTRATION_FORM_CODE)
    fields = reg_form.fields
    existing_questions = json.dumps(fields, default=field_to_json)
    subject = get_entity_type_info(project.entity_type, manager=manager)
    return render_to_response('project/subject_questionnaire.html',
                              {'project': project,
                               'project_links': project_links,
                               'is_quota_reached': is_quota_reached(request),
                               'existing_questions': repr(existing_questions),
                               'questionnaire_code': reg_form.form_code,
                               'language': reg_form.activeLanguages[0],
                               'entity_type': project.entity_type,
                               'subject': subject,
                               'post_url': reverse(subject_save_questionnaire)},
                              context_instance=RequestContext(request))


def append_success_to_context(context, form):
    success = False
    if not len(form.errors):
        success = True
    context.update({'success': success})
    return context


@login_required(login_url='/login')
@session_not_expired
@is_datasender_allowed
@project_has_web_device
@is_not_expired
def create_data_sender_and_web_user(request, project_id=None):
    manager = get_database_manager(request.user)
    project, project_links = _get_project_and_project_link(manager, project_id)
    in_trial_mode = _in_trial_mode(request)

    if request.method == 'GET':
        form = ReporterRegistrationForm(initial={'project_id': project_id})
        return render_to_response('project/register_datasender.html', {
            'project': project,
            'project_links': project_links,
            'is_quota_reached': is_quota_reached(request),
            'form': form,
            'in_trial_mode': in_trial_mode,
            'current_language': translation.get_language()
        }, context_instance=RequestContext(request))

    if request.method == 'POST':
        org_id = request.user.get_profile().org_id
        form = ReporterRegistrationForm(org_id=org_id, data=request.POST)
        try:
            reporter_id, message = process_create_data_sender_form(manager, form, org_id)
        except DataObjectAlreadyExists as e:
            message = _("Data Sender with Unique Identification Number (ID) = %s already exists.") % e.data[1]

        if not len(form.errors) and reporter_id:
            project.associate_data_sender_to_project(manager, reporter_id)
            if form.requires_web_access():
                email_id = request.POST['email']
                create_single_web_user(org_id=org_id, email_address=email_id, reporter_id=reporter_id,
                                       language_code=request.LANGUAGE_CODE)
            UserActivityLog().log(request, action=REGISTERED_DATA_SENDER,
                                  detail=json.dumps(dict({"Unique ID": reporter_id})), project=project.name)
        if message is not None and reporter_id:
            form = ReporterRegistrationForm(initial={'project_id': form.cleaned_data['project_id']})
        context = {'form': form, 'message': message, 'in_trial_mode': in_trial_mode, 'success': reporter_id is not None}
        return render_to_response('datasender_form.html',
                                  context,
                                  context_instance=RequestContext(request))


def _in_trial_mode(request):
    return utils.get_organization(request).in_trial_mode


@login_required(login_url='/login')
@session_not_expired
@is_datasender
@is_not_expired
def project_has_data(request, questionnaire_code=None):
    manager = get_database_manager(request.user)
    form_model = get_form_model_by_code(manager, questionnaire_code)
    success, error = submission_stats(manager, form_model.form_code)
    return HttpResponse(encode_json({'has_data': (success + error > 0)}))


def edit_my_subject(request, entity_type, entity_id, project_id=None):
    manager = get_database_manager(request.user)
    subject = get_by_short_code(manager, entity_id, [entity_type.lower()])
    subject_request = SubjectWebQuestionnaireRequest(request, project_id)
    form_model = subject_request.form_model
    if request.method == 'GET':
        initialize_values(form_model, subject)
        return subject_request.response_for_get_request(is_update=True)
    elif request.method == 'POST':
        return subject_request.post(is_update=True)