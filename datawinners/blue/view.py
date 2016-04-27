import json
import logging
import mimetypes
import os
import re
import traceback
from copy import deepcopy
from tempfile import NamedTemporaryFile

from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.template.defaultfilters import slugify
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_view_exempt, csrf_response_exempt, csrf_exempt
from django.views.generic.base import View
from mangrove.datastore.entity_type import get_unique_id_types

from pyxform.errors import PyXFormError, BindError

from mangrove.errors.MangroveException import ExceedSubmissionLimitException, QuestionAlreadyExistsException
from mangrove.form_model.form_model import get_form_model_by_code
from mangrove.form_model.project import Project
from mangrove.transport.repository.survey_responses import get_survey_response_by_id, get_survey_responses, \
    survey_responses_by_form_model_id
from mangrove.utils.dates import py_datetime_to_js_datestring
from mangrove.transport.xforms.xform import itemset_for
from datawinners import settings
from datawinners.accountmanagement.decorators import session_not_expired, is_not_expired, is_datasender_allowed, \
    project_has_web_device, is_datasender
from datawinners.accountmanagement.models import Organization
from datawinners.activitylog.models import UserActivityLog
from datawinners.blue.error_translation_utils import transform_error_message, translate_odk_message
from datawinners.blue.rules.factory import get_all_rules
from datawinners.blue.xform_bridge import MangroveService, XlsFormParser, XFormTransformer, XFormSubmissionProcessor, \
    get_generated_xform_id_name, XFormImageProcessor
from datawinners.blue.xform_edit.questionnaire import Questionnaire
from datawinners.blue.xform_edit.submission import Submission
from datawinners.blue.xform_edit.validator import Validator
from datawinners.blue.xform_editor import XFormEditor, UnsupportedXformEditException
from datawinners.blue.xform_web_submission_handler import XFormWebSubmissionHandler
from datawinners.common.constant import EDITED_DATA_SUBMISSION_ADV_QUEST, EDITED_QUESTIONNAIRE
from datawinners.feeds.database import get_feeds_database
from datawinners.main.database import get_database_manager
from datawinners.main.utils import get_database_name
from datawinners.project.helper import generate_questionnaire_code, is_project_exist
from datawinners.project.utils import is_quota_reached
from datawinners.project.views.utils import get_form_context
from datawinners.project.views.views import SurveyWebQuestionnaireRequest
from datawinners.questionnaire.questionnaire_builder import QuestionnaireBuilder
from datawinners.search.submission_index import SubmissionSearchStore
from datawinners.settings import EMAIL_HOST_USER, HNI_SUPPORT_EMAIL_ID
from collections import OrderedDict
from datawinners.blue.xlsform_utils import convert_excel_to_dict,\
    convert_json_to_excel
from xmldict import xml_to_dict

logger = logging.getLogger("datawinners.xls-questionnaire")

QUESTIONNAIRE_AS_DICT_FOR_BUILDER = 'questionnaire_as_dict_for_builder'

class ProjectUpload(View):
    @method_decorator(csrf_view_exempt)
    @method_decorator(csrf_response_exempt)
    @method_decorator(login_required)
    @method_decorator(session_not_expired)
    @method_decorator(is_not_expired)
    def dispatch(self, *args, **kwargs):
        return super(ProjectUpload, self).dispatch(*args, **kwargs)

    def post(self, request):
        project_name = request.GET['pname'].strip()
        manager = get_database_manager(request.user)

        try:
            xls_parser_response = _try_parse_xls(manager, request, project_name)

            if isinstance(xls_parser_response, HttpResponse):
                return xls_parser_response

            send_email_if_unique_id_type_question_has_no_registered_unique_ids(xls_parser_response, request,
                                                                               project_name)
            questionnaire_code = generate_questionnaire_code(manager)
            excel_file = _temp_file(request)
            mangrove_service = MangroveService(request, questionnaire_code=questionnaire_code,
                                               project_name=project_name, xls_form=excel_file,
                                               xls_parser_response=xls_parser_response)
            questionnaire_id, form_code = mangrove_service.create_project()

            if not questionnaire_id:
                logger.info("User: %s. Upload Error: %s", request.user.username, "Questionnaire must be unique")

                return HttpResponse(content_type='application/json', content=json.dumps({
                    'success': False,
                    'error_msg': [_("Duplicate labels. All questions (labels) must be unique.")],
                    'message_prefix': _("Sorry! Current version of DataWinners does not support"),
                    'message_suffix': _("Update your XLSForm and upload again.")
                }))

            questionnaire = Project.get(manager, questionnaire_id)
            _save_questionnaire_as_dict_for_builder(questionnaire, excel_file=excel_file)
        except QuestionAlreadyExistsException as e:
            return HttpResponse(content_type='application/json', content=json.dumps({
                'success': False,
                'error_msg': [
                    _(e.message)
                ]
            }))
        return HttpResponse(
            json.dumps(
                {
                    "success": True,
                    "project_name": project_name,
                    "project_id": questionnaire_id,
                    "form_code": form_code
                }),
            content_type='application/json')


