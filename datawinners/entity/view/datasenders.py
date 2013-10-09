import json
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import translation
from django.utils.translation import ugettext as _, ugettext
from django.views.decorators.csrf import csrf_view_exempt, csrf_response_exempt
import jsonpickle
from datawinners import utils
from datawinners.accountmanagement.decorators import session_not_expired, is_datasender, is_not_expired, is_new_user
from datawinners.activitylog.models import UserActivityLog
from datawinners.common.constant import IMPORTED_DATA_SENDERS, REMOVED_DATA_SENDER_TO_PROJECTS, ADDED_DATA_SENDERS_TO_PROJECTS
from datawinners.entity import import_data as import_module
from datawinners.entity.helper import add_imported_data_sender_to_trial_organization
from datawinners.entity.views import _get_all_datasenders
from datawinners.main.database import get_database_manager
from datawinners.project.models import get_all_projects, Project
from datawinners.search.entity_search import DatasenderQuery
from mangrove.form_model.form_model import REPORTER
from mangrove.transport.player.parser import XlsDatasenderParser
from mangrove.utils.types import is_empty

@csrf_view_exempt
@csrf_response_exempt
@login_required(login_url='/login')
@session_not_expired
@is_datasender
@is_not_expired
def all_datasenders_get(request):
    manager = get_database_manager(request.user)
    projects = get_all_projects(manager)
    in_trial_mode = utils.get_organization(request).in_trial_mode
    labels = [_("Name"), _("Unique ID"), _("Location"), _("GPS Coordinates"), _("Mobile Number"), _("Email address")]
    grant_web_access = False
    if int(request.GET.get('web', '0')):
        grant_web_access = True

    return render_to_response('entity/all_datasenders.html',
                              {'grant_web_access': grant_web_access,
                               "labels": labels,
                               "projects": projects,
                               'current_language': translation.get_language(),
                               'in_trial_mode': in_trial_mode
                              },
                              context_instance=RequestContext(request))


@csrf_view_exempt
@csrf_response_exempt
@login_required(login_url='/login')
@session_not_expired
@is_datasender
@is_not_expired
def all_datasenders_post(request):
    manager = get_database_manager(request.user)
    projects = get_all_projects(manager)
    error_message, failure_imports, success_message, imported_datasenders = import_module.import_data(request,
                                                                                                          manager,
                                                                                                          default_parser=XlsDatasenderParser)
    if len(imported_datasenders.keys()):
        UserActivityLog().log(request, action=IMPORTED_DATA_SENDERS,
                              detail=json.dumps(
                                  dict({"Unique ID": "[%s]" % ", ".join(imported_datasenders.keys())})))
    all_data_senders = _get_all_datasenders(manager, projects, request.user)
    mobile_number_index = 4
    add_imported_data_sender_to_trial_organization(request, imported_datasenders,
                                                       all_data_senders=all_data_senders, index=mobile_number_index)

    return HttpResponse(json.dumps(
            {'success': error_message is None and is_empty(failure_imports),
             'message': success_message,
             'error_message': error_message,
             'failure_imports': failure_imports,
             'all_data': all_data_senders,
             'imported_datasenders': imported_datasenders
            }))


@csrf_view_exempt
@csrf_response_exempt
@login_required(login_url='/login')
@session_not_expired
@is_new_user
@is_not_expired
def disassociate_datasenders(request):
    manager = get_database_manager(request.user)
    projects = _get_projects(manager, request)
    projects_name = []
    for project in projects:
        [project.delete_datasender(manager, id) for id in request.POST['ids'].split(';') if id in project.data_senders]
        project.save(manager)
        projects_name.append(project.name.capitalize())
    ids = request.POST["ids"].split(";")
    if len(ids):
        UserActivityLog().log(request, action=REMOVED_DATA_SENDER_TO_PROJECTS,
                              detail=json.dumps({"Unique ID": "[%s]" % ", ".join(ids),
                                                 "Projects": "[%s]" % ", ".join(projects_name)}))
    return HttpResponse(reverse("all_datasenders"))


def all_datasenders_ajax(request):
    search_parameters = {}
    search_text = request.GET.get('sSearch', '').strip()
    search_parameters.update({"search_text": search_text})
    search_parameters.update({"start_result_number": int(request.GET.get('iDisplayStart'))})
    search_parameters.update({"number_of_results": int(request.GET.get('iDisplayLength'))})
    search_parameters.update({"order_by": int(request.GET.get('iSortCol_0')) - 1})
    search_parameters.update({"order": "-" if request.GET.get('sSortDir_0') == "desc" else ""})

    user = request.user
    query_count, search_count, datasenders = DatasenderQuery().paginated_query(user, REPORTER, search_parameters)

    return HttpResponse(
        jsonpickle.encode(
            {
                'datasenders': datasenders,
                'iTotalDisplayRecords': query_count,
                'iDisplayStart': int(request.GET.get('iDisplayStart')),
                "iTotalRecords": search_count,
                'iDisplayLength': int(request.GET.get('iDisplayLength'))
            }, unpicklable=False), content_type='application/json')


@csrf_view_exempt
@csrf_response_exempt
@login_required(login_url='/login')
@session_not_expired
@is_new_user
@is_not_expired
def associate_datasenders(request):
    manager = get_database_manager(request.user)
    projects = _get_projects(manager, request)
    projects_name = []
    for project in projects:
        project.data_senders.extend([id for id in request.POST['ids'].split(';') if not id in project.data_senders])
        projects_name.append(project.name.capitalize())
        project.save(manager)
    ids = request.POST["ids"].split(';')
    if len(ids):
        UserActivityLog().log(request, action=ADDED_DATA_SENDERS_TO_PROJECTS,
                              detail=json.dumps({"Unique ID": "[%s]" % ", ".join(ids),
                                                 "Projects": "[%s]" % ", ".join(projects_name)}))
    return HttpResponse(reverse("all_datasenders"))


def _get_projects(manager, request):
    project_ids = request.POST.get('project_id').split(';')
    projects = []
    for project_id in project_ids:
        project = Project.load(manager.database, project_id)
        if project is not None:
            projects.append(project)
    return projects