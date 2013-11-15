import json
from urllib import unquote
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import translation
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _, get_language, activate
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
import jsonpickle
import unicodedata
from datawinners.accountmanagement.decorators import is_not_expired, session_not_expired
from datawinners.accountmanagement.models import Organization, DataSenderOnTrialAccount
from datawinners.activitylog.models import UserActivityLog
from datawinners.common.constant import IMPORTED_DATA_SENDERS, REMOVED_DATA_SENDER_TO_PROJECTS, EDITED_DATA_SENDER
from datawinners.entity import import_data as import_module, import_data
from datawinners.entity.data_sender import get_user_profile_by_reporter_id
from datawinners.entity.forms import ReporterRegistrationForm
from datawinners.entity.helper import add_imported_data_sender_to_trial_organization, _get_data, update_data_sender_from_trial_organization, rep_id_name_dict_of_superusers
from datawinners.location.LocationTree import get_location_tree, get_location_hierarchy
from datawinners.main.database import get_database_manager
from datawinners.project.models import Project
from datawinners.project.view_models import ReporterEntity
from datawinners.project.views.views import _get_project_and_project_link, _in_trial_mode
from datawinners.search.entity_search import MyDataSenderQuery
from datawinners.submission.location import LocationBridge
from mangrove.datastore.entity import get_by_short_code
from mangrove.errors.MangroveException import MangroveException
from mangrove.form_model.form_model import REPORTER
from mangrove.transport import Request, TransportInfo
from mangrove.transport.player.parser import XlsDatasenderParser
from mangrove.transport.player.player import WebPlayer
from mangrove.utils.types import is_empty
from datawinners.project.utils import is_quota_reached


class MyDataSendersAjaxView(View):

    def strip_accents(self, s):
       return ''.join((c for c in unicodedata.normalize('NFD', unicode(s)) if unicodedata.category(c) != 'Mn'))

    def get(self, request, project_name, *args, **kwargs):
        search_parameters = {}
        search_text = request.GET.get('sSearch', '').strip()
        search_parameters.update({"search_text": search_text})
        search_parameters.update({"start_result_number": int(request.GET.get('iDisplayStart'))})
        search_parameters.update({"number_of_results": int(request.GET.get('iDisplayLength'))})
        search_parameters.update({"order_by": int(request.GET.get('iSortCol_0')) - 1})
        search_parameters.update({"order": "-" if request.GET.get('sSortDir_0') == "desc" else ""})

        user = request.user
        project_name_unquoted = unquote(project_name)
        query_count, search_count, datasenders = MyDataSenderQuery(search_parameters).filtered_query(user, self.strip_accents(project_name_unquoted),
                                                                                    search_parameters)

        return HttpResponse(
            jsonpickle.encode(
                {
                    'data': datasenders,
                    'iTotalDisplayRecords': query_count,
                    'iDisplayStart': int(request.GET.get('iDisplayStart')),
                    "iTotalRecords": search_count,
                    'iDisplayLength': int(request.GET.get('iDisplayLength'))
                }, unpicklable=False), content_type='application/json')

    @method_decorator(login_required)
    @method_decorator(session_not_expired)
    @method_decorator(is_not_expired)
    def dispatch(self, *args, **kwargs):
        return super(MyDataSendersAjaxView, self).dispatch(*args, **kwargs)


def _parse_successful_imports(successful_imports):
    imported_data_senders=[]

    if not successful_imports:
        return imported_data_senders

    for successful_import in successful_imports:
        data_sender={}
        data_sender['email'] = successful_import["email"] if "email" in successful_import else ""
        data_sender['location'] = ",".join(successful_import["l"]) if "l" in successful_import else ""
        data_sender['coordinates'] = ','.join(str(coordinate) for coordinate in successful_import["g"]) if 'g' in successful_import else ""
        data_sender['name']=successful_import['n']
        data_sender['mobile_number']=successful_import['m']
        data_sender['id']=successful_import['s']
        imported_data_senders.append(data_sender)
    return imported_data_senders


def _add_imported_datasenders_to_project(imported_datasenders_id, manager, project):
    project.data_senders.extend(imported_datasenders_id)
    project.save(manager)


def _add_imported_datasenders_to_trail_account(imported_data_senders, org_id):
    imported_datasender_mobile_numbers = [imported_data_sender["mobile_number"] for imported_data_sender in
                                          imported_data_senders]
    DataSenderOnTrialAccount.add_imported_data_sender_to_trial_account(org_id, imported_datasender_mobile_numbers)