class ProjectBuilder(View):

    def _get_pre_computed_questionnaire_as_dict(self, questionnaire):
        try:
            return json.loads(questionnaire.get_attachments(QUESTIONNAIRE_AS_DICT_FOR_BUILDER), object_pairs_hook=OrderedDict)
        except Exception as e: 
            #Expected exception, if file not exist
            logger.info(e.message)
        return None
    
    def _reload_required(self, request):
        reload = request.GET.get("reload", 'false').lower().strip()
        return reload == 'true'
        
    def get(self, request, project_id):
        manager = get_database_manager(request.user)
        questionnaire = Project.get(manager, project_id)
        excel_as_dict = None
        try:
            if not self._reload_required(request): #Switch to handle unexpected failures
                excel_as_dict = self._get_pre_computed_questionnaire_as_dict(questionnaire)
            raw_excel, file_type = questionnaire.has_attachment()[1:]
            if excel_as_dict is None:
                excel_as_dict = convert_excel_to_dict(file_content=raw_excel, file_type=file_type)
                _save_questionnaire_as_dict_for_builder(questionnaire, excel_as_dict)

            return HttpResponse(
                json.dumps(
                    {
                        "project_id": project_id,
                        "questionnaire" : excel_as_dict,
                        "file_type" : file_type,
                        "unique_id_types": get_unique_id_types(manager)
                    }),
                content_type='application/json')
        except Exception as e:
            logger.exception("Exception : \n%s" % e)
            return HttpResponse(
                json.dumps(
                    {
                        "success": False,
                        "project_id": project_id,
                        'reason': 'Unable to fetch questionnaire details',
                        'details': e.message

                    }),
                content_type='application/json')

    def post(self,request, project_id):
        data = request.POST['data']
        file_type = request.POST['file_type']
        is_draft = request.POST['is_draft']
        try:
            excel_as_dict = json.loads(data, object_pairs_hook=OrderedDict)
            if is_draft and is_draft.lower().strip() == 'true':
                manager = get_database_manager(request.user)
                questionnaire = Project.get(manager, project_id)
                _save_questionnaire_as_dict_for_builder(questionnaire, excel_as_dict=excel_as_dict)
                return HttpResponse(
                    json.dumps(
                        {
                            "status": "success",
                            "project_id": project_id,
                            'reason': 'Successfully updated',
                            'details':''
     
                        }),
                    content_type='application/json')
            
            excel_raw_stream = convert_json_to_excel(excel_as_dict, file_type)
            excel_file = _temp_file(request, excel_raw_stream, file_type)
            return _edit_questionnaire(request, project_id, excel_file, excel_as_dict)
 
        except Exception as e:
            logger.exception('Unable to save questionnaire from builder')
            return HttpResponse(
                json.dumps(
                    {
                        "status": "error",
                        "project_id": project_id,
                        'reason': 'Unable to save', #TODO: i18n translation
                        'details': e.message

                    }),
                content_type='application/json')

