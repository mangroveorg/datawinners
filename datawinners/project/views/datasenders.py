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
from datawinners.activitylog.models import UserActivityLog
from datawinners.common.constant import IMPORTED_DATA_SENDERS
from datawinners.entity import import_data as import_module
from datawinners.entity.helper import rep_id_name_dict_of_users
from datawinners.main.database import get_database_manager
from datawinners.project.helper import is_project_exist
from datawinners.project.views.views import get_project_link, _in_trial_mode, _is_pro_sms
from datawinners.search.datasender_index import update_datasender_index_by_id
from datawinners.search.entity_search import MyDataSenderQuery
from mangrove.form_model.project import Project
from mangrove.transport.player.parser import XlsDatasenderParser
from mangrove.utils.types import is_empty
from datawinners.project.utils import is_quota_reached


class MyDataSendersAjaxView(View):
    def strip_accents(self, s):
        return ''.join((c for c in unicodedata.normalize('NFD', unicode(s)) if unicodedata.category(c) != 'Mn'))

    def post(self, request, project_name, *args, **kwargs):
        search_parameters = {}
        search_text = lower(request.POST.get('sSearch', '').strip())
        search_parameters.update({"search_text": search_text})
        search_parameters.update({"start_result_number": int(request.POST.get('iDisplayStart'))})
        search_parameters.update({"number_of_results": int(request.POST.get('iDisplayLength'))})
        search_parameters.update({"order_by": int(request.POST.get('iSortCol_0')) - 1})
        search_parameters.update({"order": "-" if request.POST.get('sSortDir_0') == "desc" else ""})

        user = request.user
        project_name_unquoted = lower(unquote(project_name))
        query_count, search_count, datasenders = MyDataSenderQuery(search_parameters).filtered_query(user,
                                                                                                     self.strip_accents(
                                                                                                         project_name_unquoted),
                                                                                                     search_parameters)

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
            str(coordinate) for coordinate in successful_import["g"]) if 'g' in successful_import else ""
        data_sender['name'] = successful_import['n']
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
                                                                                                        default_parser=XlsDatasenderParser)
        imported_data_senders = parse_successful_imports(successful_imports)
        imported_datasenders_ids = [imported_data_sender["id"] for imported_data_sender in imported_data_senders]
        _add_imported_datasenders_to_project(imported_datasenders_ids, manager, questionnaire)

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

