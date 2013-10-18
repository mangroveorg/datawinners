# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import json
import logging

from django.contrib.auth.decorators import login_required
from django.template.defaultfilters import register
from django.utils import translation
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, \
    HttpResponseServerError
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_view_exempt, csrf_response_exempt
from django.views.decorators.http import require_http_methods
from django.utils.translation import ugettext as _
import jsonpickle
import xlwt
from django.contrib import messages

from datawinners import utils
from datawinners.accountmanagement.decorators import is_datasender, session_not_expired, is_not_expired, is_new_user, valid_web_user
from datawinners.entity.subjects import load_subject_type_with_projects, get_subjects_count
from datawinners.main.database import get_database_manager
from datawinners.search.entity_search import SubjectQuery
from mangrove.form_model.field import field_to_json
from mangrove.transport import Channel
from datawinners.alldata.helper import get_visibility_settings_for
from datawinners.accountmanagement.models import NGOUserProfile, Organization
from datawinners.custom_report_router.report_router import ReportRouter
from datawinners.entity.helper import create_registration_form, delete_entity_instance, get_entity_type_fields, put_email_information_to_entity
from datawinners.location.LocationTree import get_location_tree, get_location_hierarchy
from datawinners.messageprovider.message_handler import get_exception_message_for
from datawinners.messageprovider.messages import exception_messages, WEB
from mangrove.datastore.entity_type import define_type
from mangrove.errors.MangroveException import EntityTypeAlreadyDefined, DataObjectAlreadyExists, QuestionCodeAlreadyExistsException, EntityQuestionAlreadyExistsException, DataObjectNotFound, QuestionAlreadyExistsException
from datawinners.entity.forms import EntityTypeForm
from mangrove.form_model.form_model import LOCATION_TYPE_FIELD_NAME, REGISTRATION_FORM_CODE, REPORTER, get_form_model_by_entity_type, get_form_model_by_code, GEO_CODE_FIELD_NAME, NAME_FIELD, SHORT_CODE_FIELD, header_fields
from mangrove.transport.player.player import WebPlayer
from mangrove.transport import TransportInfo
from datawinners.entity import import_data as import_module
from mangrove.utils.types import is_empty
from datawinners.submission.location import LocationBridge
from datawinners.utils import get_excel_sheet, workbook_add_sheet, get_organization, get_organization_country, \
    get_database_manager_for_org, get_changed_questions
from datawinners.questionnaire.questionnaire_builder import QuestionnaireBuilder
from mangrove.datastore.entity import get_by_short_code
from mangrove.transport.player.parser import XlsOrderedParser
from datawinners.activitylog.models import UserActivityLog
from datawinners.common.constant import ADDED_SUBJECT_TYPE, DELETED_SUBJECTS, REGISTERED_SUBJECT, EDITED_REGISTRATION_FORM, IMPORTED_SUBJECTS
from datawinners.entity.import_data import send_email_to_data_sender
from datawinners.project.helper import create_request
from datawinners.project.web_questionnaire_form import SubjectRegistrationForm
from datawinners.search.entity_search import DatasenderQuery


websubmission_logger = logging.getLogger("websubmission")

@login_required(login_url='/login')
@is_not_expired
def create_type(request):
    success = False
    form = EntityTypeForm(request.POST)
    if form.is_valid():
        entity_name = form.cleaned_data["entity_type_regex"]
        entity_name = [entity_name.strip().lower()]
        try:
            manager = get_database_manager(request.user)
            define_type(manager, entity_name)
            create_registration_form(manager, entity_name)
            message = _("Entity definition successful")
            success = True
            UserActivityLog().log(request, action=ADDED_SUBJECT_TYPE, detail=entity_name[0].capitalize())
        except EntityTypeAlreadyDefined:
            if request.POST["referer"] == 'project':
                message = _("%s already registered as a subject type. Please select %s from the drop down menu.") % (
                    entity_name[0], entity_name[0])
            else:
                message = _("%s already registered as a subject type.") % (entity_name[0],)
    else:
        message = form.errors['entity_type_regex']
    return HttpResponse(json.dumps({'success': success, 'message': _(message)}))


@register.filter
def get_count(h, key):
    return h.get(key) or "0"