def _save_questionnaire_as_dict_for_builder(questionnaire, excel_as_dict=None, excel_file=None):
    try:
        if excel_as_dict is None:
            extension = os.path.splitext(excel_file.name)[1]
            if excel_as_dict is None:
                excel_file.seek(0)
                excel_as_dict = convert_excel_to_dict(file_content=excel_file.read(), file_type=extension[1:])
    
        questionnaire.update_attachments(excel_as_dict, attachment_name=QUESTIONNAIRE_AS_DICT_FOR_BUILDER)
    except:
        logger.exception('Unable to pre compute excel as json for Builder')


def _edit_questionnaire(request, project_id, excel_file=None, excel_as_dict=None):
    manager = get_database_manager(request.user)
    questionnaire = Project.get(manager, project_id)
    try:
        xls_parser_response = _try_parse_xls(manager, request, questionnaire.name, excel_file)

        if isinstance(xls_parser_response, HttpResponse):
            return xls_parser_response

        doc = deepcopy(questionnaire._doc)
        doc.xform = MangroveService(request, questionnaire_code=questionnaire.form_code, xls_parser_response=xls_parser_response).xform_with_form_code
        new_questionnaire = Project.new_from_doc(manager, doc)
        QuestionnaireBuilder(new_questionnaire, manager).update_questionnaire_with_questions(xls_parser_response.json_xform_data)
        xform_rules = get_all_rules()
        if excel_file is None:
            excel_file = _temp_file(request)
        else:
            excel_file.seek(0)
        questionnaire_wrapper = Questionnaire(excel_file)
        activity_log_detail = {}
        XFormEditor(Submission(manager, get_database_name(request.user), xform_rules), Validator(xform_rules),
                    questionnaire_wrapper).edit(new_questionnaire, questionnaire, activity_log_detail)
        questionnaire = Project.get(manager, project_id)
        _save_questionnaire_as_dict_for_builder(questionnaire, excel_as_dict, excel_file)
        UserActivityLog().log(request, action=EDITED_QUESTIONNAIRE, project=questionnaire.name,
                              detail=json.dumps(activity_log_detail))

    except UnsupportedXformEditException as e:
        return HttpResponse(content_type='application/json', content=json.dumps({
            'success': False,
            'unsupported': True,
            'error_msg': [
                _("Unsupported edit operation")
            ],
            "status": "error",
            'reason': "Unsupported edit operation", #TODO: i18n translation
            'details': e.message
        }))
    except QuestionAlreadyExistsException as e:
        return HttpResponse(content_type='application/json', content=json.dumps({
            'success': False,
            'error_msg': [
                _(e.message)
            ],
            "status": "error",
            'reason': "Save Failed", #TODO: i18n translation
            'details': _(e.message)
        }))
    return HttpResponse(
        json.dumps({
            "success": True,
            "status": "success",
            'reason': 'Successfully updated' #TODO: i18n translation
        }),
        content_type='application/json'
    )


