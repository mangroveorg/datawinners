# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import json
import logging
from operator import itemgetter

import elasticutils
import jsonpickle
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.template.defaultfilters import register, lower
from django.utils import translation
from django.utils.translation import ugettext as _, ugettext, get_language
from django.views.decorators.csrf import csrf_view_exempt, csrf_response_exempt
from django.views.decorators.http import require_http_methods
from waffle.decorators import waffle_flag

from datawinners.accountmanagement.decorators import is_datasender, session_not_expired, is_not_expired, is_new_user, \
    valid_web_user
from datawinners.accountmanagement.helper import create_web_users, validate_email_addresses
from datawinners.accountmanagement.localized_time import get_country_time_delta
from datawinners.accountmanagement.models import Organization, OrganizationSetting
from datawinners.activitylog.models import UserActivityLog
from datawinners.alldata.helper import get_visibility_settings_for
from datawinners.common.constant import ADDED_IDENTIFICATION_NUMBER_TYPE, REGISTERED_IDENTIFICATION_NUMBER, \
    EDITED_REGISTRATION_FORM, IMPORTED_IDENTIFICATION_NUMBER, DELETED_IDENTIFICATION_NUMBER
from datawinners.custom_report_router.report_router import ReportRouter
from datawinners.entity import import_data as import_module
from datawinners.entity.forms import EntityTypeForm
from datawinners.entity.geo_data import geo_jsons
from datawinners.entity.group_helper import create_new_group
from datawinners.entity.helper import create_registration_form, get_organization_telephone_number, set_email_for_contact
from datawinners.entity.subjects import load_subject_type_with_projects, get_subjects_count
from datawinners.location.LocationTree import get_location_tree, get_location_hierarchy
from datawinners.main.database import get_database_manager, get_db_manager
from datawinners.main.utils import get_database_name
from datawinners.messageprovider.message_handler import get_exception_message_for
from datawinners.messageprovider.messages import exception_messages, WEB
from datawinners.project.helper import create_request
from datawinners.project.submission.exporter import SubmissionExporter
from datawinners.project.web_questionnaire_form import SubjectRegistrationForm
from datawinners.public.views import _get_filters, _get_uniqueid_filters
from datawinners.questionnaire.questionnaire_builder import QuestionnaireBuilder
from datawinners.search.entity_search import SubjectQuery
from datawinners.search.index_utils import delete_mapping, es_questionnaire_field_name
from datawinners.search.submission_index import update_submission_search_for_subject_edition
from datawinners.settings import ELASTIC_SEARCH_URL, ELASTIC_SEARCH_TIMEOUT
from datawinners.submission.location import LocationBridge
from datawinners.utils import get_organization, get_organization_country, \
    get_changed_questions, get_mapbox_api_key
from datawinners.workbook_utils import workbook_add_sheet
from mangrove.datastore.documents import EntityActionDocument, HARD_DELETE
from mangrove.datastore.entity import get_all_entities_include_voided, delete_data_record, contact_by_short_code
from mangrove.datastore.entity import get_by_short_code
from mangrove.datastore.entity_share import save_entity_preference, get_entity_preference
from mangrove.datastore.entity_type import define_type, delete_type, entity_type_already_defined,\
    get_unique_id_types
from mangrove.datastore.report_config import get_report_config
from mangrove.errors.MangroveException import EntityTypeAlreadyDefined, DataObjectAlreadyExists, \
    QuestionCodeAlreadyExistsException, EntityQuestionAlreadyExistsException, DataObjectNotFound, \
    QuestionAlreadyExistsException
from mangrove.form_model.field import field_to_json, DateField
from mangrove.form_model.form_model import LOCATION_TYPE_FIELD_NAME, REGISTRATION_FORM_CODE, REPORTER, \
    get_form_model_by_entity_type, get_form_model_by_code, GEO_CODE_FIELD_NAME, SHORT_CODE_FIELD, \
    header_fields, get_field_by_attribute_value
from mangrove.transport import Channel
from mangrove.transport.player.parser import XlsOrderedParser
from mangrove.transport.player.player import WebPlayer
from mangrove.utils.types import is_empty

websubmission_logger = logging.getLogger("websubmission")
datawinners_logger = logging.getLogger("datawinners")


