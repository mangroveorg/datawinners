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
from datawinners.entity.datasender_tasks import convert_open_submissions_to_registered_submissions
from mangrove.transport import TransportInfo

from datawinners import settings
from datawinners import utils
from datawinners.accountmanagement.decorators import is_datasender, session_not_expired, is_not_expired, is_new_user
from datawinners.entity.views import log_activity, get_success_message
from datawinners.main.database import get_database_manager
from datawinners.entity.helper import delete_entity_instance, delete_datasender_users_if_any, \
    delete_datasender_for_trial_mode, rep_id_name_dict_of_users
from datawinners.project.models import get_all_projects, delete_datasenders_from_project
from datawinners.entity import import_data as import_module
from datawinners.project.views.datasenders import parse_successful_imports
from datawinners.search.entity_search import DatasenderQuery, MyDataSenderQuery
from mangrove.form_model.form_model import REPORTER, header_fields, get_form_model_by_code
from mangrove.form_model.project import Project
from mangrove.utils.types import is_empty
from datawinners.utils import get_organization
from mangrove.transport.player.parser import XlsDatasenderParser
from datawinners.activitylog.models import UserActivityLog
from datawinners.common.constant import IMPORTED_DATA_SENDERS, ADDED_DATA_SENDERS_TO_QUESTIONNAIRES, \
    REMOVED_DATA_SENDER_TO_QUESTIONNAIRES, DELETED_DATA_SENDERS


class AllDataSendersView(TemplateView):
    template_name = 'entity/all_datasenders.html'

    def get(self, request, *args, **kwargs):
        manager = get_database_manager(request.user)
        projects = get_all_projects(manager)
        in_trial_mode = utils.get_organization(request).in_trial_mode
        user_rep_id_name_dict = rep_id_name_dict_of_users(manager)

        return self.render_to_response(RequestContext(request, {
            "user_dict": json.dumps(user_rep_id_name_dict),
            "projects": projects,
            'current_language': translation.get_language(),
            'in_trial_mode': in_trial_mode,
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
        manager = get_database_manager(request.user)
        error_message, failure_imports, success_message, successful_imports = import_module.import_data(
            request,
            manager,
            default_parser=XlsDatasenderParser)

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
    def _get_order_field(self, post_dict, user):
        order_by = int(post_dict.get('iSortCol_0')) - 1
        headers = DatasenderQuery().get_headers(user)
        return headers[order_by]

    def post(self, request, *args, **kwargs):
        user = request.user
        search_parameters = {}
        search_text = request.POST.get('sSearch', '').strip()
        search_parameters.update({"search_text": search_text})
        search_parameters.update({"start_result_number": int(request.POST.get('iDisplayStart'))})
        search_parameters.update({"number_of_results": int(request.POST.get('iDisplayLength'))})
        search_parameters.update({"sort_field": self._get_order_field(request.POST, user)})
        #search_parameters.update({"order_by": int(request.POST.get('iSortCol_0')) - 1})
        search_parameters.update({"order": "-" if request.POST.get('sSortDir_0') == "desc" else ""})

        query_count, search_count, datasenders = DatasenderQuery(search_parameters).paginated_query(user, REPORTER)

        return HttpResponse(
            jsonpickle.encode(
                {
                    'data': datasenders,
                    'iTotalDisplayRecords': query_count,
                    'iDisplayStart': int(request.POST.get('iDisplayStart')),
                    "iTotalRecords": search_count,
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
        search_text = request.POST.get('search_query')
        datasender_list = []
        project_name = request.POST.get("project_name", None)
        if project_name:
            datasender_list = MyDataSenderQuery().query_by_project_name(request.user, project_name, search_text)
        else:
            datasender_list = DatasenderQuery().query(request.user, search_text)
        form_model = get_form_model_by_code(manager, 'reg')
        fields = header_fields(form_model).keys()
        fields.remove("entity_type")
        short_code_index = fields.index("short_code")
        return [ds[short_code_index].lower() for ds in datasender_list]

    return request.POST['ids'].lower().split(';')


class AssociateDataSendersView(DataSenderActionView):
    def post(self, request, *args, **kwargs):
        manager = get_database_manager(request.user)
        questionnaires = self._get_projects(manager, request)
        projects_name = Set()
        for questionnaire in questionnaires:
            questionnaire.associate_data_sender_to_project(manager, data_sender_short_codes(request, manager))
            projects_name.add(questionnaire.name.capitalize())
        ids = request.POST["ids"].split(';')
        if len(ids):
            UserActivityLog().log(request, action=ADDED_DATA_SENDERS_TO_QUESTIONNAIRES,
                                  detail=json.dumps({"Unique ID": "[%s]" % ", ".join(ids),
                                                     "Projects": "[%s]" % ", ".join(projects_name)}))

        return HttpResponse(
            json.dumps({"success": True, "message": _("The Data Sender(s) are added to Questionnaire(s) successfully")}))


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