class ProjectUpdate(View):
    @method_decorator(csrf_view_exempt)
    @method_decorator(csrf_response_exempt)
    @method_decorator(login_required)
    @method_decorator(session_not_expired)
    @method_decorator(is_not_expired)
    @method_decorator(is_datasender)
    def dispatch(self, *args, **kwargs):
        return super(ProjectUpdate, self).dispatch(*args, **kwargs)

    def recreate_submissions_mapping(self, manager, questionnaire):
        SubmissionSearchStore(manager, questionnaire, None).recreate_elastic_store()

    def post(self, request, project_id):
        if request.GET["edit"] == 'true':
            return _edit_questionnaire(request, project_id)

        return self._overwrite(project_id, request)

    def _overwrite(self, project_id, request):
        manager = get_database_manager(request.user)
        questionnaire = Project.get(manager, project_id)
        xls_parser_response = _try_parse_xls(manager, request, questionnaire.name)
        if isinstance(xls_parser_response, HttpResponse):
            return xls_parser_response
        send_email_if_unique_id_type_question_has_no_registered_unique_ids(xls_parser_response, request,
                                                                           questionnaire.name)
        mangrove_service = MangroveService(request, questionnaire_code=questionnaire.form_code,
                                           project_name=questionnaire.name, xls_parser_response=xls_parser_response)
        questionnaire.xform = mangrove_service.xform_with_form_code
        QuestionnaireBuilder(questionnaire, manager).update_questionnaire_with_questions(
            xls_parser_response.json_xform_data)
        questionnaire.update_media_field_flag()
        questionnaire.save(process_post_update=False)
        UserActivityLog().log(self.request, action=EDITED_QUESTIONNAIRE, project=questionnaire.name,
                              detail=questionnaire.name)
        tmp_file = _temp_file(request)
        base_name, extension = os.path.splitext(tmp_file.name)
        questionnaire.update_attachments(tmp_file, 'questionnaire%s' % extension)
        questionnaire.update_external_itemset(mangrove_service.itemsets_csv)
        self._purge_submissions(manager, questionnaire)
        self._purge_feed_documents(questionnaire, request)
        self._purge_media_details_documents(manager, questionnaire)
        self.recreate_submissions_mapping(manager, questionnaire)
        if xls_parser_response.info:
            info_list = list(xls_parser_response.info)
            logger.info("User: %s. Edit upload Errors: %s", request.user.username, json.dumps(info_list))
            return HttpResponse(content_type='application/json', content=json.dumps({
                'success': True,
                'information': info_list,
            }))
        return HttpResponse(
            json.dumps(
                {
                    "success": True,
                    "project_name": questionnaire.name,
                    "project_id": questionnaire.id,
                    "file_name": "%s%s" % (slugify(questionnaire.name), extension),
                    # "xls_dict": XlsProjectParser().parse(file_content)
                }),
            content_type='application/json')

    def _purge_feed_documents(self, questionnaire, request):
        feed_dbm = get_feeds_database(request.user)
        rows = feed_dbm.view.questionnaire_feed(startkey=[questionnaire.form_code],
                                                endkey=[questionnaire.form_code, {}], include_docs=True)
        for row in rows:
            feed_dbm.database.delete(row['doc'])

    def _purge_submissions(self, manager, questionnaire):
        survey_responses = survey_responses_by_form_model_id(manager, questionnaire.id)
        for survey_response in survey_responses:
            data_record = survey_response.data_record
            if data_record:
                data_record.delete()

            survey_response.delete()

    def _purge_media_details_documents(self, dbm, questionnaire):
        media_details_docs = dbm.database.iterview("all_media_details/all_media_details", 1000, reduce=False,
                                                   include_docs=True, key=questionnaire.id)
        for media_detail_row in media_details_docs:
            dbm.database.delete(media_detail_row['doc'])


@login_required
@session_not_expired
@is_project_exist
@is_datasender_allowed
@project_has_web_device
@is_not_expired
def new_xform_submission_get(request, project_id):
    survey_request = SurveyWebXformQuestionnaireRequest(request, project_id, XFormSubmissionProcessor())
    if request.method == 'GET':
        return survey_request.response_for_get_request()


@csrf_exempt
def new_xform_submission_post(request):
    try:
        response = XFormWebSubmissionHandler(request=request).create_new_submission_response()
        response['Location'] = request.build_absolute_uri(request.path)
        return response
    except ExceedSubmissionLimitException as e:
        return HttpResponse(json.dumps({'error_message': e.message}))
    except Exception as e:
        logger.exception("Exception in submission : \n%s" % e)
        send_email_on_exception(request.user, "New Web Submission", traceback.format_exc(),
                                additional_details={'submitted-data': request.POST['form_data']})
        return HttpResponseBadRequest()