@login_required
@is_not_expired
def create_group(request):
    manager = get_database_manager(request.user)
    new_group_name = request.POST.get('group_name')
    success, message = create_new_group(manager, new_group_name.strip())
    return HttpResponse(json.dumps({'success': success, 'message': _(message)}))

@login_required
@is_not_expired
def create_type(request):
    success = False
    form = EntityTypeForm(request.POST)
    if form.is_valid():
        entity_name = form.cleaned_data["entity_type_regex"]
        entity_name = [entity_name.strip().lower()]
        try:
            manager = get_database_manager(request.user)

            if entity_type_already_defined(manager, entity_name):
                raise EntityTypeAlreadyDefined(u"Type: %s is already defined" % u'.'.join(entity_name))

            create_registration_form(manager, entity_name)
            define_type(manager, entity_name)
            message = _("Entity definition successful")
            success = True
            UserActivityLog().log(request, action=ADDED_IDENTIFICATION_NUMBER_TYPE, project=entity_name[0].capitalize())
        except EntityTypeAlreadyDefined:
            message = _("%s already exists.") % (entity_name[0].capitalize(),)
    else:
        message = form.errors['entity_type_regex']
    return HttpResponse(json.dumps({'success': success, 'message': _(message)}))


@register.filter
def get_count(h, key):
    return h.get(key) or "0"


@csrf_view_exempt
@csrf_response_exempt
@login_required
@session_not_expired
@is_new_user
@is_datasender
@is_not_expired
def all_subject_types(request):
    manager = get_database_manager(request.user)
    subjects_data = load_subject_type_with_projects(manager)
    subjects_count = get_subjects_count(manager)
    if "deleted_subject" in request.GET.keys():
        deleted_subject_error_message = _('Sorry. The Identification Number Type you are looking for has been deleted')
        return render_to_response('entity/all_subject_types.html',
                              {'all_data': subjects_data, 'current_language': translation.get_language(),
                               'subjects_count': subjects_count,
                               'is_pro_sms': get_organization(request).is_pro_sms,
                               'deleted_subject_error_message': [deleted_subject_error_message],
                              },
                              context_instance=RequestContext(request))
    else:
        return render_to_response('entity/all_subject_types.html',
                              {'all_data': subjects_data,'is_pro_sms': get_organization(request).is_pro_sms
                               ,'current_language': translation.get_language(),
                               'subjects_count': subjects_count,
                              },
                              context_instance=RequestContext(request))


def delete_subject_types(request):
    manager = get_database_manager(request.user)
    subject_types = request.POST.get("all_ids")
    subject_types = subject_types.split(";")
    delete_type(manager, subject_types)
    for subject_type in subject_types:
        form_model = get_form_model_by_entity_type(manager, [subject_type])
        delete_mapping(manager.database_name, subject_type)
        entities = get_all_entities_include_voided(manager, [subject_type])
        for entity in entities:
            delete_data_record(manager, form_model.form_code, entity.short_code)
            manager._save_document(EntityActionDocument(form_model.entity_type[0], entity.short_code, HARD_DELETE))
            entity.delete()
        form_model.delete()
        UserActivityLog().log(request, action=DELETED_IDENTIFICATION_NUMBER, project=form_model.entity_type[0].capitalize())
    messages.success(request, _("Identification Number Type(s) successfully deleted."))
    return HttpResponse(json.dumps({'success': True}))