@csrf_view_exempt
@csrf_response_exempt
@login_required(login_url='/login')
@session_not_expired
@is_new_user
@is_datasender
@is_not_expired
def all_subject_types(request):
    manager = get_database_manager(request.user)
    subjects_data = load_subject_type_with_projects(manager)
    subjects_count = get_subjects_count(manager)
    return render_to_response('entity/all_subject_types.html',
                              {'all_data': subjects_data, 'current_language': translation.get_language(),
                               'subjects_count': subjects_count,
                              },
                              context_instance=RequestContext(request))


@csrf_view_exempt
@csrf_response_exempt
@login_required(login_url='/login')
@session_not_expired
@is_new_user
@is_datasender
@is_not_expired
def all_subjects(request, subject_type):
    manager = get_database_manager(request.user)
    header_dict = header_fields(manager, subject_type)
    form_model = get_form_model_by_entity_type(manager, [subject_type])
    return render_to_response('entity/all_subjects.html',
                              {'subject_headers': header_dict,
                               'current_language': translation.get_language(),
                               'entity_type': subject_type,
                               'questions': form_model.fields,
                               'form_code': form_model.form_code,
                               'links': {
                                   'create_subject': reverse("create_subject", args=(subject_type,)) + "?web_view=True",
                                   'edit_subject_registration_form': reverse("edit_subject_questionnaire",
                                                                             args=(subject_type,))}
                              },
                              context_instance=RequestContext(request))


def viewable_questionnaire(form_model):
    questions = []
    for field in form_model.fields:
        preview = {"description": field.label, "code": field.code, "type": field.type,
                   "instruction": field.instruction}
        constraints = field.get_constraint_text() if field.type not in ["select", "select1"] else \
            [(option["text"], option["val"]) for option in field.options]
        preview.update({"constraints": constraints})
        questions.append(preview)
    return questions


@csrf_view_exempt
@csrf_response_exempt
@login_required()
@session_not_expired
@is_new_user
@is_datasender
@is_not_expired
def all_subjects_ajax(request, subject_type):
    search_parameters = {}
    search_text = request.GET.get('sSearch', '').strip()
    search_parameters.update({"search_text": search_text})
    search_parameters.update({"start_result_number": int(request.GET.get('iDisplayStart'))})
    search_parameters.update({"number_of_results": int(request.GET.get('iDisplayLength'))})
    search_parameters.update({"order_by": int(request.GET.get('iSortCol_0')) - 1})
    search_parameters.update({"order": "-" if request.GET.get('sSortDir_0') == "desc" else ""})
    user = request.user

    query_count, search_count, subjects = SubjectQuery().paginated_query(user, subject_type, search_parameters)

    return HttpResponse(
        jsonpickle.encode(
            {
                'subjects': subjects,
                'iTotalDisplayRecords': query_count,
                'iDisplayStart': int(request.GET.get('iDisplayStart')),
                "iTotalRecords": search_count,
                'iDisplayLength': int(request.GET.get('iDisplayLength'))
            }, unpicklable=False), content_type='application/json')


@register.filter
def get_element(h, key):
    return h.get(key) or '--'


def get_success_message(entity_type):
    if entity_type == REPORTER:
        return _("Data Sender(s) successfully deleted.")
    return _("Subject(s) successfully deleted.")


def _get_full_name(user):
    return user.first_name + ' ' + user.last_name


@csrf_view_exempt
@csrf_response_exempt
@login_required(login_url='/login')
@is_datasender
def delete_subjects(request):
    manager = get_database_manager(request.user)
    entity_type = request.POST['entity_type']
    all_ids = subject_short_codes_to_delete(request, manager, entity_type)

    transport_info = TransportInfo("web", request.user.username, "")
    delete_entity_instance(manager, all_ids, entity_type, transport_info)
    log_activity(request, DELETED_SUBJECTS, "%s: [%s]" % (entity_type.capitalize(), ", ".join(all_ids)))
    messages.success(request, get_success_message(entity_type))
    return HttpResponse(json.dumps({'success': True}))


def subject_short_codes_to_delete(request, manager, entity_type):
    if request.POST.get("all_selected", False):
        search_query = request.POST.get('search_query')
        subject_list = SubjectQuery().query(request.user, entity_type, search_query)
        short_code_index = header_fields(manager, entity_type).keys().index("short_code")
        return [s[short_code_index] for s in subject_list]

    return request.POST['all_ids'].split(';')