@csrf_exempt
def edit_xform_submission_post(request, survey_response_id):
    manager = get_database_manager(request.user)
    survey_response = get_survey_response_by_id(manager, survey_response_id)
    activity_log = UserActivityLog()
    questionnaire = Project.get(manager, survey_response.form_model_id)
    old_data = survey_response._doc.values
    new_data = (xml_to_dict(str(request.POST['form_data'])))
    new_data_dict = new_data.values()[0]
    details = dict()
    question = ''
    for key, value in new_data_dict.iteritems():
        if key in old_data and key not in {"intro", "meta", "form_code"}:
            if new_data_dict[key] != old_data[key]:
                details.update({key: {'old_data': old_data[key], 'new_data': new_data_dict[key]}})
    edit_details = dict()

    for key, value in details.iteritems():
        for field in questionnaire._form_fields:
            if field.code == key:
                question = field.label
        if isinstance(value['new_data'],dict): #if its a repeat with only 1 node
            for q, val in value['new_data'].items():
                if q in value['old_data'][0]:
                    if value['old_data'][0][q] != value['new_data'][q]:
                        for field in questionnaire._form_fields:
                            if field.code == key:
                                if field.fields:
                                    for f in field.fields:
                                        if f.code == q:
                                            question = f.label
                                            edit_details.update({q: {'question':question, 'old': value['old_data'][0][q], 'new': value['new_data'][q]}})
                                else:
                                    question = field.label
                                    edit_details.update({q: {'question':question, 'old': value['old_data'][0][q], 'new': value['new_data'][q]}})

        elif isinstance(value['new_data'],list): #if repeat with more than 1 node
            if value['old_data'] != value['new_data']:
                for index, i in enumerate(value['new_data']):
                    for key, val in i.items():
                        if key in value['old_data'][index]:
                            if val != value['old_data'][index][key]:
                                edit_details.update({index: {'question': question, 'old': value['old_data'][index][key], 'new': val}})
        else:
                edit_details.update({key: {'question':question, 'old': old_data[key], 'new': new_data_dict[key]}})

    activity_log.log(request, action=EDITED_DATA_SUBMISSION_ADV_QUEST,  project=questionnaire.name, detail=json.dumps(edit_details))
    try:
        return XFormWebSubmissionHandler(request=request). \
            update_submission_response(survey_response_id)
    except Exception as e:
        logger.exception("Exception in submission : \n%s" % e)
        send_email_on_exception(request.user, "Edit Web Submission", traceback.format_exc(),
                                additional_details={'survey_response_id': survey_response_id,
                                                    'submitted-data': request.POST['form_data']
                                                    })
        return HttpResponseBadRequest()


@login_required
@session_not_expired
@is_datasender
@is_not_expired
def project_download(request):
    project_name = request.POST.get(u"project_name")
    questionnaire_code = request.POST.get(u'questionnaire_code')

    manager = get_database_manager(request.user)
    questionnaire = get_form_model_by_code(manager, questionnaire_code)
    project = Project.from_form_model(questionnaire)
    try:
        raw_excel, file_extension = project.has_attachment()[1:]

        response = HttpResponse(mimetype="application/vnd.ms-excel", content=raw_excel)
        response['Content-Disposition'] = 'attachment; filename="%s.%s"' % (slugify(project_name), file_extension)

    except LookupError:
        response = HttpResponse(status=404)

    return response


@login_required
@session_not_expired
@is_datasender
@is_not_expired
def get_attachment(request, document_id, attachment_name):
    manager = get_database_manager(request.user)
    return HttpResponse(manager.get_attachments(document_id, attachment_name=attachment_name))


def send_email_if_unique_id_type_question_has_no_registered_unique_ids(xls_parser_response, request,
                                                                       questionnaire_name):
    if not xls_parser_response.info:
        # no info present
        return

    if xls_parser_response.info and ugettext('Making submission via Smartphone will not be possible.') not in \
            list(xls_parser_response.info)[0]:
        # 'unique id number not preset' info not present
        return

    send_no_registered_unique_id_for_type_email(request.user, questionnaire_name)


@login_required
@session_not_expired
@is_datasender
@is_not_expired
def attachment_download(request, document_id, attachment_name):
    manager = get_database_manager(request.user)
    try:
        raw_file = manager.get_attachments(document_id, attachment_name=attachment_name)
        mime_type = mimetypes.guess_type(os.path.basename(attachment_name))[0]
        response = HttpResponse(raw_file, mimetype=mime_type)
        file_extension = attachment_name.split('.')[-1]
        file_name_slugifed = "%s.%s" % (slugify(".".join(attachment_name.split('.')[:-1])), file_extension)
        response['Content-Disposition'] = 'attachment; filename="%s"' % file_name_slugifed
        return response
    except LookupError:
        return HttpResponse(status=404)


