import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from datawinners.accountmanagement.decorators import session_not_expired, is_not_expired
from datawinners.main.database import get_database_manager
from datawinners.project import helper
from datawinners.project.helper import associate_account_users_to_project
from datawinners.project.views.create_questionnaire import validate_questionnaire_name_and_code
from datawinners.questionnaire.questionnaire_builder import QuestionnaireBuilder
from datawinners.search.all_datasender_search import get_all_datasenders_short_codes
from mangrove.form_model.project import Project
from django.utils.translation import ugettext as _


def _is_project_name_unique(error_message, name_has_errors, questionnaire):
    if not questionnaire.is_project_name_unique():
        name_has_errors = True
        error_message["name"] = _("Questionnaire with same name already exists.")
    return name_has_errors


def get_datasenders_ids(manager, questionnaire_names):
    datasender_ids = []
    for questionnaire_name in questionnaire_names:
        search_parameters = {'response_fields': 'short_code',
                             'project_name': questionnaire_name}

        datasender_ids.extend(get_all_datasenders_short_codes(manager, search_parameters))
    return set(datasender_ids)


def get_datasender_ids_by_group_name(manger, group_names):
    data_sender_ids = []
    for group_name in group_names:
        search_parameters = {'search_filters': {'group_name': group_name}}
        data_sender_ids = get_all_datasenders_short_codes(manger, search_parameters)

    return set(data_sender_ids)


def _associate_data_senders_to_questionnaire(data_senders_list, manager, questionnaire, selected_option):
    if selected_option.get('option') == 'questionnaire_linked':
        questionnaire_names = selected_option.get('questionnaire_names')
        data_senders_list = get_datasenders_ids(manager, questionnaire_names)

    elif selected_option.get('option') == 'group':
        group_names = selected_option.get('group_names')
        data_senders_list = get_datasender_ids_by_group_name(manager, group_names)
    questionnaire.associate_data_sender_to_project(manager, data_senders_list)


def _create_questionnaire(manager, questionnaire, question):
    question_set = [{'title': question, 'type': 'text', "is_entity_question": False,
                     "code": 'q1', "name": question, 'required': True,
                     "parent_field_code": '',
                     "instruction": "Answer must be a text", 'label': question}]
    QuestionnaireBuilder(questionnaire, manager).update_questionnaire_with_questions(question_set)


def _create_poll(manager, questionnaire, selected_option, question):
    data_senders_list = []
    _create_questionnaire(manager, questionnaire, question)
    _associate_data_senders_to_questionnaire(data_senders_list, manager, questionnaire, selected_option)
    questionnaire.update_doc_and_save()


def _construct_questionnaire(request):
    manager = get_database_manager(request.user)
    questionnaire_code = helper.generate_questionnaire_code(manager)
    questionnaire = Project(manager, name=request.POST.get('poll_name'),
                            fields=[], form_code=questionnaire_code, language=request.LANGUAGE_CODE,
                            devices=[u'sms', u'web', u'smartPhone'], is_poll=True)
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


@login_required
@session_not_expired
@csrf_exempt
@is_not_expired
def create_poll(request):
    if request.method == 'POST':
        return create_poll_questionnaire(request)