def _index_ofkey_in_ordered_dict(ordered_dict, key):
    return ordered_dict.keys().index(key)


def log_activity(request, action, detail):
    UserActivityLog().log(request, action=action, detail=detail, project=request.POST.get("project", "").capitalize())


def __create_web_users(org_id, reporter_details, language_code):
    duplicate_email_ids = User.objects.filter(email__in=[x['email'].lower() for x in reporter_details]).values('email')
    errors = []
    dbm = get_database_manager_for_org(Organization.objects.get(org_id=org_id))
    if len(duplicate_email_ids) > 0:
        for duplicate_email in duplicate_email_ids:
            errors.append("User with email %s already exists" % duplicate_email['email'])
        content = json.dumps({'success': False, 'errors': errors})
    else:
        for reporter in reporter_details:
            reporter_entity = get_by_short_code(dbm, reporter['reporter_id'], [REPORTER])
            reporter_email = reporter['email'].lower()
            put_email_information_to_entity(dbm, reporter_entity, email=reporter_email)
            user = User.objects.create_user(reporter_email, reporter_email, 'test123')
            group = Group.objects.filter(name="Data Senders")[0]
            user.groups.add(group)
            user.first_name = reporter_entity.value(NAME_FIELD)
            user.save()
            profile = NGOUserProfile(user=user, org_id=org_id, title="Mr",
                                     reporter_id=reporter['reporter_id'].lower())
            profile.save()

            send_email_to_data_sender(user, language_code)

        content = json.dumps({'success': True, 'message': "Users has been created"})
    return content


def create_single_web_user(org_id, email_address, reporter_id, language_code):
    """Create single web user from My Data Senders page"""
    return HttpResponse(
        __create_web_users(org_id, [{'email': email_address, 'reporter_id': reporter_id}], language_code))


@login_required(login_url='/login')
@csrf_view_exempt
@is_not_expired
def create_multiple_web_users(request):
    """Create multiple web users from All Data Senders page"""
    org_id = request.user.get_profile().org_id
    if request.method == 'POST':
        post_data = json.loads(request.POST['post_data'])
        content = __create_web_users(org_id, post_data, request.LANGUAGE_CODE)
        return HttpResponse(content)

@csrf_view_exempt
@csrf_response_exempt
@require_http_methods(['POST'])
@valid_web_user
#todo remove form_code from here, use entity_type instead
def import_subjects_from_project_wizard(request, form_code):
    manager = get_database_manager(request.user)
    error_message, failure_imports, success_message, imported_entities = import_module.import_data(request, manager,
                                                                                                   default_parser=XlsOrderedParser,
                                                                                                   form_code=form_code)
    if len(imported_entities) != 0:
        detail_dict = dict()
        for short_code, entity_type in imported_entities.items():
            entity_type = entity_type.capitalize()
            if detail_dict.get(entity_type) is not None:
                detail_dict.get(entity_type).append(short_code)
            else:
                detail_dict.update({entity_type: [short_code]})
        for key, detail in detail_dict.items():
            detail_dict.update({key: "[%s]" % ", ".join(detail)})
        UserActivityLog().log(request, action=IMPORTED_SUBJECTS, detail=json.dumps(detail_dict))

    subjects_data = import_module.load_all_subjects(manager)

    return HttpResponse(json.dumps(
        {'success': error_message is None and is_empty(failure_imports),
         'message': success_message,
         'error_message': error_message,
         'failure_imports': failure_imports,
         'all_data': subjects_data,
         'imported': imported_entities.keys()
        }))


def _make_form_context(questionnaire_form, entity_type, disable_link_class, hide_link_class, form_code, org_number,
                       form_model_fields, is_update=False, back_link=None, web_view=False):
    return {'questionnaire_form': questionnaire_form,
            'questions': form_model_fields,
            'entity_type': entity_type,
            "disable_link_class": disable_link_class,
            "hide_link_class": hide_link_class,
            'back_to_project_link': reverse("alldata_index"),
            'smart_phone_instruction_link': reverse("smart_phone_instruction"),
            'is_update': is_update,
            'back_link': back_link,
            'form_code': form_code,
            'example_sms': get_example_sms_message(form_model_fields, form_code),
            'org_number': org_number,
            "web_view": web_view,
            'extension_template': "entity/web_questionnaire.html",
            "register_subjects_link": reverse("create_subject", args=[entity_type]) + "?web_view=True",
            "edit_subject_questionnaire_link": reverse("edit_subject_questionnaire", args=[entity_type])
    }


