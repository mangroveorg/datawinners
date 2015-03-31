import json
from sets import Set

from django.contrib.auth.decorators import login_required
from django.template.context import RequestContext
from django.utils import translation
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_view_exempt, csrf_response_exempt
from django.utils.translation import ugettext as _
from django.views.generic.base import TemplateView, View
import jsonpickle

from datawinners.accountmanagement.helper import create_web_users, get_org_id
from datawinners.entity.datasender_tasks import convert_open_submissions_to_registered_submissions
from datawinners.entity.group_helper import get_group_details
from datawinners.project.couch_view_helper import get_project_id_name_map
from datawinners.search.all_datasender_search import get_data_sender_search_results, get_data_sender_count, \
    get_data_sender_without_search_filters_count, get_all_datasenders_short_codes, get_query_fields
from datawinners.search.datasender_index import update_datasender_index_by_id
from mangrove.datastore.entity import contact_by_short_code
from mangrove.form_model.field import field_to_json
from mangrove.transport import TransportInfo
from datawinners import settings
from datawinners import utils
from datawinners.accountmanagement.decorators import is_datasender, session_not_expired, is_not_expired, is_new_user
from datawinners.entity.views import log_activity, get_success_message
from datawinners.main.database import get_database_manager
from datawinners.entity.helper import delete_entity_instance, delete_datasender_users_if_any, \
    delete_datasender_for_trial_mode, rep_id_name_dict_of_users
from datawinners.project.models import delete_datasenders_from_project
from datawinners.entity import import_data as import_module
from datawinners.project.views.datasenders import parse_successful_imports
from datawinners.search.entity_search import DatasenderQueryResponseCreator
from mangrove.form_model.project import Project
from mangrove.utils.types import is_empty
from datawinners.utils import get_organization
from mangrove.transport.player.parser import XlsDatasenderParser
from datawinners.activitylog.models import UserActivityLog
from datawinners.common.constant import IMPORTED_DATA_SENDERS, ADDED_DATA_SENDERS_TO_QUESTIONNAIRES, \
    REMOVED_DATA_SENDER_TO_QUESTIONNAIRES, DELETED_DATA_SENDERS
from mangrove.transport.player.parser import XlsxDataSenderParser


class AllDataSendersView(TemplateView):
    template_name = 'entity/all_datasenders.html'

    def get(self, request, *args, **kwargs):
        manager = get_database_manager(request.user)
        project_name_id_map = get_project_id_name_map(manager)
        organization = utils.get_organization(request)
        in_trial_mode = organization.in_trial_mode
        is_pro_sms = organization.is_pro_sms
        user_rep_id_name_dict = rep_id_name_dict_of_users(manager)
        groups = get_group_details(manager)

        return self.render_to_response(RequestContext(request, {
            "user_dict": json.dumps(user_rep_id_name_dict),
            "projects": project_name_id_map,
            'current_language': translation.get_language(),
            'in_trial_mode': in_trial_mode,
            'is_pro_sms': is_pro_sms,
            'groups': repr(json.dumps(groups, default=field_to_json))
        }))

    def get_imported_data_senders(self, successful_imports):
        imported_data_senders = successful_imports.values()
        for imported_data_sender in imported_data_senders:
            imported_data_sender.remove(["reporter"])
        return imported_data_senders

    def update_activity_log(self, request, successful_imports):

        if successful_imports is None or len(successful_imports) == 0:
            return

        imported_datasenders_ids = successful_imports.keys()
        if len(imported_datasenders_ids):
            UserActivityLog().log(request, action=IMPORTED_DATA_SENDERS,
                                  detail=json.dumps(
                                      dict({"Unique ID": "[%s]" % ", ".join(imported_datasenders_ids)})))

    def _convert_anonymous_submissions_to_registered(self, imported_data_senders, manager):
        imported_datasenders_ids = [imported_data_sender["id"] for imported_data_sender in imported_data_senders]
        convert_open_submissions_to_registered_submissions.delay(manager.database_name, imported_datasenders_ids)

    def post(self, request, *args, **kwargs):
        parser_dict = {'.xls': XlsDatasenderParser, '.xlsx': XlsxDataSenderParser}
        manager = get_database_manager(request.user)
        import os
        file_extension = os.path.splitext(request.GET["qqfile"])[1]
        parser = parser_dict.get(file_extension, None)
        error_message, failure_imports, success_message, successful_imports = import_module.import_data(
            request, manager, default_parser=parser)

        imported_data_senders = parse_successful_imports(successful_imports)
        self._convert_anonymous_submissions_to_registered(imported_data_senders, manager)

        self.update_activity_log(request, successful_imports)

        return HttpResponse(json.dumps(
            {
                'success': error_message is None and is_empty(failure_imports),
                'message': success_message,
                'error_message': error_message,
                'failure_imports': failure_imports,
                'successful_imports': imported_data_senders
            }))

    @method_decorator(csrf_view_exempt)
    @method_decorator(csrf_response_exempt)
    @method_decorator(login_required)
    @method_decorator(session_not_expired)
    @method_decorator(is_datasender)
    @method_decorator(is_not_expired)
    def dispatch(self, *args, **kwargs):
        return super(AllDataSendersView, self).dispatch(*args, **kwargs)


