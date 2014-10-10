import json
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _, ugettext
from django.views.decorators.csrf import csrf_exempt
from datawinners.accountmanagement.decorators import session_not_expired, is_not_expired
from datawinners.accountmanagement.models import NGOUserProfile
from datawinners.activitylog.models import UserActivityLog
from datawinners.common.constant import CREATED_QUESTIONNAIRE
from datawinners.main.database import get_database_manager
from datawinners.project import helper
from datawinners.project.helper import associate_account_users_to_project
from datawinners.project.wizard_view import get_preview_and_instruction_links, create_questionnaire
from datawinners.utils import get_organization
from mangrove.datastore.entity_type import get_unique_id_types
from mangrove.errors.MangroveException import QuestionCodeAlreadyExistsException, QuestionAlreadyExistsException, EntityQuestionAlreadyExistsException


@login_required
@session_not_expired
@csrf_exempt
@is_not_expired
def create_project(request):
    manager = get_database_manager(request.user)
    if request.method == 'GET':
        cancel_link = reverse('dashboard') if request.GET.get('prev', None) == 'dash' else reverse('alldata_index')
        return render_to_response('project/create_project.html',
                                  {'preview_links': get_preview_and_instruction_links(),
                                   'questionnaire_code': helper.generate_questionnaire_code(manager),
                                   'is_edit': 'false',
                                   'active_language': request.LANGUAGE_CODE,
                                   'post_url': reverse(create_project),
                                   'unique_id_types': json.dumps([unique_id_type.capitalize() for unique_id_type in
                                                                  get_unique_id_types(manager)]),
                                   'cancel_link': cancel_link}, context_instance=RequestContext(request))

    if request.method == 'POST':
        response_dict = _create_project_post_response(request, manager)
        return HttpResponse(json.dumps(response_dict))


def _validate_questionnaire_name_and_code(questionnaire):
    code_has_errors, name_has_errors = False, False
    error_message = {}
    if not questionnaire.is_form_code_unique():
        code_has_errors = True
        error_message["code"] = _("Questionnaire with same code already exists.")
    if not questionnaire.is_project_name_unique():
        name_has_errors = True
        error_message["name"] = _("Questionnaire with same name already exists.")
    return code_has_errors, error_message, name_has_errors


def _is_open_survey_allowed(request, is_open_survey):
    return get_organization(request).is_pro_sms and is_open_survey


def _create_project_post_response(request, manager):
    project_info = json.loads(request.POST['profile_form'])
    try:
        ngo_admin = NGOUserProfile.objects.get(user=request.user)
        is_open_survey_allowed = _is_open_survey_allowed(request, request.POST.get('is_open_survey'))
        questionnaire = create_questionnaire(post=request.POST, manager=manager, name=project_info.get('name'),
                                             language=project_info.get('language', request.LANGUAGE_CODE),
                                             reporter_id=ngo_admin.reporter_id,
                                             is_open_survey=is_open_survey_allowed)
    except (QuestionCodeAlreadyExistsException, QuestionAlreadyExistsException,
            EntityQuestionAlreadyExistsException) as ex:
        return {'success': False, 'error_message': _(ex.message), 'error_in_project_section': False}

    code_has_errors, error_message, name_has_errors = _validate_questionnaire_name_and_code(questionnaire)

    if not code_has_errors and not name_has_errors:
        associate_account_users_to_project(manager, questionnaire)
        questionnaire.update_doc_and_save()
        UserActivityLog().log(request, action=CREATED_QUESTIONNAIRE, project=questionnaire.name,
                              detail=questionnaire.name)
        return {'success': True, 'project_id': questionnaire.id}

    return {'success': False,
            'error_message': error_message,
            'error_in_project_section': False,
            'code_has_errors': code_has_errors,
            'name_has_errors': name_has_errors}