def get_template(user):
    return 'entity/register_subject.html' if user.get_profile().reporter else 'entity/subject/registration.html'


def initialize_values(form_model, subject):
    for field in form_model.fields:
        if field.name == LOCATION_TYPE_FIELD_NAME:
            field.value = ','.join(subject.location_path)
        elif field.name == GEO_CODE_FIELD_NAME:
            field.value = ','.join(map(str, subject.geometry['coordinates']))
        elif field.name == SHORT_CODE_FIELD:
            field.value = subject.short_code
        else:
            field.value = subject.data[field.name]['value'] if field.name in subject.data.keys() else None

        if field.value:
            field.value = field.convert_to_unicode()


@valid_web_user
def edit_subject(request, entity_type, entity_id, project_id=None):
    manager = get_database_manager(request.user)
    form_model = get_form_model_by_entity_type(manager, [entity_type.lower()])
    subject = get_by_short_code(manager, entity_id, [entity_type.lower()])
    back_link = reverse(all_subjects, args=[entity_type])

    web_questionnaire_template = get_template(request.user)
    disable_link_class, hide_link_class = get_visibility_settings_for(request.user)
    if request.method == 'GET':
        initialize_values(form_model, subject)
        questionnaire_form = SubjectRegistrationForm(form_model)
        form_context = _make_form_context(questionnaire_form, entity_type, disable_link_class, hide_link_class,
                                          form_model.form_code, get_organization_telephone_number(request),
                                          form_model.fields, is_update=True,
                                          back_link=back_link)
        return render_to_response(web_questionnaire_template,
                                  form_context,
                                  context_instance=RequestContext(request))
    if request.method == 'POST':
        questionnaire_form = SubjectRegistrationForm(form_model, data=request.POST,
                                                     country=get_organization_country(request))
        if not questionnaire_form.is_valid():
            form_context = _make_form_context(questionnaire_form, entity_type, disable_link_class, hide_link_class,
                                              form_model.form_code, get_organization_telephone_number(request),
                                              form_model.fields, is_update=True, back_link=back_link)
            return render_to_response(web_questionnaire_template,
                                      form_context,
                                      context_instance=RequestContext(request))

        success_message = None
        error_message = None
        try:
            response = WebPlayer(manager,
                                 LocationBridge(location_tree=get_location_tree(),
                                                get_loc_hierarchy=get_location_hierarchy)).accept(
                create_request(questionnaire_form, request.user.username, is_update=True))

            if response.success:
                success_message = _("Your changes have been saved.")
                questionnaire_form = SubjectRegistrationForm(form_model, data=request.POST,
                                                             country=get_organization_country(request))
            else:
                from datawinners.project.helper import errors_to_list

                questionnaire_form._errors = errors_to_list(response.errors, form_model.fields)
                form_context = _make_form_context(questionnaire_form, entity_type, disable_link_class, hide_link_class,
                                                  form_model.form_code, get_organization_telephone_number(request),
                                                  form_model.fields, is_update=True, back_link=back_link)
                return render_to_response(web_questionnaire_template,
                                          form_context,
                                          context_instance=RequestContext(request))

        except DataObjectNotFound:
            message = exception_messages.get(DataObjectNotFound).get(WEB)
            error_message = _(message) % (form_model.entity_type[0], form_model.entity_type[0])
        except Exception as exception:
            error_message = _(get_exception_message_for(exception=exception, channel=Channel.WEB))
        subject_context = _make_form_context(questionnaire_form, entity_type, disable_link_class, hide_link_class,
                                             form_model.form_code, get_organization_telephone_number(request),
                                             form_model.fields, is_update=True, back_link=back_link)
        subject_context.update({'success_message': success_message, 'error_message': error_message})

        return render_to_response(web_questionnaire_template, subject_context,
                                  context_instance=RequestContext(request))