class AllDataSendersAjaxView(View):
    def _get_order_field(self, post_dict, dbm):
        order_by = int(post_dict.get('iSortCol_0')) - 1
        headers = get_query_fields(dbm)
        return headers[order_by]

    def post(self, request, *args, **kwargs):
        user = request.user
        manager = get_database_manager(user)
        search_parameters = {}
        search_filters = json.loads(request.POST.get('search_filters', ''))
        search_text = request.POST.get('sSearch', '').strip()
        search_filters.update({"search_text": search_text})
        search_parameters.update({"start_result_number": int(request.POST.get('iDisplayStart'))})
        search_parameters.update({"number_of_results": int(request.POST.get('iDisplayLength'))})
        search_parameters.update({"sort_field": self._get_order_field(request.POST, manager)})
        search_parameters.update({"search_filters": search_filters})
        search_parameters.update({"order": "-" if request.POST.get('sSortDir_0') == "desc" else ""})

        query_fields, datasenders = get_data_sender_search_results(manager, search_parameters)
        total_count = get_data_sender_without_search_filters_count(manager, search_parameters)
        filtered_count = get_data_sender_count(manager, search_parameters)
        datasenders = DatasenderQueryResponseCreator().create_response(query_fields, datasenders)

        return HttpResponse(
            jsonpickle.encode(
                {
                    'data': datasenders,
                    'iTotalDisplayRecords': filtered_count,
                    'iDisplayStart': int(request.POST.get('iDisplayStart')),
                    "iTotalRecords": total_count,
                    'iDisplayLength': int(request.POST.get('iDisplayLength'))
                }, unpicklable=False), content_type='application/json')

    @method_decorator(csrf_view_exempt)
    @method_decorator(csrf_response_exempt)
    @method_decorator(login_required)
    @method_decorator(session_not_expired)
    @method_decorator(is_not_expired)
    def dispatch(self, *args, **kwargs):
        return super(AllDataSendersAjaxView, self).dispatch(*args, **kwargs)


class DataSenderActionView(View):
    def _get_projects(self, manager, request):
        project_ids = request.POST.get('project_id').split(';')
        questionnaires = []
        for project_id in project_ids:
            questionnaire = Project.get(manager, project_id)
            if questionnaire is not None:
                questionnaires.append(questionnaire)
        return questionnaires

    @method_decorator(login_required)
    @method_decorator(session_not_expired)
    @method_decorator(is_not_expired)
    @method_decorator(is_new_user)
    @method_decorator(is_datasender)
    def dispatch(self, *args, **kwargs):
        return super(DataSenderActionView, self).dispatch(*args, **kwargs)


def data_sender_short_codes(request, manager):
    if request.POST.get("all_selected") == 'true':
        search_parameters = {'search_text': request.POST.get('search_query'),
                             'project_name': request.POST.get("project_name", None)}
        return get_all_datasenders_short_codes(manager, search_parameters)

    return request.POST['ids'].lower().split(';')