def send_email_on_exception(user, error_type, stack_trace, additional_details=None):
    email_message = ''
    profile = user.get_profile()
    organization = Organization.objects.get(org_id=profile.org_id)
    file_contents = additional_details.pop('file_contents') if additional_details and additional_details.get(
        'file_contents') else None
    submitted_data = additional_details.pop('submitted-data') if additional_details and additional_details.get(
        'submitted-data') else None
    email_message += '\nError Scenario : %s (%s)\n' % (organization.name, profile.org_id)
    email_message += '\nOrganization Details : %s (%s)' % (organization.name, profile.org_id)
    email_message += '\nUser Email Id : %s\n' % user.username
    email_message += '\n%s' % stack_trace
    email = EmailMessage(subject="[ERROR] %s : %s" % (error_type, organization.name),
                         body=repr(re.sub("\n", "<br/>", email_message)),
                         from_email=EMAIL_HOST_USER, to=[HNI_SUPPORT_EMAIL_ID])
    email.content_subtype = "html"

    if file_contents:
        email.attach("errored_excel.xls", content=file_contents, mimetype='application/ms-excel')

    if submitted_data:
        email.attach("submitted-data.xml", content=submitted_data, mimetype='text/xml')

    email.send()


def send_no_registered_unique_id_for_type_email(user, questionnaire_name):
    email_message = "Questionnaire '%s' created by '%s' has one or more unique-id question(s) with no registered unique-ids." % (
    questionnaire_name, user.email)
    profile = user.get_profile()
    organization = Organization.objects.get(org_id=profile.org_id)
    email = EmailMessage(subject="[INFO - No regd. unique-ids] : %s" % organization.name,
                         body=re.sub("\n", "<br/>", email_message),
                         from_email=EMAIL_HOST_USER, to=[HNI_SUPPORT_EMAIL_ID])
    email.content_subtype = "html"

    email.send()


EXCEL_UPLOAD_FILE_SIZE = 10485760  # 10MB


def _perform_file_validations(request):
    errors = []
    if request.GET and request.GET.get("qqfile"):
        file_extension = _file_extension(request)
        if file_extension not in [".xls", ".xlsx"]:
            errors.append(_("Please upload an excel file"))
            return errors, file_extension

    if request.META.get('CONTENT_LENGTH') and int(request.META.get('CONTENT_LENGTH')) > EXCEL_UPLOAD_FILE_SIZE:
        errors.append(_("larger files than 10MB."))
        
    if errors:
        logger.info("User: %s. Edit upload File validation failed: %s. File name: %s, size: %d",
                    request.user.username,
                    json.dumps(errors), request.GET.get("qqfile"), int(request.META.get('CONTENT_LENGTH')))
    
        return HttpResponse(content_type='application/json', content=json.dumps({
            'success': False,
            'error_msg': errors
        }))

def _file_extension(request):
    return os.path.splitext(request.GET["qqfile"])[1]


def _temp_file(request, input_stream=None, file_type=None):
    tmp_file = None
    if request.GET and request.GET.get('qqfile'):
        tmp_file = NamedTemporaryFile(delete=True, suffix=_file_extension(request))
        tmp_file.write(request.raw_post_data)
        tmp_file.seek(0)
    if input_stream:
        tmp_file = NamedTemporaryFile(delete=True, suffix='.'+file_type)
        tmp_file.write(input_stream.getvalue())
        tmp_file.seek(0)
        
    return tmp_file