@valid_web_user
def create_subject(request, entity_type=None):
    manager = get_database_manager(request.user)
    form_model = get_form_model_by_entity_type(manager, [entity_type.lower()])
    web_questionnaire_template = get_template(request.user)
    disable_link_class, hide_link_class = get_visibility_settings_for(request.user)

    if request.method == 'GET':
        questionnaire_form = SubjectRegistrationForm(form_model)

        form_context = _make_form_context(questionnaire_form, entity_type, disable_link_class, hide_link_class,
                                          form_model.form_code, get_organization_telephone_number(request),
                                          form_model.fields, web_view=request.GET.get("web_view", False))

        return render_to_response(web_questionnaire_template,
                                  form_context,
                                  context_instance=RequestContext(request))

    if request.method == 'POST':
        questionnaire_form = SubjectRegistrationForm(form_model, data=request.POST,
                                                     country=get_organization_country(request))
        if not questionnaire_form.is_valid():
            form_context = _make_form_context(questionnaire_form, entity_type, disable_link_class, hide_link_class,
                                              form_model.form_code, get_organization_telephone_number(request),
                                              form_model.fields, web_view=True)
            return render_to_response(web_questionnaire_template,
                                      form_context,
                                      context_instance=RequestContext(request))

        success_message = None
        error_message = None
        try:
            from datawinners.project.helper import create_request

            response = WebPlayer(manager,
                                 LocationBridge(location_tree=get_location_tree(),
                                                get_loc_hierarchy=get_location_hierarchy)).accept(
                create_request(questionnaire_form, request.user.username), logger=websubmission_logger)
            if response.success:
                ReportRouter().route(get_organization(request).org_id, response)
                success_message = (_("Successfully submitted. Unique identification number(ID) is:") + " %s") % (
                    response.short_code,)
                detail_dict = dict({"Subject Type": entity_type.capitalize(), "Unique ID": response.short_code})
                UserActivityLog().log(request, action=REGISTERED_SUBJECT, detail=json.dumps(detail_dict))
                questionnaire_form = SubjectRegistrationForm(form_model)
            else:
                from datawinners.project.helper import errors_to_list

                questionnaire_form._errors = errors_to_list(response.errors, form_model.fields)
                form_context = _make_form_context(questionnaire_form, entity_type, disable_link_class, hide_link_class,
                                                  form_model.form_code, get_organization_telephone_number(request),
                                                  form_model.fields, web_view=True)
                return render_to_response(web_questionnaire_template,
                                          form_context,
                                          context_instance=RequestContext(request))

        except DataObjectNotFound:
            message = exception_messages.get(DataObjectNotFound).get(WEB)
            error_message = _(message) % (form_model.entity_type[0], form_model.entity_type[0])
        except DataObjectAlreadyExists as exception:
            error_message = _("Entity with Unique Identification Number (ID) = %s already exists.") % exception.data[1]
        except Exception as exception:
            error_message = _(get_exception_message_for(exception=exception, channel=Channel.WEB))

        subject_context = _make_form_context(questionnaire_form, entity_type, disable_link_class, hide_link_class,
                                             form_model.form_code, get_organization_telephone_number(request),
                                             form_model.fields, web_view=True)
        subject_context.update({'success_message': success_message, 'error_message': error_message})

        return render_to_response(web_questionnaire_template, subject_context,
                                  context_instance=RequestContext(request))

@valid_web_user
@login_required(login_url='/login')
@session_not_expired
@is_not_expired
def edit_subject_questionnaire(request, entity_type=None):
    # edit subject type questionnaire view
    manager = get_database_manager(request.user)
    if entity_type is None:
        return HttpResponseRedirect(reverse(all_subject_types))

    form_model = get_form_model_by_entity_type(manager, [entity_type.lower()])
    if form_model is None:
        form_model = get_form_model_by_code(manager, REGISTRATION_FORM_CODE)
    fields = form_model.fields

    existing_questions = json.dumps(fields, default=field_to_json)
    return render_to_response('entity/questionnaire.html',
                              {'existing_questions': repr(existing_questions),
                               'questionnaire_code': form_model.form_code,
                               'language': form_model.activeLanguages[0],
                               'entity_type': entity_type,
                               'post_url': reverse(save_questionnaire)},
                              context_instance=RequestContext(request))


