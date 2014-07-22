# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from _codecs import encode
import json
import datetime
import logging
from operator import itemgetter
import datawinners

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_view_exempt
from django.utils import translation
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _, ugettext
from datawinners.alldata import views
from datawinners.common.urlextension import append_query_strings_to_url
from mangrove.datastore.entity import get_by_short_code
from mangrove.datastore.entity_type import get_unique_id_types
from mangrove.datastore.queries import get_entity_count_for_type
from mangrove.errors.MangroveException import DataObjectAlreadyExists, DataObjectNotFound
from mangrove.form_model import form_model
from mangrove.form_model.field import field_to_json
from mangrove.form_model.form_model import get_form_model_by_code, REGISTRATION_FORM_CODE, get_form_model_by_entity_type, REPORTER, header_fields, get_form_code_by_entity_type
from mangrove.transport.player.player import WebPlayer
from mangrove.utils.json_codecs import encode_json
from mangrove.utils.types import is_empty, is_string
from mangrove.transport.contract.transport_info import Channel
from mangrove.transport.player.new_players import WebPlayerV2
from mangrove.transport.repository.survey_responses import survey_response_count

from datawinners import settings
from datawinners.accountmanagement.decorators import is_datasender_allowed, is_datasender, session_not_expired, is_not_expired, is_new_user, project_has_web_device, valid_web_user
from datawinners.blue.xform_bridge import XlsProjectParser
from datawinners.feeds.database import get_feeds_database
from datawinners.feeds.mail_client import mail_feed_errors
from datawinners.main.database import get_database_manager
from datawinners.project.submission.util import submission_stats
from datawinners.project.submission_form import SurveyResponseForm
from datawinners.project.web_questionnaire_form import SubjectRegistrationForm
from datawinners.project.wizard_view import edit_project, get_preview_and_instruction_links
from datawinners.scheduler.smsclient import NoSMSCException
from datawinners.alldata.helper import get_visibility_settings_for
from datawinners.custom_report_router.report_router import ReportRouter
from datawinners.entity.helper import process_create_data_sender_form, get_organization_telephone_number
from datawinners.entity import import_data as import_module
from datawinners.submission.location import LocationBridge
from datawinners.utils import get_organization, get_map_key
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
from datawinners.location.LocationTree import get_location_hierarchy
from datawinners.project import models
from datawinners.project import helper
from datawinners.project.utils import make_project_links
from datawinners.project.helper import is_project_exist, get_feed_dictionary
from datawinners.activitylog.models import UserActivityLog
from datawinners.common.constant import DELETED_QUESTIONNAIRE, REGISTERED_IDENTIFICATION_NUMBER, REGISTERED_DATA_SENDER, RENAMED_QUESTIONNAIRE
from datawinners.project.views.utils import get_form_context
from datawinners.project.utils import is_quota_reached
from datawinners.submission.views import check_quotas_and_update_users


logger = logging.getLogger("django")
websubmission_logger = logging.getLogger("websubmission")

@login_required
@session_not_expired
@is_new_user
@is_datasender
@is_not_expired
@is_project_exist
def delete_project(request, project_id):
    manager = get_database_manager(request.user)
    questionnaire = Project.get(manager, project_id)
    dashboard_page = settings.HOME_PAGE + "?deleted=true"
    if questionnaire.is_void():
        return HttpResponseRedirect(dashboard_page)
    helper.delete_project(questionnaire)
    undelete_link = reverse(undelete_project, args=[project_id])
    messages.info(request, undelete_link)
    UserActivityLog().log(request, action=DELETED_QUESTIONNAIRE, project=questionnaire.name)
    return HttpResponseRedirect(reverse(views.index))



@csrf_view_exempt
@valid_web_user
@is_datasender
def rename_project(request, project_id):
    manager = get_database_manager(request.user)
    questionnaire = Project.get(manager, project_id)
    new_project_name = request.POST.get('data', '').strip()
    if len(new_project_name) == 0:
        return HttpResponse(json.dumps({"status": "error", "message": ugettext("This field is required.")}),
                            content_type='application/json')

    if (questionnaire.name != new_project_name):
        questionnaire.name = new_project_name
        try:
            questionnaire.save(process_post_update=True)
            UserActivityLog().log(request, action=RENAMED_QUESTIONNAIRE, project=questionnaire.name)
            return HttpResponse(json.dumps({"status": "success"}), content_type='application/json')
        except DataObjectAlreadyExists as e:
            return HttpResponse(
                json.dumps({"status": "error", "message": ugettext("Questionnaire with same name already exists.")}),
                content_type='application/json')
    return HttpResponse(json.dumps({"status": "success"}), content_type='application/json')