def _try_parse_xls(manager, request, questionnaire_name, excel_file=None):
    try:
        file_validation_results = _perform_file_validations(request)
        if isinstance(file_validation_results, HttpResponse):
            return file_validation_results

        if excel_file:
            tmp_file=excel_file
        else:
            tmp_file = _temp_file(request)

        xls_parser_response = XlsFormParser(tmp_file, questionnaire_name, manager).parse()

        profile = request.user.get_profile()
        organization = Organization.objects.get(org_id=profile.org_id)
        if xls_parser_response.is_multiple_languages:
            logger.info("Edit Questionnaire %s with Multi Language support for organization : %s(%s) and email: %s",
                        questionnaire_name, organization.name, profile.org_id, profile.user.email)

        if xls_parser_response.errors:
            info_list = list(xls_parser_response.errors)
            logger.info("User: %s. Edit upload Errors: %s", request.user.username, json.dumps(info_list))

            return HttpResponse(content_type='application/json', content=json.dumps({
                'success': False,
                'error_msg': info_list,
                'message_prefix': _("Sorry! Current version of DataWinners does not support"),
                'message_suffix': _("Update your XLSForm and upload again.")
            }))

    except BindError as e:
        return HttpResponse(content_type='application/json', content=json.dumps({
                'success': False,
                'status': 'error',
                'errors': [
                    {
                        e.field.name: {
                            e.attribute: e.custom_message
                        }
                    }
                ],
                'reason': 'Save Failed', #TODO: i18n translation
                'details': ''
            }))

    except PyXFormError as e:
        logger.info("User: %s. Upload Error: %s", request.user.username, e.message)

        message = transform_error_message(e.message)
        if 'name_type_error' in message or 'choice_name_type_error' in message:
            if 'choice_name_type_error' in message:
                message_prefix = _(
                    "On your \"choices\" sheet the first and second column must be \"list_name\" and \"name\".  Possible errors:")
            else:
                message_prefix = _(
                    "On your \"survey\" sheet the first and second column must be \"type\" and \"name\".  Possible errors:")
            return HttpResponse(content_type='application/json', content=json.dumps({
                'success': False,
                'error_msg': [_("Columns are missing"), _("Column name is misspelled"),
                              _("Additional space in column name")],
                'message_prefix': message_prefix,
                'message_suffix': _("Update your XLSForm and upload again.")
            }))
        else:
            return HttpResponse(content_type='application/json', content=json.dumps({
                'success': False,
                'error_msg': [message if message else ugettext(
                    "all XLSForm features. Please check the list of unsupported features.")]
            }))

    except UnicodeDecodeError as e:
        logger.info("User: %s. Upload Error: %s", request.user.username, e.message)

        return HttpResponse(content_type='application/json', content=json.dumps({
            'success': False,
            'error_msg': [
                _(
                    "Check your columns for errors.<br>There are missing symbols (like $ for relevant or calculate) or incorrect characters<br>") + _(
                    "Update your XLSForm and upload again.")],
        }))

    except Exception as e:

        logger.info("User: %s. Edit Upload Exception message: %s", request.user.username, e.message)

        message = e.message if e.message else _("Some error in excel")
        odk_message = ''
        if not 'ODK Validate Errors:' in e.message:
            send_email_on_exception(request.user, "Questionnaire Edit", traceback.format_exc(),
                                    additional_details={'file_contents': request.raw_post_data})
        else:
            odk_message = translate_odk_message(e.message)
        message = odk_message if odk_message else message
        return HttpResponse(content_type='application/json', content=json.dumps({
            'error_msg': [message], 'success': False,
        }))

    return xls_parser_response


@login_required
@session_not_expired
@is_project_exist
@is_not_expired
def external_itemset(request, questionnaire_code=None):
    request_user = request.user
    return itemset_for(get_database_manager(request_user), questionnaire_code)