@valid_web_user
def save_questionnaire(request):
    manager = get_database_manager(request.user)
    if request.method == 'POST':
        new_short_code = request.POST['questionnaire-code'].lower()
        saved_short_code = request.POST['saved-questionnaire-code'].lower()

        form_model = get_form_model_by_code(manager, saved_short_code)
        detail_dict = dict()
        if new_short_code != saved_short_code:
            try:
                form_model.form_code = new_short_code
                form_model.save()
                detail_dict.update({"form_code": new_short_code})
            except DataObjectAlreadyExists as e:
                if e.message.find("Form") >= 0:
                    return HttpResponse(json.dumps({'success': False,
                                                    'error_message': "Questionnaire with this code already exists"}))
                return HttpResponseServerError(e.message)

        json_string = request.POST['question-set']
        question_set = json.loads(json_string)
        try:
            saved_fields = form_model.fields
            QuestionnaireBuilder(form_model, manager).update_questionnaire_with_questions(question_set)
            form_model.save()
            changed = get_changed_questions(saved_fields, form_model.fields)
            changed.update(dict(entity_type=form_model.entity_type[0].capitalize()))
            detail_dict.update(changed)
            kwargs = dict()
            if request.POST.get("project-name") is not None:
                kwargs.update(dict(project=request.POST.get("project-name").capitalize()))
            UserActivityLog().log(request, action=EDITED_REGISTRATION_FORM, detail=json.dumps(detail_dict), **kwargs)
            return HttpResponse(json.dumps({'success': True, 'form_code': form_model.form_code}))
        except QuestionCodeAlreadyExistsException as e:
            return HttpResponse(json.dumps({'success': False, 'error_message': _(e.message)}))
        except QuestionAlreadyExistsException as e:
            return HttpResponse(json.dumps({'success': False, 'error_message': _(e.message)}))
        except EntityQuestionAlreadyExistsException as e:
            return HttpResponse(json.dumps({'success': False, 'error_message': _(e.message)}))


@valid_web_user
def export_subject(request):
    manager = get_database_manager(request.user)
    query_text = request.POST.get('query_text', '')
    subject_type = request.POST.get('subject_type', '').lower()
    subject_list = SubjectQuery().query(request.user, subject_type, query_text)

    response = HttpResponse(mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="%s.xls"' % (subject_type,)
    fields, labels, field_codes = get_entity_type_fields(manager, subject_type, for_export=True)
    raw_data = [labels]

    for subject in subject_list:
        raw_data.append(subject)

    wb = get_excel_sheet(raw_data, subject_type)
    form_model = get_form_model_by_entity_type(manager, [subject_type.lower()])
    add_codes_sheet(wb, form_model.form_code, field_codes)
    wb.save(response)
    return response


def add_codes_sheet(wb, form_code, field_codes):
    codes = [form_code]
    codes.extend(field_codes)
    ws = workbook_add_sheet(wb, [codes], "codes")
    ws.visibility = 1


@valid_web_user
def export_template(request, entity_type=None):
    manager = get_database_manager(request.user)
    if entity_type is None:
        return HttpResponseRedirect(reverse(all_subject_types))

    fields, labels, field_codes = get_entity_type_fields(manager, entity_type, for_export=True)
    response = HttpResponse(mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="%s.xls"' % (entity_type,)
    form_model = get_form_model_by_entity_type(manager, [entity_type.lower()])

    wb = get_excel_sheet([labels], entity_type)
    form_code = form_model.form_code
    add_codes_sheet(wb, form_code, field_codes)
    try:
        index_geocode = fields.index(GEO_CODE_FIELD_NAME)
    except ValueError:
        index_geocode = 0

    ws = wb.get_sheet(0)

    style = xlwt.XFStyle()
    style.num_format_str = '@'
    gps_col = ws.col(index_geocode)
    gps_col.set_style(style)

    uid_col = ws.col(len(fields) - 1)
    uid_col.set_style(style)

    wb.save(response)
    return response


def get_organization_telephone_number(request):
    organization_settings = utils.get_organization_settings_from_request(request)
    organisation_sms_numbers = organization_settings.get_organisation_sms_number()
    if organization_settings.organization.in_trial_mode:
        return organisation_sms_numbers
    return organisation_sms_numbers[0] if not organisation_sms_numbers[0] or organisation_sms_numbers[0][0] \
                                          == "+" else "+%s" % organisation_sms_numbers[0]


def get_example_sms_message(fields, form_code):
    return "%s %s" % (form_code, get_example_sms(fields))


def get_example_sms(fields):
    example_sms = ""
    for field in fields:
        example_sms = example_sms + " " + unicode(_('answer')) + str(fields.index(field) + 1)
    return example_sms