class AssociateDataSendersView(DataSenderActionView):
    def _update_activity_log(self, projects_name, request):
        ids = request.POST["ids"].split(';')
        if len(ids):
            UserActivityLog().log(request, action=ADDED_DATA_SENDERS_TO_QUESTIONNAIRES,
                                  detail=json.dumps({"Unique ID": "[%s]" % ", ".join(ids),
                                                     "Projects": "[%s]" % ", ".join(projects_name)}))

    def _convert_contacts_to_datasenders(self, contact_short_codes, manager, request):
        datasender_id_email_map = {}
        for contact_short_code in contact_short_codes:
            datasender = contact_by_short_code(manager, contact_short_code)
            if datasender.is_contact:
                datasender.change_status_to_datasender()
                datasender.save(process_post_update=False)
                if datasender.email:
                    datasender_id_email_map.update({datasender.short_code: datasender.email})
            update_datasender_index_by_id(contact_short_code, manager)
        org_id = get_org_id(request)
        create_web_users(org_id, datasender_id_email_map, request.LANGUAGE_CODE)

    def post(self, request, *args, **kwargs):
        manager = get_database_manager(request.user)
        questionnaires = self._get_projects(manager, request)
        projects_name = Set()
        for questionnaire in questionnaires:
            datasenders_to_associate = data_sender_short_codes(request, manager)
            questionnaire.associate_data_sender_to_project(manager, datasenders_to_associate)
            self._convert_contacts_to_datasenders(datasenders_to_associate, manager, request)
            projects_name.add(questionnaire.name.capitalize())
        self._update_activity_log(projects_name, request)

        return HttpResponse(
            json.dumps({"success": True, "message": _("Your contact(s) have been added as Data Sender. Contacts with an Email address who are added to a Questionnaire for the first time will receive an activation email with instructions.")}))


class DisassociateDataSendersView(DataSenderActionView):
    def post(self, request, *args, **kwargs):
        manager = get_database_manager(request.user)
        questionnaires = self._get_projects(manager, request)
        projects_name = Set()
        removed_rep_ids = Set()
        selected_rep_ids = data_sender_short_codes(request, manager)

        for questionnaire in questionnaires:
            dashboard_page = settings.HOME_PAGE + "?deleted=true"
            if questionnaire.is_void():
                return HttpResponseRedirect(dashboard_page)
            for rep_id in selected_rep_ids:
                if rep_id in questionnaire.data_senders:
                    questionnaire.delete_datasender(manager, rep_id)
                    update_datasender_index_by_id(rep_id, manager)

                    projects_name.add(questionnaire.name.capitalize())
                    removed_rep_ids.add(rep_id)

        if len(removed_rep_ids):
            UserActivityLog().log(request, action=REMOVED_DATA_SENDER_TO_QUESTIONNAIRES,
                                  detail=json.dumps({"Unique ID": "[%s]" % ", ".join(removed_rep_ids),
                                                     "Projects": "[%s]" % ", ".join(projects_name)}))

        return HttpResponse(
            json.dumps({"success": True, "message": _("The Data Sender(s) are removed from Questionnaire(s) successfully")}))


@csrf_view_exempt
@csrf_response_exempt
@login_required
@is_datasender
def delete_data_senders(request):
    manager = get_database_manager(request.user)
    organization = get_organization(request)
    entity_type = request.POST['entity_type']
    all_ids = data_sender_short_codes(request, manager)
    superusers = rep_id_name_dict_of_users(manager)
    non_superuser_rep_ids = [id for id in all_ids if id not in superusers.keys()]
    transport_info = TransportInfo("web", request.user.username, "")

    delete_datasenders_from_project(manager, non_superuser_rep_ids)
    delete_entity_instance(manager, non_superuser_rep_ids, entity_type, transport_info)
    delete_datasender_users_if_any(non_superuser_rep_ids, organization)
    if organization.in_trial_mode:
        delete_datasender_for_trial_mode(manager, non_superuser_rep_ids, entity_type)
    log_activity(request, DELETED_DATA_SENDERS,
                 "%s: [%s]" % (entity_type.capitalize(), ", ".join(non_superuser_rep_ids)), )
    messages = get_success_message(entity_type)
    return HttpResponse(json.dumps({'success': True, 'message': messages}))


class UsersInSearchedDataSender(View):
    def post(self, request, *args, **kwargs):
        manager = get_database_manager(request.user)
        selected_rep_ids = data_sender_short_codes(request, manager)
        users = rep_id_name_dict_of_users(manager)
        users_selected = []

        non_superuser_selected = []
        for rep_id in selected_rep_ids:
            if rep_id in users.keys():
                users_selected.append(users[rep_id])
            else:
                non_superuser_selected.append(rep_id)

        return HttpResponse(json.dumps({"success": True, "superusers_selected": users_selected}))

    @method_decorator(csrf_view_exempt)
    @method_decorator(csrf_response_exempt)
    @method_decorator(login_required)
    @method_decorator(session_not_expired)
    @method_decorator(is_not_expired)
    def dispatch(self, *args, **kwargs):
        return super(UsersInSearchedDataSender, self).dispatch(*args, **kwargs)

