import json
from string import lower
from urllib import unquote
import unicodedata

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import translation
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt, csrf_view_exempt, csrf_response_exempt
from django.views.generic.base import View
import jsonpickle

from datawinners import settings
from datawinners.accountmanagement.decorators import is_not_expired, session_not_expired, is_datasender
from datawinners.accountmanagement.helper import create_web_users
from datawinners.activitylog.models import UserActivityLog
from datawinners.common.constant import IMPORTED_DATA_SENDERS
from datawinners.entity import import_data as import_module
from datawinners.entity.datasender_tasks import convert_open_submissions_to_registered_submissions
from datawinners.entity.helper import rep_id_name_dict_of_users
from datawinners.main.database import get_database_manager
from datawinners.project.helper import is_project_exist
from datawinners.project.views.views import get_project_link, _in_trial_mode, _is_pro_sms
from datawinners.search.all_datasender_search import get_data_sender_search_results, \
    get_data_sender_without_search_filters_count, \
    get_data_sender_count
from datawinners.search.datasender_index import update_datasender_index_by_id
from datawinners.search.entity_search import DatasenderQueryResponseCreator
from mangrove.form_model.project import Project
from mangrove.transport.player.parser import XlsDatasenderParser
from mangrove.utils.types import is_empty
from datawinners.project.utils import is_quota_reached


class MyDataSendersAjaxView(View):
    def strip_accents(self, s):
        return ''.join((c for c in unicodedata.normalize('NFD', unicode(s)) if unicodedata.category(c) != 'Mn'))

    def post(self, request, project_name, *args, **kwargs):
        user = request.user
        manager = get_database_manager(user)
        project_name_unquoted = lower(unquote(project_name))

        search_parameters = {}
        search_filters = {}
        search_text = lower(request.POST.get('sSearch', '').strip())
        search_filters.update({"search_text": search_text})
        search_parameters.update({"start_result_number": int(request.POST.get('iDisplayStart'))})
        search_parameters.update({"number_of_results": int(request.POST.get('iDisplayLength'))})
        search_parameters.update({"order_by": int(request.POST.get('iSortCol_0')) - 1})
        search_parameters.update({"order": "-" if request.POST.get('sSortDir_0') == "desc" else ""})
        search_filters.update({"project_name": project_name_unquoted})
        search_parameters.update({"search_filters": search_filters})

        query_fields, search_results = get_data_sender_search_results(manager, search_parameters)
        total_count = get_data_sender_without_search_filters_count(manager, search_parameters)
        filtered_count = get_data_sender_count(manager, search_parameters)
        query_fields.remove('projects')
        datasenders = DatasenderQueryResponseCreator().create_response(search_results, show_projects=False)

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
        return super(MyDataSendersAjaxView, self).dispatch(*args, **kwargs)


def parse_successful_imports(successful_imports):
    imported_data_senders = []

    if not successful_imports:
        return imported_data_senders

    for successful_import in successful_imports.values():
        data_sender = {}
        data_sender['email'] = successful_import["email"] if "email" in successful_import else ""
        data_sender['location'] = ",".join(successful_import["l"]) if "l" in successful_import else ""
        data_sender['coordinates'] = ','.join(
            str(coordinate) for coordinate in successful_import["g"]) if successful_imports.get('g') else ""
        data_sender['name'] = successful_import['n'] if 'n' in successful_import else ""
        data_sender['mobile_number'] = successful_import['m']
        data_sender['id'] = successful_import['s']
        imported_data_senders.append(data_sender)
    return imported_data_senders


def _add_imported_datasenders_to_project(imported_datasenders_id, manager, project):
    project.data_senders.extend(imported_datasenders_id)
    project.save(process_post_update=False)
    for datasender_id in imported_datasenders_id:
        update_datasender_index_by_id(datasender_id, manager)


@login_required
@csrf_exempt
@is_not_expired
@is_project_exist
@is_datasender
def registered_datasenders(request, project_id):
    manager = get_database_manager(request.user)
    questionnaire = Project.get(manager, project_id)
    project_links = get_project_link(questionnaire)
    dashboard_page = settings.HOME_PAGE + "?deleted=true"
    if questionnaire.is_void():
        return HttpResponseRedirect(dashboard_page)
    if request.method == 'GET':
        in_trial_mode = _in_trial_mode(request)
        is_open_survey_allowed = _is_pro_sms(request) and not questionnaire.xform
        is_open_survey = 'open' if questionnaire.is_open_survey else 'restricted'
        user_rep_id_name_dict = rep_id_name_dict_of_users(manager)
        return render_to_response('project/registered_datasenders.html',
                                  {'project': questionnaire,
                                   'project_links': project_links,
                                   'questionnaire_code': questionnaire.form_code,
                                   'current_language': translation.get_language(),
                                   'is_quota_reached': is_quota_reached(request),
                                   'in_trial_mode': in_trial_mode,
                                   'is_open_survey_allowed': is_open_survey_allowed,
                                   'is_open_survey': is_open_survey,
                                   'user_dict': json.dumps(user_rep_id_name_dict)},
                                  context_instance=RequestContext(request))
    if request.method == 'POST':
        error_message, failure_imports, success_message, successful_imports = import_module.import_data(request,
                                                                                                        manager,
                                                                                                        default_parser=XlsDatasenderParser,
                                                                                                        is_datasender=True)
        imported_data_senders = parse_successful_imports(successful_imports)

        reporter_id_email_map = dict(
            [(imported_datasender['id'], imported_datasender['email']) for imported_datasender in
             imported_data_senders])
        org_id = request.user.get_profile().org_id
        create_web_users(org_id, reporter_id_email_map, request.LANGUAGE_CODE)

        imported_datasenders_ids = [imported_data_sender["id"] for imported_data_sender in imported_data_senders]
        _add_imported_datasenders_to_project(imported_datasenders_ids, manager, questionnaire)
        convert_open_submissions_to_registered_submissions.delay(manager.database_name, imported_datasenders_ids)

        if len(imported_datasenders_ids):
            UserActivityLog().log(request, action=IMPORTED_DATA_SENDERS,
                                  detail=json.dumps(dict({"Unique ID": "[%s]" % ", ".join(imported_datasenders_ids)})),
                                  project=questionnaire.name)
        return HttpResponse(json.dumps(
            {
                'success': error_message is None and is_empty(failure_imports),
                'message': success_message,
                'error_message': error_message,
                'failure_imports': failure_imports,
                'successful_imports': imported_data_senders
            }))