@login_required
@csrf_exempt
@is_not_expired
def registered_datasenders(request, project_id):
    manager = get_database_manager(request.user)
    project, project_links = _get_project_and_project_link(manager, project_id)
    if request.method == 'GET':
        in_trial_mode = _in_trial_mode(request)
        user_rep_id_name_dict = rep_id_name_dict_of_superusers(manager)
        return render_to_response('project/registered_datasenders.html',
                                  {   'project': project,
                                      'project_links': project_links,
                                      'current_language': translation.get_language(),
                                      'is_quota_reached':is_quota_reached(request),
                                      'in_trial_mode': in_trial_mode,
                                      'user_dict': json.dumps(user_rep_id_name_dict)},
                                  context_instance=RequestContext(request))
    if request.method == 'POST':
        error_message, failure_imports, success_message, imported_entities, successful_imports = import_module.import_data(request, manager,
                                                                                                                           default_parser=XlsDatasenderParser)
        imported_data_senders = _parse_successful_imports(successful_imports)
        imported_datasenders_ids = [imported_data_sender["id"] for imported_data_sender in imported_data_senders]
        _add_imported_datasenders_to_project(imported_datasenders_ids, manager, project)

        if len(imported_datasenders_ids):
            UserActivityLog().log(request, action=IMPORTED_DATA_SENDERS,
                                  detail=json.dumps(dict({"Unique ID": "[%s]" % ", ".join(imported_datasenders_ids)})),
                                  project=project.name)
        org_id = request.user.get_profile().org_id
        _add_imported_datasenders_to_trail_account(imported_data_senders, org_id)
        return HttpResponse(json.dumps(
            {
                'success': error_message is None and is_empty(failure_imports),
                'message': success_message,
                'error_message': error_message,
                'failure_imports': failure_imports,
                'successful_imports': imported_data_senders
            }))


def edit_data_sender(request, project_id, reporter_id):
    manager = get_database_manager(request.user)
    reporter_entity = ReporterEntity(get_by_short_code(manager, reporter_id, [REPORTER]))
    project, links = _get_project_and_project_link(manager, project_id, reporter_id)
    user_profile = get_user_profile_by_reporter_id(reporter_id, request.user)
    email = user_profile.user.email if user_profile else None

    if request.method == 'GET':
        location = reporter_entity.location
        geo_code = reporter_entity.geo_code
        form = ReporterRegistrationForm(initial={'project_id': project_id, 'name': reporter_entity.name,
                                                 'telephone_number': reporter_entity.mobile_number, 'location': location
            , 'geo_code': geo_code})
        return render_to_response('project/edit_datasender.html',
                                  {'project': project, 'reporter_id': reporter_id, 'form': form, 'project_links': links,
                                   'in_trial_mode': _in_trial_mode(request), 'email': email},
                                  context_instance=RequestContext(request))

    if request.method == 'POST':
        org_id = request.user.get_profile().org_id
        form = ReporterRegistrationForm(org_id=org_id, data=request.POST)

        message = None
        if form.is_valid():
            try:
                organization = Organization.objects.get(org_id=org_id)
                current_telephone_number = reporter_entity.mobile_number
                web_player = WebPlayer(manager,
                                       LocationBridge(location_tree=get_location_tree(),
                                                      get_loc_hierarchy=get_location_hierarchy))
                response = web_player.accept(
                    Request(message=_get_data(form.cleaned_data, organization.country_name(), reporter_id),
                            transportInfo=TransportInfo(transport='web', source='web', destination='mangrove'),
                            is_update=True))
                if response.success:
                    if organization.in_trial_mode:
                        update_data_sender_from_trial_organization(current_telephone_number,
                                                                   form.cleaned_data["telephone_number"], org_id)
                    message = _("Your changes have been saved.")

                    detail_dict = {"Unique ID": reporter_id}
                    current_lang = get_language()
                    activate("en")
                    field_mapping = dict(mobile_number="telephone_number")
                    for field in ["geo_code", "location", "mobile_number", "name"]:
                        if getattr(reporter_entity, field) != form.cleaned_data.get(field_mapping.get(field, field)):
                            label = u"%s" % form.fields[field_mapping.get(field, field)].label
                            detail_dict.update({label: form.cleaned_data.get(field_mapping.get(field, field))})
                    activate(current_lang)
                    if len(detail_dict) > 1:
                        detail_as_string = json.dumps(detail_dict)
                        UserActivityLog().log(request, action=EDITED_DATA_SENDER, detail=detail_as_string,
                                              project=project.name)
                else:
                    form.update_errors(response.errors)
            except MangroveException as exception:
                message = exception.message

        return render_to_response('edit_datasender_form.html',
                                  {'project': project, 'form': form, 'reporter_id': reporter_id, 'message': message,
                                   'project_links': links, 'in_trial_mode': _in_trial_mode(request), 'email': email},
                                  context_instance=RequestContext(request))