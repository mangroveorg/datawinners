import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext as _
import time
from datawinners.accountmanagement.decorators import session_not_expired, is_not_expired
from datawinners.main.database import get_database_manager
from datawinners.project import helper
from datawinners.questionnaire.questionnaire_builder import QuestionnaireBuilder
from datawinners.search.all_datasender_search import get_datasenders_ids_by_questionnaire_names, get_datasender_ids_by_group_names
from datawinners.submission.organization_finder import OrganizationFinder
from datawinners.utils import lowercase_and_strip_accents, get_organization
from mangrove.form_model.project import Project, get_active_form_model_name_and_id


def _is_project_name_unique(error_message, name_has_errors, questionnaire):
    if not questionnaire.is_project_name_unique():
        name_has_errors = True
        error_message["name"] = _("Questionnaire with same name already exists.")
    return name_has_errors

def _associate_data_senders_to_questionnaire(manager, questionnaire, selected_option):
    data_senders_list = []
    if selected_option.get('option') == 'questionnaire_linked':
        questionnaire_names = map(lambda item: lowercase_and_strip_accents(item), selected_option.get('questionnaire_names'))
        data_senders_list = get_datasenders_ids_by_questionnaire_names(manager, questionnaire_names)
        questionnaire.associate_data_sender_to_project(manager, data_senders_list)

    elif selected_option.get('option') == 'group':
        group_names = selected_option.get('group_names')
        data_senders_list = get_datasender_ids_by_group_names(manager, group_names)
        questionnaire.associate_data_sender_to_project(manager, data_senders_list)

    elif selected_option.get('option') == 'broadcast':
        questionnaire.is_open_survey = True



def _create_questionnaire(manager, questionnaire, question):
    question_set = [{'title': question, 'type': 'text', "is_entity_question": False,
                     "code": 'q1', "name": question, 'required': True,
                     "parent_field_code": '',
                     "instruction": "Answer must be a text", 'label': question}]
    QuestionnaireBuilder(questionnaire, manager).update_questionnaire_with_questions(question_set)


def _create_poll(manager, questionnaire, selected_option, question):
    _create_questionnaire(manager, questionnaire, question)
    _associate_data_senders_to_questionnaire(manager, questionnaire, selected_option)
    questionnaire.update_doc_and_save()


def _construct_questionnaire(request):
    from datetime import datetime
    manager = get_database_manager(request.user)
    end_date = datetime.strptime(request.POST.get('end_date'), '%Y-%m-%dT%H:%M:%S')

    questionnaire_code = 'poll_'+str(time.time())
    questionnaire = Project(manager, name=request.POST.get('poll_name'),
                            fields=[], form_code=questionnaire_code, language=request.LANGUAGE_CODE,
                            devices=[u'sms', u'web', u'smartPhone'], is_poll=True, end_date=end_date, active="active")

    return manager, questionnaire


def create_poll_questionnaire(request):
    manager, questionnaire = _construct_questionnaire(request)
    project_name_unique = False
    error_message = {}
    selected_option = json.loads(request.POST['selected_option'])
    question = request.POST.get('question')
    project_name_unique = _is_project_name_unique(error_message, project_name_unique, questionnaire)
    if not project_name_unique:
        _create_poll(manager, questionnaire, selected_option, question)
        return HttpResponse(
            json.dumps({'success': True, 'project_id': questionnaire.id, 'project_code': questionnaire.form_code}))
    return HttpResponse(json.dumps({'success': False,
                                    'error_message': error_message,
                                    'project_name_unique': project_name_unique}))


def _check_if_smsc_is_configured(request):
    organization = get_organization(request)
    organization_setting = OrganizationFinder().find_organization_setting(organization.tel_number())
    smsc = None
    if organization_setting is not None and organization_setting.outgoing_number is not None:
        smsc = organization_setting.outgoing_number.smsc
    return smsc


@login_required
@session_not_expired
@csrf_exempt
@is_not_expired
def create_poll(request):
    if request.method == 'POST':
        smsc = _check_if_smsc_is_configured(request)
        if smsc is None:
            return HttpResponse(json.dumps({'success': False,
                                    'error_message': 'No SMSC configured'}))


        manager = get_database_manager(request.user)
        is_active, project_id, project_name = get_active_form_model_name_and_id(manager)
        if not is_active:
            return create_poll_questionnaire(request)
        else:
            return HttpResponse(json.dumps({'success': False,
                                    'error_message': 'Another poll is active',
                                    'project_name_unique': project_name}))