class SurveyWebXformQuestionnaireRequest(SurveyWebQuestionnaireRequest):
    def __init__(self, request, project_id=None, submissionProcessor=None):
        SurveyWebQuestionnaireRequest.__init__(self, request, project_id)
        self.submissionProcessor = submissionProcessor
        self.is_data_sender = request.user.get_profile().reporter

    @property
    def template(self):
        return 'project/xform_web_questionnaire_datasender.html' if self.is_data_sender \
            else 'project/xform_web_questionnaire.html'

    def response_for_get_request(self, initial_data=None, is_update=False):
        dashboard_page = settings.HOME_PAGE + "?deleted=true"
        if self.questionnaire.is_void():
            return HttpResponseRedirect(dashboard_page)
        questionnaire_form = self.form(initial_data=initial_data)
        form_context = get_form_context(self.questionnaire, questionnaire_form,
                                        self.manager, self.hide_link_class, self.disable_link_class,
                                        is_update=is_update)
        if self.questionnaire.xform:
            form_context.update(
                {
                    'xform_xml': re.sub(r"\n", " ", XFormTransformer(
                        self.questionnaire.do_enrich_xform()).transform())
                })
            form_context.update({'is_advance_questionnaire': True})
            form_context.update({'external_itemset_url': self._get_itemset_url(self.questionnaire)})
            form_context.update({'submission_create_url': reverse('new_web_submission')})
        form_context.update({'is_quota_reached': is_quota_reached(self.request)})
        return render_to_response(self.template, form_context, context_instance=RequestContext(self.request))

    def _model_str_of(self, survey_response_id, project_name):
        # TODO this can be avoided
        survey_response = get_survey_response_by_id(self.manager, survey_response_id)
        xform_instance_xml = self.submissionProcessor. \
            get_model_edit_str(self.questionnaire.fields, survey_response.values, project_name,
                               self.questionnaire.form_code, )
        return xform_instance_xml

    def response_for_xform_edit_get_request(self, survey_response_id):

        # todo delete/refactor this block
        dashboard_page = settings.HOME_PAGE + "?deleted=true"
        if self.questionnaire.is_void():
            return HttpResponseRedirect(dashboard_page)
        questionnaire_form = self.form(initial_data=None)
        form_context = get_form_context(self.questionnaire, questionnaire_form,
                                        self.manager, self.hide_link_class, self.disable_link_class, is_update=False)

        if self.questionnaire.xform:
            form_context.update({'survey_response_id': survey_response_id})
            # xform_transformer = XFormTransformer(self.questionnaire.xform)
            form_context.update({'xform_xml': re.sub(r"\n", " ", XFormTransformer(
                self.questionnaire.do_enrich_xform()).transform())})
            form_context.update(
                {'edit_model_str': self._model_str_of(survey_response_id,
                                                      get_generated_xform_id_name(self.questionnaire.xform))})
            form_context.update({'external_itemset_url': self._get_itemset_url(self.questionnaire)})
            form_context.update({'submission_update_url': reverse('update_web_submission',
                                                                  kwargs={'survey_response_id': survey_response_id})})
            form_context.update({'is_advance_questionnaire': True})

        form_context.update({'is_quota_reached': is_quota_reached(self.request)})
        return render_to_response(self.template, form_context, context_instance=RequestContext(self.request))

    def _to_html(self, data):
        html = '<ul>'
        for key, value in data.items():
            if isinstance(value, dict):
                continue
            html += '<li>' + key + ' : '
            if isinstance(value, list):
                for v in value:
                    html += self._to_html(v)
            else:
                html += value if value else ""
            html += '</li>'

        html += '</ul>'
        return html

    def get_submissions(self):
        submission_list = []
        submissions = get_survey_responses(self.manager, self.questionnaire.id, None, None,
                                           view_name="undeleted_survey_response")
        for submission in submissions:
            submission_list.append({'submission_uuid': submission.id,
                                    'version': submission.version,
                                    'project_uuid': self.questionnaire.id,
                                    'created': py_datetime_to_js_datestring(submission.created)
                                    })
        return submission_list

    def get_submission(self, submission_uuid):
        submission = get_survey_response_by_id(self.manager, submission_uuid)
        imageProcessor = XFormImageProcessor()

        return {'submission_uuid': submission.id,
                'version': submission.version,
                'project_uuid': self.questionnaire.id,
                'created': py_datetime_to_js_datestring(submission.created),
                'media_file_names_string': imageProcessor
                    .get_media_files_str(self.questionnaire.fields, submission.values),
                'xml': self._model_str_of(submission.id, get_generated_xform_id_name(self.questionnaire.xform)),
                'data': json.dumps(submission.values)
                }

    def _get_itemset_url(self, questionnaire):
        xform_base_url = self.request.build_absolute_uri('/xlsform')
        return xform_base_url + '/itemset/' + questionnaire.id