@csrf_view_exempt
@csrf_response_exempt
@login_required
@session_not_expired
@is_new_user
@is_datasender
@is_not_expired
def all_subjects(request, subject_type):
    manager = get_database_manager(request.user)
    form_model = get_form_model_by_entity_type(manager, [subject_type])
    if not form_model:
        all_subject_types_page = '/entity/subjects/' + "?deleted_subject=true"
        return HttpResponseRedirect(all_subject_types_page)
    else:
        header_dict = header_fields(form_model)
        form_model = get_form_model_by_entity_type(manager, [subject_type])
        return render_to_response('entity/all_subjects.html',
                              {'subject_headers': header_dict,
                               'current_language': translation.get_language(),
                               'entity_type': subject_type,
                               'questions': form_model.fields,
                               'form_code': form_model.form_code,
                               'is_pro_sms': get_organization(request).is_pro_sms,
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


def _get_order_field(post_dict, user, subject_type):
    order_by = int(post_dict.get('iSortCol_0')) - 1
    headers = SubjectQuery().get_headers(user, subject_type)
    return headers[order_by]


@csrf_view_exempt
@csrf_response_exempt
@login_required
@session_not_expired
@is_new_user
@is_datasender
@is_not_expired
def all_subjects_ajax(request, subject_type):
    try:
        user = request.user
        search_parameters = {}
        search_text = request.POST.get('sSearch', '').strip()
        search_parameters.update({"search_text": search_text})
        search_parameters.update({"start_result_number": int(request.POST.get('iDisplayStart'))})
        search_parameters.update({"number_of_results": int(request.POST.get('iDisplayLength'))})
        search_parameters.update({"sort_field": _get_order_field(request.POST, user, subject_type)})
        search_parameters.update({"order": "-" if request.POST.get('sSortDir_0') == "desc" else ""})

        query_count, search_count, subjects = SubjectQuery(search_parameters).paginated_query(user, subject_type)
        return HttpResponse(
        jsonpickle.encode(
            {
                'data': subjects,
                'iTotalDisplayRecords': query_count,
                'iDisplayStart': int(request.POST.get('iDisplayStart')),
                "iTotalRecords": search_count,
                'iDisplayLength': int(request.POST.get('iDisplayLength'))
            }, unpicklable=False), content_type='application/json')

    except Exception as e:
        datawinners_logger.error("All Subjects Ajax failed")
        datawinners_logger.error(request.POST)
        datawinners_logger.exception(e)
        raise


@register.filter
def get_element(h, key):
    return h.get(key) or '--'


def get_success_message(entity_type):
    if entity_type == REPORTER:
        return _("Data Sender(s) successfully deleted.")
    return _("Subject(s) successfully deleted.")


def log_activity(request, action, detail):
    UserActivityLog().log(request, action=action, detail=detail, project=request.POST.get("project", "").capitalize())


def create_single_web_user(org_id, email_address, reporter_id, language_code):
    """Create single web user from My Data Senders page"""
    return HttpResponse(
        create_web_users(org_id, {reporter_id: email_address}, language_code))


def _set_contacts_email_address(dbm, request):
    web_user_id_email_map = {}
    for item in json.loads(request.POST['post_data']):
        contact = contact_by_short_code(dbm, item['reporter_id'])
        if contact.is_contact:
            set_email_for_contact(dbm, contact, item['email'])
        else:
            web_user_id_email_map.update({item['reporter_id']: item['email']})

    return web_user_id_email_map


def create_contact_id_email_map(request):
    contact_id_email_map = {}
    for item in json.loads(request.POST['post_data']):
        contact_id_email_map.update({item['reporter_id']: item['email']})
    return contact_id_email_map


def _set_email_for_contacts(dbm, org_id, request):
    contact_id_email_map = create_contact_id_email_map(request)
    content, duplicate_entries, errors = validate_email_addresses(contact_id_email_map)
    if errors.__len__() == 0 and duplicate_entries.keys().__len__() == 0:
        web_user_id_email_map = _set_contacts_email_address(dbm, request)
        content = create_web_users(org_id, web_user_id_email_map, request.LANGUAGE_CODE)
    return content


@login_required
@csrf_view_exempt
@is_not_expired
@is_datasender
def create_multiple_web_users(request):
    """Create multiple web users from All Data Senders page"""
    org_id = request.user.get_profile().org_id
    dbm = get_database_manager(request.user)

    if request.method == 'POST':
        content = _set_email_for_contacts(dbm, org_id, request)
        return HttpResponse(content)


@csrf_view_exempt
@csrf_response_exempt
@require_http_methods(['POST'])
@valid_web_user
#todo remove form_code from here, use entity_type instead
def import_subjects_from_project_wizard(request, form_code):
    manager = get_database_manager(request.user)
    error_message, failure_imports, success_message, short_code_subject_details_dict = import_module.import_data(
        request, manager,
        default_parser=XlsOrderedParser,
        form_code=form_code)
    subject_details = {}

    if len(short_code_subject_details_dict) != 0:
        detail_dict = dict()
        form_model = get_form_model_by_code(manager, form_code)
        entity_type = form_model.entity_type[0]
        short_codes = []
        for short_code in short_code_subject_details_dict.keys():
            short_codes.append(short_code)

        subject_details = _format_imported_subjects_datetime_field_to_str(form_model, short_code_subject_details_dict)
        detail_dict.update({entity_type: "[%s]" % ", ".join(short_codes)})
        UserActivityLog().log(request, action=IMPORTED_IDENTIFICATION_NUMBER, detail=json.dumps(detail_dict))

    return HttpResponse(json.dumps(
        {'success': error_message is None and is_empty(failure_imports),
         'message': success_message,
         'error_message': error_message,
         'failure_imports': failure_imports,
         'successful_imports': subject_details,
        }))


def _format_imported_subjects_datetime_field_to_str(form_model, short_code_subject_details_dict):
    datetime_fields = [index for index, field in enumerate(form_model.fields) if type(field) == DateField]
    subject_details = []
    for subject_detail_dict in short_code_subject_details_dict.values():
        value = subject_detail_dict.values()
        for index in datetime_fields:
            value[index] = "%s-%s-%s" % (
            value[index].day, value[index].month, value[index].year) #strftime doesn't work for year<1900
        subject_details.append(value)
    return subject_details


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
        form_context.update({'is_pro_sms': get_organization(request).is_pro_sms})
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
                #assumption q6 - unique_id code and q2 - lastname codes cannot be changed
                update_submission_search_for_subject_edition(manager, [entity_type], response.processed_data)
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
@waffle_flag('idnr_map', None)
def map_admin(request, entity_type=None):
    form_model = get_form_model_by_entity_type(get_database_manager(request.user), [entity_type.lower()])
    entity_preference = get_entity_preference(get_db_manager("public"), _get_organization_id(request), entity_type)

    filters_in_entity_preference = []
    details_in_entity_preference = []
    specials_in_entity_preference = []

    if entity_preference is not None:
        filters_in_entity_preference = entity_preference.filters
        details_in_entity_preference = entity_preference.details
        specials_in_entity_preference = entity_preference.specials

    filters = _build_filterable_fields(form_model.form_fields, filters_in_entity_preference)
    details = _build_details(form_model.form_fields, details_in_entity_preference)
    specials = _build_specials(form_model.form_fields, specials_in_entity_preference)
    height_frame = len([flr for flr in filters if flr['visible']])
    height_frame = 428 + height_frame * 80
    return render_to_response('entity/map_edit.html',
                              {
                                  "entity_type": entity_type,
                                  "form_code": form_model.form_code,
                                  "filters": json.dumps(filters),
                                  "details": json.dumps(details),
                                  "specials": json.dumps(specials),
                                  "height_frame": height_frame
                                  
                               },
                              context_instance=RequestContext(request))


@valid_web_user
@waffle_flag('reports', None)
def map_data_for_reports(request, entity_type=None, report_id=None):
    return map_data(request, entity_type, get_report_config(get_database_manager(request.user), report_id),True)


@valid_web_user
@waffle_flag('idnr_map', None)
def map_data(request, entity_type=None, entity_preference=None, map_view = False):
    manager = get_database_manager(request.user)
    form_model = get_form_model_by_entity_type(manager, [entity_type.lower()])
    entity_preference = entity_preference or get_entity_preference(get_db_manager("public"), _get_organization_id(request), entity_type)
    details = entity_preference.details if entity_preference is not None else []
    specials = entity_preference.specials if entity_preference is not None else []
    total_in_label = entity_preference.total_in_label if entity_preference is not None else False
    fallback_location = entity_preference.fallback_location if entity_preference is not None else {}
    return render_to_response('map.html',
                              {
                                  "entity_type": entity_type,
                                  "fallback_location": fallback_location,
                                  "filters": [] if entity_preference is None else _get_filters(form_model, entity_preference.filters),
                                  "idnr_filters": [] if entity_preference is None else _get_uniqueid_filters(form_model, entity_preference.filters, manager),
                                  "geo_jsons": geo_jsons(manager, entity_type, request.GET, details, specials, map_view, total_in_label),
                                  "mapbox_api_key": get_mapbox_api_key(request.META['HTTP_HOST'])
                               },
                              context_instance=RequestContext(request))


def _get_organization_id(request):
    org_id = request.user.get_profile().org_id
    organization = Organization.objects.get(org_id=org_id)
    org_settings = OrganizationSetting.objects.get(organization=organization)
    return org_settings.document_store


def _build_filterable_fields(form_fields, filters_in_entity_preference):
    filters = [
        {'code': field['code'], 'label': field['label'], 'visible': field['code'] in filters_in_entity_preference}
        for field in form_fields if field.get('type') in ['select', 'select1']
    ]
    return filters


def _build_details(form_fields, details_in_entity_preference):
    details = [
        {'code': field['code'], 'label': field['label'], 'visible': field['code'] in details_in_entity_preference}
        for field in form_fields if field['code'] not in ['q2']
    ]
    return details


def _build_specials(form_fields, specials_in_entity_preference):
    specials = [
        {
            'code': field['code'], 'label': field['label'],
            'visible': field["code"] in specials_in_entity_preference,
            'choices': map(
                lambda c: {
                    'visible': field["code"] in specials_in_entity_preference and any(choice["value"] == c['val'] for choice in specials_in_entity_preference[field["code"]]),
                    'color': [choice['color'] for choice in specials_in_entity_preference[field["code"]] if choice["value"] == c['val']][0]
                        if field["code"] in specials_in_entity_preference and any(choice["value"] == c['val'] for choice in specials_in_entity_preference[field["code"]]) else "rgb(0, 0, 0)",
                    'choice': c
                },
                field["choices"]
            )
        }
        for field in form_fields if field.get('type') == 'select1'
    ]
    return specials


def _trim_empty_specials(specials):
    if specials:
        return dict(filter(itemgetter(1), specials.items()))
    return specials


@valid_web_user
@waffle_flag('idnr_map', None)
def save_preference(request, entity_type=None):
    form_model = get_form_model_by_entity_type(get_database_manager(request.user), [entity_type.lower()])
    if request.method == 'POST':
        data = json.loads(request.POST['data'])
        entity_preference = save_entity_preference(get_db_manager("public"),
                               _get_organization_id(request),
                               entity_type,
                               data.get('filters'),
                               data.get('details'),
                               _trim_empty_specials(data.get('specials')),
                               data.get('fallback_location'))
        filters = _build_filterable_fields(form_model.form_fields, entity_preference.filters)
        specials = _build_specials(form_model.form_fields, entity_preference.specials)
        details = _build_details(form_model.form_fields, entity_preference.details)
        return HttpResponse(json.dumps({
            'success': True,
            'filters': filters,
            'specials': specials,
            'details': details
        }))


@valid_web_user
@waffle_flag('idnr_map', None)
def share_token(request, entity_type):
    manager = get_db_manager("public")
    organization_id = _get_organization_id(request)
    entity_preference = get_entity_preference(manager, organization_id, entity_type)
    if entity_preference:
        return HttpResponse(json.dumps({"token": entity_preference.share_token}))
    entity_preference = save_entity_preference(manager, organization_id, entity_type)
    return HttpResponse(json.dumps({"token": entity_preference.share_token}))


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
        form_context.update({'is_pro_sms': get_organization(request).is_pro_sms})

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
                success_message = _("%s with Identification Number %s successfully registered.") % (
                entity_type.capitalize(), response.short_code)

                detail_dict = dict({"Subject Type": entity_type.capitalize(), "Unique ID": response.short_code})
                UserActivityLog().log(request, action=REGISTERED_IDENTIFICATION_NUMBER, detail=json.dumps(detail_dict))
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
            error_message = _("%s with ID Number '%s' already exists or has previously collected data.") % (exception.data[2], exception.data[1])
        except Exception as exception:
            error_message = _(get_exception_message_for(exception=exception, channel=Channel.WEB))

        subject_context = _make_form_context(questionnaire_form, entity_type, disable_link_class, hide_link_class,
                                             form_model.form_code, get_organization_telephone_number(request),
                                             form_model.fields, web_view=True)
        subject_context.update({'success_message': success_message, 'error_message': error_message})

        return render_to_response(web_questionnaire_template, subject_context,
                                  context_instance=RequestContext(request))


@login_required
@session_not_expired
@is_not_expired
def get_questionnaire_details_ajax(request, entity_type):
    manager = get_database_manager(request.user)
    form_model = get_form_model_by_entity_type(manager, [entity_type.lower()])
    if form_model is None:
        form_model = get_form_model_by_code(manager, REGISTRATION_FORM_CODE)
    fields = form_model.fields
    existing_questions = json.dumps(fields, default=field_to_json)

    return HttpResponse(jsonpickle.encode(
        {'existing_questions': existing_questions,
         'questionnaire_code': form_model.form_code},
        unpicklable=False), content_type='application/json')


@valid_web_user
@login_required
@session_not_expired
@is_not_expired
@is_datasender
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
                              {
                                  'existing_questions': repr(existing_questions),
                                  'questionnaire_code': form_model.form_code,
                                  'language': form_model.activeLanguages[0],
                                  'entity_type': entity_type,
                                  'is_pro_sms': get_organization(request).is_pro_sms,
                                  'post_url': reverse(save_questionnaire),
                                  'unique_id_types': json.dumps([{"name":unique_id_type.capitalize(),
                                                                  "value":unique_id_type} for unique_id_type in
                                                                 get_unique_id_types(manager) if unique_id_type != entity_type]),

                              },
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
                form_model.old_form_code = form_model.form_code
                form_model.form_code = new_short_code
                form_model.save()
                detail_dict.update({"form_code": new_short_code})
            except DataObjectAlreadyExists as e:
                if e.message.find("Form") >= 0:
                    return HttpResponse(json.dumps({'success': False, "code_has_error": True,
                                                    'error_message': ugettext(
                                                        "Questionnaire with same code already exists.")}))
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


def subject_autocomplete(request, entity_type):
    search_text = lower(request.GET["term"] or "")
    database_name = get_database_name(request.user)
    dbm = get_database_manager(request.user)
    form_model = get_form_model_by_entity_type(dbm, [entity_type.lower()])
    subject_name_field = get_field_by_attribute_value(form_model, 'name', 'name')
    es_field_name_for_subject_name = es_questionnaire_field_name(subject_name_field.code, form_model.id)
    subject_short_code_field = get_field_by_attribute_value(form_model, 'name', 'short_code')
    es_field_name_for_short_code = es_questionnaire_field_name(subject_short_code_field.code, form_model.id)
    query = elasticutils.S().es(urls=ELASTIC_SEARCH_URL, timeout=ELASTIC_SEARCH_TIMEOUT).indexes(database_name).doctypes(lower(entity_type)) \
        .query(or_={es_field_name_for_subject_name + '__match': search_text,
                    es_field_name_for_subject_name + '_value': search_text,
                    es_field_name_for_short_code + '__match': search_text,
                    es_field_name_for_short_code + '_value': search_text}) \
        .values_dict()
    resp = [{"id": r[es_field_name_for_short_code], "label": r[es_field_name_for_subject_name]} for r in
            query[:min(query.count(), 50)]]
    return HttpResponse(json.dumps(resp))

@valid_web_user
def export_subject(request):
    manager = get_database_manager(request.user)
    organization = get_organization(request)
    local_time_delta = get_country_time_delta(organization.country)
    current_language = get_language()
    subject_type = request.POST.get('subject_type', '').lower()
    project_name = subject_type
    form_model = get_form_model_by_entity_type(manager, [subject_type.lower()])
    query_params = {
                    "start_result_number": 0,
                    "number_of_results": 4000,
                    "order": "",
                    "filter":'identification_number',
                    }

    return SubmissionExporter(form_model, project_name, manager, local_time_delta, current_language, None) \
        .create_excel_response('identification_number', query_params)

def add_codes_sheet(wb, form_code, field_codes):
    codes = [form_code]
    codes.extend(field_codes)
    ws = workbook_add_sheet(wb, [codes], "codes")
    ws.visibility = 1


def get_example_sms_message(fields, form_code):
    return "%s %s" % (form_code, get_example_sms(fields))


def get_example_sms(fields):
    example_sms = ""
    for field in fields:
        example_sms = example_sms + " " + unicode(_('answer')) + str(fields.index(field) + 1)
    return example_sms