@is_datasender
def undelete_project(request, project_id):
    manager = get_database_manager(request.user)
    questionnaire = Project.get(manager, project_id)
    helper.delete_project(questionnaire, void=False)
    return HttpResponseRedirect(reverse(views.index))


@login_required
@session_not_expired
@is_datasender
@is_not_expired
@is_project_exist
def project_overview(request, project_id):
    manager = get_database_manager(request.user)
    questionnaire = Project.get(manager, project_id)

    dashboard_page = settings.HOME_PAGE + "?deleted=true"
    if questionnaire.is_void():
        return HttpResponseRedirect(dashboard_page)
    number_of_questions = len(questionnaire.fields)
    questionnaire_code = questionnaire.form_code
    project_links = make_project_links(questionnaire)
    map_api_key = get_map_key(request.META['HTTP_HOST'])
    number_data_sender = len(questionnaire.data_senders)
    number_records = survey_response_count(manager, questionnaire_code, None, None)
    number_reminders = Reminder.objects.filter(project_id=questionnaire.id).count()
    links = {'registered_data_senders': reverse("registered_datasenders", args=[project_id]),
             'web_questionnaire_list': reverse('web_questionnaire', args=[project_id])}
    add_subjects_to_see_on_map_msg = ""
    if not is_empty(questionnaire.entity_type):
        subject_links = {}
        for entity_type in questionnaire.entity_type:
            subject_links.update({entity_type: append_query_strings_to_url(reverse("subject_questionnaire", args=[project_id, entity_type]),
                                                           web_view=True)})
        links.update({'create_subjects_links': subject_links})
        add_subjects_to_see_on_map_msg = _(
            "Register %s to see them on this map") % questionnaire.entity_type[0] if get_entity_count_for_type(manager,
                                                                                                               questionnaire.entity_type[
                                                                                                                   0]) == 0 else ""
    entity_type = ""
    has_multiple_unique_id = False
    in_trial_mode = _in_trial_mode(request)
    unique_id_header_text = ""
    if len(questionnaire.entity_type) == 1:
        entity_type = questionnaire.entity_type[0]
        unique_id_header_text = "%s %s &" % (ugettext("My"), entity_type.capitalize())
    if len(questionnaire.entity_type) > 1:
        has_multiple_unique_id = True
        unique_id_header_text = "%s &" % ugettext("My Identification Numbers")

    return render_to_response('project/overview.html', RequestContext(request, {
        'project': questionnaire,
        'project_links': project_links,
        'is_quota_reached': is_quota_reached(request),
        'number_of_questions': number_of_questions,
        'map_api_key': map_api_key,
        'number_data_sender': number_data_sender,
        'number_records': number_records,
        'number_reminders': number_reminders,
        'links': links,
        'add_subjects_to_see_on_map_msg': add_subjects_to_see_on_map_msg,
        'in_trial_mode': in_trial_mode,
        'questionnaire_code': questionnaire_code,
        'has_multiple_unique_id':has_multiple_unique_id,
        'entity_type': json.dumps(entity_type),
        'unique_id_header_text': unique_id_header_text,
        'org_number': get_organization_telephone_number(request)
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


def _format_reminders(reminders, project_id):
    return [_format_reminder(reminder, project_id) for reminder in reminders]


@login_required
@session_not_expired
@is_datasender
@is_not_expired
@is_project_exist
def sent_reminders(request, project_id):
    dbm = get_database_manager(request.user)
    dashboard_page = settings.HOME_PAGE + "?deleted=true"
    questionnaire = Project.get(dbm, project_id)
    if questionnaire.is_void():
        return HttpResponseRedirect(dashboard_page)
    organization = Organization.objects.get(org_id=request.user.get_profile().org_id)
    is_trial_account = organization.in_trial_mode
    html = 'project/sent_reminders_trial.html' if organization.in_trial_mode else 'project/sent_reminders.html'
    return render_to_response(html,
                              {
                                  'project': questionnaire,
                                  "project_links": make_project_links(questionnaire),
                                  'is_quota_reached': is_quota_reached(request, organization=organization),
                                  'reminders': get_all_reminder_logs_for_project(project_id, dbm),
                                  'in_trial_mode': is_trial_account,
                                  'questionnaire_code': questionnaire.form_code
                              },
                              context_instance=RequestContext(request))


def _get_data_senders(dbm, form, project):
    data_senders = []
    if form.cleaned_data['to'] == "All":
        data_senders = _get_all_data_senders(dbm)
    elif form.cleaned_data['to'] == "Associated":
        data_senders = project.get_data_senders(dbm)
    return data_senders

@login_required
@session_not_expired
@is_datasender
@is_not_expired
@is_project_exist
def broadcast_message(request, project_id):
    dbm = get_database_manager(request.user)
    questionnaire = Project.get(dbm, project_id)
    dashboard_page = settings.HOME_PAGE + "?deleted=true"
    if questionnaire.is_void():
        return HttpResponseRedirect(dashboard_page)
    number_associated_ds = len(questionnaire.data_senders)
    number_of_ds = len(import_module.load_all_entities_of_type(dbm, type=REPORTER)[0]) - 1
    organization = utils.get_organization(request)

    account_type = organization.account_type
    if (account_type == 'Pro'):
        account_type = True

    if request.method == 'GET':
        form = BroadcastMessageForm(associated_ds=number_associated_ds, number_of_ds=number_of_ds)
        html = 'project/broadcast_message_trial.html' if organization.in_trial_mode else 'project/broadcast_message.html'
        return render_to_response(html, {'project': questionnaire,
                                         "project_links": make_project_links(questionnaire),
                                         'is_quota_reached': is_quota_reached(request, organization=organization),
                                         "form": form, "ong_country": organization.country,
                                         "success": None,
                                         'questionnaire_code': questionnaire.form_code
        },
                                  context_instance=RequestContext(request))
    if request.method == 'POST':
        form = BroadcastMessageForm(associated_ds=number_associated_ds, number_of_ds=number_of_ds, data=request.POST)
        if form.is_valid():
            no_smsc = False
            data_senders = _get_data_senders(dbm, form, questionnaire)
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
                                      {'project': questionnaire,
                                       "project_links": make_project_links(questionnaire),
                                       'is_quota_reached': is_quota_reached(request, organization=organization),
                                       "form": form, "account_type": account_type,
                                       "ong_country": organization.country, "no_smsc": no_smsc,
                                       'questionnaire_code': questionnaire.form_code,
                                       'failed_numbers': ",".join(failed_numbers), "success": success},
                                      context_instance=RequestContext(request))

        return render_to_response('project/broadcast_message.html',
                                  {'project': questionnaire,
                                   "project_links": make_project_links(questionnaire), "form": form,
                                   'is_quota_reached': is_quota_reached(request, organization=organization),
                                   'questionnaire_code': questionnaire.form_code,
                                   'success': None, "ong_country": organization.country},
                                  context_instance=RequestContext(request))


def _get_all_data_senders(dbm):
    data_senders, fields, labels = load_all_entities_of_type(dbm)
    return [dict(zip(fields, data["cols"])) for data in data_senders]


def get_project_link(project, entity_type=None):
    project_links = make_project_links(project, entity_type)
    return project_links


@valid_web_user
@is_project_exist
@is_datasender
def registered_subjects(request, project_id, entity_type=None):
    manager = get_database_manager(request.user)
    questionnaire = Project.get(manager, project_id)
    dashboard_page = settings.HOME_PAGE + "?deleted=true"
    if questionnaire.is_void():
        return HttpResponseRedirect(dashboard_page)
    current_entity_type = entity_type
    if not current_entity_type:
        current_entity_type = questionnaire.entity_type[0]

    subject = get_entity_type_info(current_entity_type, manager=manager)
    project_links = get_project_link(questionnaire, current_entity_type)
    subject_form_model = get_form_model_by_entity_type(manager, [current_entity_type])
    in_trial_mode = _in_trial_mode(request)
    return render_to_response('project/subjects/registered_subjects_list.html',
                              {'project': questionnaire,
                               'project_links': project_links,
                               'is_quota_reached': is_quota_reached(request),
                               "subject": subject,
                               'in_trial_mode': in_trial_mode,
                               'project_id': project_id,
                               'entity_type': current_entity_type,
                               'subject_headers': header_fields(subject_form_model),
                               'questionnaire_code': questionnaire.form_code,
                               'form_code': subject_form_model.form_code}, context_instance=RequestContext(request))


def _get_questions_for_datasenders_registration_for_print_preview(questions):
    cleaned_qestions = _get_questions_for_datasenders_registration_for_wizard(questions)
    cleaned_qestions.insert(0, questions[0])
    return cleaned_qestions


def _get_questions_for_datasenders_registration_for_wizard(questions):
    return [questions[1], questions[2], questions[3], questions[4], questions[5]]


@valid_web_user
@is_project_exist
@is_datasender
def questionnaire(request, project_id):
    manager = get_database_manager(request.user)
    if request.method == 'GET':
        questionnaire = Project.get(manager, project_id)
        if questionnaire.is_void():
            return HttpResponseRedirect(settings.HOME_PAGE + "?deleted=true")
        fields = questionnaire.fields
        existing_questions = json.dumps(fields, default=field_to_json)
        project_links = make_project_links(questionnaire)
        success, error = submission_stats(manager, questionnaire.form_code)
        project_has_submissions = (success + error > 0)
        in_trial_mode = _in_trial_mode(request)
        is_success = False
        active_language = request.LANGUAGE_CODE
        if "success" in [m.message for m in messages.get_messages(request)]:
            is_success = True
        if questionnaire.xform:
                try: # find a better way to check attachement exisits
                    questionnaire.get_attachments('questionnaire.xls')
                    show_xls_download_link = True
                except LookupError:
                    show_xls_download_link = False

                return render_to_response('project/edit_xform.html',
                                  {"existing_questions": repr(existing_questions),
                                   'questionnaire_code': questionnaire.form_code,
                                   'project': questionnaire,
                                   'project_id': project_id,
                                   'project_has_submissions': project_has_submissions,
                                   'project_links': project_links,
                                   'is_quota_reached': is_quota_reached(request),
                                   'in_trial_mode': in_trial_mode,
                                   'show_xls_download_link': show_xls_download_link,
                                   'post_url': reverse(edit_project, args=[project_id]),
                                   # 'xls_form': repr(json.dumps(XlsProjectParser().parse(questionnaire.get_attachments(attachment_name='questionnaire.xls')))),
                                   'preview_links': get_preview_and_instruction_links()},
                                  context_instance=RequestContext(request))
        return render_to_response('project/questionnaire.html',
                                  {"existing_questions": repr(existing_questions),
                                   'questionnaire_code': questionnaire.form_code,
                                   'project': questionnaire,
                                   'project_has_submissions': project_has_submissions,
                                   'project_links': project_links,
                                   'is_quota_reached': is_quota_reached(request),
                                   'in_trial_mode': in_trial_mode,
                                   'is_success':is_success,
                                   'active_language':active_language,
                                   'post_url': reverse(edit_project, args=[project_id]),
                                   'unique_id_types': get_unique_id_types(manager),
                                   'preview_links': get_preview_and_instruction_links()},
                                  context_instance=RequestContext(request))


@valid_web_user
@is_project_exist
def get_questionnaire_ajax(request, project_id):
    manager = get_database_manager(request.user)
    project = Project.get(manager, project_id)
    existing_questions = project.fields
    return HttpResponse(json.dumps({
                                       'name': project.name,
                                       'language': project.language,
                                       'questions': existing_questions,
                                       'is_outgoing_sms_enabled': project.is_outgoing_sms_replies_enabled,
                                       'datasenders': project.data_senders,
                                       'reminder_and_deadline': project.reminder_and_deadline
                                   }, default=field_to_json), content_type='application/json')


class SubjectWebQuestionnaireRequest():
    def __init__(self, request, project_id, entity_type=None):
        self.request = request
        self._initialize(project_id, entity_type)

    def _initialize(self, project_id, entity_type=None):
        self.manager = get_database_manager(self.request.user)
        self.questionnaire = Project.get(self.manager, project_id)
        if self.questionnaire.is_void():
            return HttpResponseRedirect(settings.HOME_PAGE + "?deleted=true")
        self.is_data_sender = self.request.user.get_profile().reporter
        self.disable_link_class, self.hide_link_class = get_visibility_settings_for(self.request.user)
        #self.form_code = self.questionnaire.form_code
        self.entity_type = entity_type
        self.form_model = _get_subject_form_model(self.manager, entity_type)
        self.subject_registration_code = get_form_code_by_entity_type(self.manager, [entity_type])

    def form(self, initial_data=None, country=None):
        return SubjectRegistrationForm(self.form_model, data=initial_data, country=country)

    @property
    def template(self):
        return 'entity/register_subject.html' if self.is_data_sender else 'entity/subject/registration.html'


    def player_response(self, created_request):
        location_bridge = LocationBridge(location_tree=get_location_tree(), get_loc_hierarchy=get_location_hierarchy)
        return WebPlayer(self.manager, location_bridge).accept(created_request, logger=websubmission_logger)


    def success_message(self, response_short_code):
        entity_type = self.questionnaire.entity_type[0].capitalize()
        detail_dict = dict(
            {"Subject Type": entity_type, "Unique ID": response_short_code})
        UserActivityLog().log(self.request, action=REGISTERED_IDENTIFICATION_NUMBER, project=self.questionnaire.name,
                              detail=json.dumps(detail_dict))
        return (_("%s with Identification Number %s successfully registered.")) % (entity_type,response_short_code)

    def response_for_get_request(self, initial_data=None, is_update=False):
        if self.entity_type not in self.questionnaire.entity_type:
            raise Http404
        questionnaire_form = self.form(initial_data=initial_data)
        form_context = get_form_context(self.questionnaire, questionnaire_form, self.manager, self.hide_link_class,
                                        self.disable_link_class, entity_type=self.entity_type, is_update=is_update)
        self._update_form_context(form_context, questionnaire_form,
                                  web_view_enabled=self.request.GET.get("web_view", False))
        form_context.update({'is_quota_reached': is_quota_reached(self.request)})
        return render_to_response(self.template, form_context, context_instance=RequestContext(self.request))


    def _update_form_context(self, form_context, questionnaire_form, web_view_enabled=True):
        form_context.update({'extension_template': 'project/subjects.html',
                             'form_code': self.subject_registration_code,
                             'entity_type': self.entity_type,
                             'project_id': self.questionnaire.id,
                             "questionnaire_form": questionnaire_form,
                             "questions": self.form_model.fields,
                             "org_number": get_organization_telephone_number(self.request),
                             "example_sms": get_example_sms_message(self.form_model.fields,
                                                                    self.subject_registration_code),
                             "web_view": web_view_enabled,
                             "back_link": reverse("registered_subjects", args=[self.questionnaire.id, self.entity_type]),
                             "edit_subject_questionnaire_link": reverse('edit_my_subject_questionnaire',
                                                                        args=[self.questionnaire.id, self.entity_type]),
                             "register_subjects_link": reverse('subject_questionnaire',
                                                               args=[self.questionnaire.id, self.entity_type]) + "?web_view=True"}
        )

    def invalid_data_response(self, questionnaire_form, is_update):
        form_context = get_form_context(self.questionnaire, questionnaire_form, self.manager, self.hide_link_class,
                                        self.disable_link_class, is_update)
        self._update_form_context(form_context, questionnaire_form)
        return render_to_response(self.template, form_context,
                                  context_instance=RequestContext(self.request))

    def success_response(self, is_update, organization, questionnaire_form):
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
        except DataObjectAlreadyExists as exception:
            error_message = _("%s with %s %s already exists.") % (exception.data[2], _(exception.data[0]), exception.data[1])
        except Exception as exception:
            logger.exception('Web Submission failure:-')
            error_message = _(get_exception_message_for(exception=exception, channel=Channel.WEB))
        _project_context = get_form_context(self.questionnaire, questionnaire_form, self.manager, self.hide_link_class,
                                            self.disable_link_class, is_update=is_update)
        _project_context.update({'success_message': success_message, 'error_message': error_message})
        self._update_form_context(_project_context, questionnaire_form)
        return render_to_response(self.template, _project_context,
                                  context_instance=RequestContext(self.request))

    def post(self, is_update=None):
        organization = get_organization(self.request)
        questionnaire_form = self.form(self.request.POST, organization.country_name())
        if not questionnaire_form.is_valid():
            return self.invalid_data_response(questionnaire_form, is_update)

        return self.success_response(is_update, organization, questionnaire_form)


class SurveyWebQuestionnaireRequest():
    def __init__(self, request, project_id=None):
        self.request = request
        self.manager = get_database_manager(self.request.user)
        self.questionnaire = Project.get(self.manager, project_id)
        self.form_code = self.questionnaire.form_code
        self.feeds_dbm = get_feeds_database(request.user)
        self.is_data_sender = self.request.user.get_profile().reporter
        self.disable_link_class, self.hide_link_class = get_visibility_settings_for(self.request.user)

    def form(self, initial_data=None):
        return SurveyResponseForm(self.questionnaire, data=initial_data, is_datasender=self.is_data_sender)

    @property
    def template(self):
        return 'project/data_submission.html' if self.is_data_sender else "project/web_questionnaire.html"

    def response_for_get_request(self, initial_data=None, is_update=False):
        dashboard_page = settings.HOME_PAGE + "?deleted=true"
        if self.questionnaire.is_void():
            return HttpResponseRedirect(dashboard_page)
        if self.questionnaire.xform:
            return HttpResponseRedirect(reverse('xform_web_questionnaire', args=[self.questionnaire.id]))
        questionnaire_form = self.form(initial_data=initial_data)
        form_context = get_form_context(self.questionnaire, questionnaire_form, self.manager, self.hide_link_class,
                                        self.disable_link_class, is_update)
        form_context.update({
            'is_quota_reached': is_quota_reached(self.request),
            'questionnaire_code': self.questionnaire.form_code,
            'is_datasender': self.is_data_sender,
            'is_advance_questionnaire': False,
        })
        return render_to_response(self.template, form_context, context_instance=RequestContext(self.request))


    def player_response(self, created_request, reporter_id):
        user_profile = NGOUserProfile.objects.get(user=self.request.user)
        additional_feed_dictionary = get_feed_dictionary(self.questionnaire)
        if not reporter_id:
            reporter_id = user_profile.reporter_id
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
            form_context = get_form_context(self.questionnaire, questionnaire_form, self.manager, self.hide_link_class,
                                            self.disable_link_class)
            form_context.update({'is_quota_reached': quota_reached})
            return render_to_response(self.template, form_context,
                                      context_instance=RequestContext(self.request))

        success_message = None
        error_message = None
        # if self.is_data_sender:
        #     questionnaire_form.cleaned_data['eid'] = self.request.user.get_profile().reporter_id
        try:
            created_request = helper.create_request(questionnaire_form, self.request.user.username, is_update=is_update)
            reporter_id = self.request.POST.get('dsid')
            response = self.player_response(created_request, reporter_id)
            if response.success:
                ReportRouter().route(get_organization(self.request).org_id, response)
                success_message = _("Successfully submitted")
            else:
                questionnaire_form._errors = helper.errors_to_list(response.errors, self.questionnaire.fields)
        except DataObjectNotFound as exception:
            logger.exception(exception)
            message = exception_messages.get(DataObjectNotFound).get(WEB)
            error_message = _(message) % (self.questionnaire.entity_type[0], self.questionnaire.entity_type[0])
        except Exception as exception:
            logger.exception('Web Submission failure:-')
            error_message = _(get_exception_message_for(exception=exception, channel=Channel.WEB))

        _project_context = get_form_context(self.questionnaire, questionnaire_form, self.manager, self.hide_link_class,
                                            self.disable_link_class, is_update=is_update)

        _project_context.update({'success_message': success_message, 'error_message': error_message,
                                 'questionnaire_form': self.form(), })

        return render_to_response(self.template, _project_context,
                                  context_instance=RequestContext(self.request))


@login_required
@session_not_expired
@is_project_exist
@is_datasender_allowed
@project_has_web_device
@is_not_expired
def survey_web_questionnaire(request, project_id):
    survey_request = SurveyWebQuestionnaireRequest(request, project_id)
    if request.method == 'GET':
        return survey_request.response_for_get_request()
    elif request.method == 'POST':
        return survey_request.response_for_post_request()


@login_required
@session_not_expired
@is_project_exist
@is_datasender_allowed
@project_has_web_device
@is_not_expired
#@is_datasender
def subject_web_questionnaire(request, project_id=None, entity_type=None):
    subject_request = SubjectWebQuestionnaireRequest(request, project_id, entity_type)
    if request.method == 'GET':
        return subject_request.response_for_get_request()
    elif request.method == 'POST':
        return subject_request.post()


@valid_web_user
@is_project_exist
@is_datasender
# TODO : TW_BLR : what happens in case of POST?
def questionnaire_preview(request, project_id=None, sms_preview=False):
    manager = get_database_manager(request.user)
    if request.method == 'GET':
        dashboard_page = settings.HOME_PAGE + "?deleted=true"
        questionnaire = Project.get(manager, project_id)
        if questionnaire.is_void():
            return HttpResponseRedirect(dashboard_page)
            #if form_model.is_entity_type_reporter():
        #    fields = helper.hide_entity_question(form_model.fields)
        project_links = make_project_links(questionnaire)
        questions = []
        fields = questionnaire.fields
        for field in fields:
            question = helper.get_preview_for_field(field)
            questions.append(question)
        example_sms = "%s" % (
            questionnaire.form_code)
        example_sms += get_example_sms(fields)

    template = 'project/questionnaire_preview.html' if sms_preview else 'project/questionnaire_preview_list.html'
    return render_to_response(template,
                              {"questions": questions, 'questionnaire_code': questionnaire.form_code,
                               'project': questionnaire, 'project_links': project_links,'project_name':questionnaire.name,
                               'is_quota_reached': is_quota_reached(request),
                               'example_sms': example_sms, 'org_number': get_organization_telephone_number(request)},
                              context_instance=RequestContext(request))


def _get_registration_form(manager, project, type_of_subject='reporter'):
    if type_of_subject == 'reporter':
        registration_questionnaire = form_model.get_form_model_by_code(manager, REGISTRATION_FORM_CODE)
    else:
        entity_type = type_of_subject
        registration_questionnaire = get_form_model_by_entity_type(manager, [entity_type])
        if registration_questionnaire is None:
            registration_questionnaire = form_model.get_form_model_by_code(manager, REGISTRATION_FORM_CODE)
    questions = viewable_questionnaire(registration_questionnaire)
    project_links = make_project_links(project, entity_type)
    return registration_questionnaire.fields, project_links, questions, registration_questionnaire


@valid_web_user
@is_project_exist
def subject_registration_form_preview(request, project_id=None, entity_type=None):
    manager = get_database_manager(request.user)
    questionnaire = Project.get(manager, project_id)
    dashboard_page = settings.HOME_PAGE + "?deleted=true"
    if questionnaire.is_void():
        return HttpResponseRedirect(dashboard_page)
    if not entity_type:
        entity_type = questionnaire.entity_type[0]
    if request.method == "GET":
        fields, project_links, questions, registration_questionnaire = _get_registration_form(manager,
                                                                                              questionnaire,
                                                                                              entity_type)
        example_sms = get_example_sms_message(fields, registration_questionnaire.form_code)
        return render_to_response('project/questionnaire_preview_list.html',
                                  {"questions": questions, 'questionnaire_code': registration_questionnaire.form_code,
                                   'project': questionnaire, 'project_links': project_links,
                                   'is_quota_reached': is_quota_reached(request),
                                   'example_sms': example_sms,
                                   'org_number': get_organization_telephone_number(request)},
                                  context_instance=RequestContext(request))


@valid_web_user
def sender_registration_form_preview(request, project_id=None):
    manager = get_database_manager(request.user)
    dashboard_page = settings.HOME_PAGE + "?deleted=true"
    questionnaire = Project.get(manager, project_id)
    if questionnaire.is_void():
        return HttpResponseRedirect(dashboard_page)
    if request.method == "GET":
        fields, project_links, questions, registration_questionnaire = _get_registration_form(manager,
                                                                                              questionnaire,
                                                                                              type_of_subject='reporter')
        datasender_questions = _get_questions_for_datasenders_registration_for_print_preview(questions)
        example_sms = get_example_sms_message(datasender_questions, registration_questionnaire.form_code)
        return render_to_response('project/questionnaire_preview_list.html',
                                  {"questions": datasender_questions,
                                   'questionnaire_code': registration_questionnaire.form_code,
                                   'project': questionnaire, 'project_links': project_links,
                                   'is_quota_reached': is_quota_reached(request),
                                   'example_sms': example_sms,
                                   'org_number': get_organization_telephone_number(request)},
                                  context_instance=RequestContext(request))


def _get_subject_form_model(manager, entity_type):
    if is_string(entity_type):
        entity_type = [entity_type]
    return get_form_model_by_entity_type(manager, entity_type)


@valid_web_user
@is_project_exist
@is_datasender
def edit_my_subject_questionnaire(request, project_id, entity_type=None):
    manager = get_database_manager(request.user)
    questionnaire = Project.get(manager, project_id)
    if not entity_type:
        entity_type = questionnaire.entity_type[0]
    project_links = get_project_link(questionnaire, entity_type)
    dashboard_page = settings.HOME_PAGE + "?deleted=true"
    if questionnaire.is_void():
        return HttpResponseRedirect(dashboard_page)
    reg_form = _get_subject_form_model(manager, entity_type)
    if reg_form is None:
        reg_form = form_model.get_form_model_by_code(manager, REGISTRATION_FORM_CODE)
    fields = reg_form.fields
    existing_questions = json.dumps(fields, default=field_to_json)
    subject = get_entity_type_info(entity_type, manager=manager)
    return render_to_response('project/subject_questionnaire.html',
                              {'project': questionnaire,
                               'entity_type': entity_type,
                               'project_links': project_links,
                               'is_quota_reached': is_quota_reached(request),
                               'existing_questions': repr(existing_questions),
                               'questionnaire_code': reg_form.form_code,
                               'language': reg_form.activeLanguages[0],
                               'project_id': questionnaire.id,
                               'subject': subject,
                               'post_url': reverse(subject_save_questionnaire)},
                              context_instance=RequestContext(request))


def append_success_to_context(context, form):
    success = False
    if not len(form.errors):
        success = True
    context.update({'success': success})
    return context


@login_required
@session_not_expired
@is_datasender_allowed
@project_has_web_device
@is_not_expired
@is_project_exist
@is_datasender
def create_data_sender_and_web_user(request, project_id):
    manager = get_database_manager(request.user)
    questionnaire = Project.get(manager, project_id)
    project_links = get_project_link(questionnaire)
    dashboard_page = settings.HOME_PAGE + "?deleted=true"
    if questionnaire.is_void():
        return HttpResponseRedirect(dashboard_page)

    in_trial_mode = _in_trial_mode(request)

    if request.method == 'GET':
        form = ReporterRegistrationForm(initial={'project_id': project_id})
        return render_to_response('project/register_datasender.html', {
            'project': questionnaire,
            'project_links': project_links,
            'is_quota_reached': is_quota_reached(request),
            'form': form,
            'in_trial_mode': in_trial_mode,
            'questionnaire_code': questionnaire.form_code,
            'current_language': translation.get_language()
        }, context_instance=RequestContext(request))

    if request.method == 'POST':
        org_id = request.user.get_profile().org_id
        form = ReporterRegistrationForm(org_id=org_id, data=request.POST)
        reporter_id = None
        try:
            reporter_id, message = process_create_data_sender_form(manager, form, org_id)
        except DataObjectAlreadyExists as e:
            message = _("Data Sender with Unique Identification Number (ID) = %s already exists.") % e.data[1]

        if not len(form.errors) and reporter_id:
            project = questionnaire
            project.associate_data_sender_to_project(manager, reporter_id)
            if form.requires_web_access():
                email_id = request.POST['email']
                create_single_web_user(org_id=org_id, email_address=email_id, reporter_id=reporter_id,
                                       language_code=request.LANGUAGE_CODE)
            UserActivityLog().log(request, action=REGISTERED_DATA_SENDER,
                                  detail=json.dumps(dict({"Unique ID": reporter_id})), project=questionnaire.name)
        if message is not None and reporter_id:
            form = ReporterRegistrationForm(initial={'project_id': form.cleaned_data['project_id']})
        context = {'form': form, 'message': message, 'in_trial_mode': in_trial_mode, 'success': reporter_id is not None}
        return render_to_response('datasender_form.html',
                                  context,
                                  context_instance=RequestContext(request))


def _in_trial_mode(request):
    return utils.get_organization(request).in_trial_mode


@login_required
@session_not_expired
@is_datasender
@is_not_expired
def project_has_data(request, questionnaire_code=None):
    manager = get_database_manager(request.user)
    form_model = get_form_model_by_code(manager, questionnaire_code)
    success, error = submission_stats(manager, form_model.form_code)
    return HttpResponse(encode_json({'has_data': (success + error > 0)}))


@is_project_exist
def edit_my_subject(request, entity_type, entity_id, project_id=None):
    manager = get_database_manager(request.user)
    subject = get_by_short_code(manager, entity_id, [entity_type.lower()])
    subject_request = SubjectWebQuestionnaireRequest(request, project_id, entity_type)
    form_model = subject_request.form_model
    if request.method == 'GET':
        initialize_values(form_model, subject)
        return subject_request.response_for_get_request(is_update=True)
    elif request.method == 'POST':
        return subject_request.post(is_update=True)