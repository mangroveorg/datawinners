import json
import logging
import re
from tempfile import NamedTemporaryFile
import traceback

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext
from django.views.decorators.csrf import csrf_view_exempt, csrf_response_exempt, csrf_exempt
from django.views.generic.base import View
from django.template.defaultfilters import slugify
from pyxform.errors import PyXFormError
import xlwt
from datawinners.accountmanagement.models import Organization
from datawinners.monitor.carbon_pusher import send_to_carbon
from datawinners.monitor.metric_path import create_path
from datawinners.settings import EMAIL_HOST_USER, HNI_SUPPORT_EMAIL_ID
from django.core.mail import EmailMessage

from datawinners.feeds.database import get_feeds_database
from datawinners.search.submission_index import SubmissionSearchStore
from mangrove.errors.MangroveException import ExceedSubmissionLimitException, QuestionAlreadyExistsException
from datawinners import settings
from datawinners.accountmanagement.decorators import session_not_expired, is_not_expired, is_datasender_allowed, \
    project_has_web_device, is_datasender
from datawinners.blue.xform_bridge import MangroveService, XlsFormParser, XFormTransformer, XFormSubmissionProcessor, \
    XlsProjectParser, get_generated_xform_id_name
from datawinners.blue.xform_web_submission_handler import XFormWebSubmissionHandler
from datawinners.main.database import get_database_manager
from datawinners.project.helper import generate_questionnaire_code, is_project_exist
from datawinners.project.models import Project
from datawinners.project.utils import is_quota_reached
from datawinners.project.views.utils import get_form_context
from datawinners.project.views.views import SurveyWebQuestionnaireRequest
from datawinners.questionnaire.questionnaire_builder import QuestionnaireBuilder
from datawinners.utils import workbook_add_sheet
from mangrove.form_model.form_model import get_form_model_by_code
from mangrove.transport.repository.survey_responses import get_survey_response_by_id, get_survey_responses, \
    survey_responses_by_form_code
from mangrove.utils.dates import py_datetime_to_js_datestring


logger = logging.getLogger("datawinners.xlsform")


class ProjectUpload(View):
    @method_decorator(csrf_view_exempt)
    @method_decorator(csrf_response_exempt)
    @method_decorator(login_required)
    @method_decorator(session_not_expired)
    @method_decorator(is_not_expired)
    def dispatch(self, *args, **kwargs):
        return super(ProjectUpload, self).dispatch(*args, **kwargs)

    def post(self, request):
        file_content = None
        try:
            file_errors = _perform_file_validations(request)
            if file_errors:
                return HttpResponse(content_type='application/json', content=json.dumps({
                    'success': False,
                    'error_msg': list(file_errors)
                }))
            file_content = request.raw_post_data
            tmp_file = NamedTemporaryFile(delete=True, suffix=".xls")
            tmp_file.write(file_content)
            tmp_file.seek(0)

            manager = get_database_manager(request.user)
            questionnaire_code = generate_questionnaire_code(manager)
            project_name = request.GET['pname']

            errors, xform_as_string, json_xform_data = XlsFormParser(tmp_file, project_name).parse()
            if errors:
                return HttpResponse(content_type='application/json', content=json.dumps({
                    'success': False,
                    'error_msg': list(errors)
                }))

            mangrove_service = MangroveService(request.user, xform_as_string, json_xform_data,
                                               questionnaire_code=questionnaire_code, project_name=project_name,
                                               xls_form=file_content)
            questionnaire_id = mangrove_service.create_project()

        except (PyXFormError,QuestionAlreadyExistsException) as e :
            return HttpResponse(content_type='application/json', content=json.dumps({
                'success': False,
                'error_msg': [e.message if e.message else ugettext("Errors in excel")]
            }))

        except Exception as e:
            if not 'ODK Validate Errors:' in e.message:
                send_email_on_exception(request.user,"Questionnaire Upload",traceback.format_exc(),additional_details={'file_contents':file_content})
            return HttpResponse(content_type='application/json', content=json.dumps({
                'success': False,
                'error_msg': [e.message if e.message else ugettext("Errors in excel")]
            }))

        if not questionnaire_id:
            return HttpResponse(json.dumps(
                {'success': False, 'error_msg': [ugettext("Questionnaire with same name already exists.")]}), content_type='application/json')

        return HttpResponse(
            json.dumps(
                {
                    "success": True,
                    "project_name": project_name,
                    "project_id": questionnaire_id,
                    "xls_dict": XlsProjectParser().parse(file_content)
                }),
            content_type='application/json')


class ProjectUpdate(View):
    @method_decorator(csrf_view_exempt)
    @method_decorator(csrf_response_exempt)
    @method_decorator(login_required)
    @method_decorator(session_not_expired)
    @method_decorator(is_not_expired)
    @method_decorator(is_datasender)
    def dispatch(self, *args, **kwargs):
        return super(ProjectUpdate, self).dispatch(*args, **kwargs)

    def _purge_feed_documents(self, questionnaire, request):
        feed_dbm = get_feeds_database(request.user)
        rows = feed_dbm.view.questionnaire_feed(startkey=[questionnaire.form_code],
                                                endkey=[questionnaire.form_code, {}], include_docs=True)
        for row in rows:
            feed_dbm.database.delete(row['doc'])

    def _purge_submissions(self, manager, questionnaire):
        survey_responses = survey_responses_by_form_code(manager, questionnaire.form_code)
        for survey_response in survey_responses:
            survey_response.data_record.delete()
            survey_response.delete()

    def recreate_submissions_mapping(self, manager, questionnaire):
        SubmissionSearchStore(manager, questionnaire, None).recreate_elastic_store()

    def post(self, request, project_id):
        manager = get_database_manager(request.user)
        questionnaire = Project.get(manager, project_id)
        file_content = None
        try:
            file_content = request.raw_post_data
            tmp_file = NamedTemporaryFile(delete=True, suffix=".xls")
            tmp_file.write(file_content)
            tmp_file.seek(0)

            errors, xform_as_string, json_xform_data = XlsFormParser(tmp_file, questionnaire.name).parse()

            if errors:
                return HttpResponse(content_type='application/json', content=json.dumps({
                    'success': False,
                    'error_msg': list(errors)
                }))

            mangrove_service = MangroveService(request.user, xform_as_string, json_xform_data,
                                               questionnaire_code=questionnaire.form_code,
                                               project_name=questionnaire.name)

            QuestionnaireBuilder(questionnaire, manager).update_questionnaire_with_questions(json_xform_data)
            questionnaire.xform = mangrove_service.xform_with_form_code

            tmp_file.seek(0)
            questionnaire.save(process_post_update=False)
            questionnaire.add_attachments(tmp_file, 'questionnaire.xls')

            self._purge_submissions(manager, questionnaire)
            self._purge_feed_documents(questionnaire, request)
            self.recreate_submissions_mapping(manager, questionnaire)

        except (PyXFormError,QuestionAlreadyExistsException) as e :
            return HttpResponse(content_type='application/json', content=json.dumps({
                'success': False,
                'error_msg': [e.message if e.message else ugettext("Errors in excel")]
            }))

        except Exception as e:
            if not 'ODK Validate Errors:' in e.message:
                send_email_on_exception(request.user,"Questionnaire Edit",traceback.format_exc(),additional_details={'file_contents':file_content})
            message = e.message if e.message else "Some error in excel"
            return HttpResponse(content_type='application/json', content=json.dumps({
                'error_msg': [message], 'success': False
            }))

        return HttpResponse(
            json.dumps(
                {
                    "success": True,
                    "project_name": questionnaire.name,
                    "project_id": questionnaire.id,
                    "xls_dict": XlsProjectParser().parse(file_content)
                }),
            content_type='application/json')


@login_required
@session_not_expired
@csrf_exempt
@is_not_expired
def upload_project(request):
    return render_to_response('project/xform_project.html')


@login_required
@session_not_expired
@is_project_exist
@is_datasender_allowed
@project_has_web_device
@is_not_expired
def new_xform_submission_get(request, project_id=None):
    survey_request = SurveyWebXformQuestionnaireRequest(request, project_id, XFormSubmissionProcessor())
    if request.method == 'GET':
        return survey_request.response_for_get_request()


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
                                        self.manager, self.hide_link_class, self.disable_link_class, is_update)
        if self.questionnaire.xform:
            form_context.update(
                {'xform_xml': re.sub(r"\n", " ", XFormTransformer(self.questionnaire.xform).transform())})
            form_context.update({'is_advance_questionnaire': True})
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
                                        self.manager, self.hide_link_class, self.disable_link_class, False)

        if self.questionnaire.xform:
            form_context.update({'survey_response_id': survey_response_id})
            xform_transformer = XFormTransformer(self.questionnaire.xform)
            form_context.update({'xform_xml': re.sub(r"\n", " ", xform_transformer.transform())})
            form_context.update(
                {'edit_model_str': self._model_str_of(survey_response_id,
                                                      get_generated_xform_id_name(self.questionnaire.xform))})
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
        submissions = get_survey_responses(self.manager, self.questionnaire.form_code, None, None,
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

        return {'submission_uuid': submission.id,
                'version': submission.version,
                'project_uuid': self.questionnaire.id,
                'created': py_datetime_to_js_datestring(submission.created),
                'xml': self._model_str_of(submission.id, self.questionnaire.name),
                'html': self._to_html(submission.values)
        }


@csrf_exempt
def new_xform_submission_post(request):
    try:
        send_to_carbon(create_path('submissions.web.advanced'), 1)
        response = XFormWebSubmissionHandler(request.user, request=request).create_new_submission_response()
        response['Location'] = request.build_absolute_uri(request.path)
        return response
    except ExceedSubmissionLimitException as e:
        return HttpResponse(json.dumps({'error_message': e.message}))
    except Exception as e:
        logger.exception("Exception in submission : \n%s" % e)
        send_email_on_exception(request.user,"New Web Submission",traceback.format_exc())
        return HttpResponseBadRequest()


@csrf_exempt
def edit_xform_submission_post(request, survey_response_id):
    try:
        send_to_carbon(create_path('submissions.web.advanced'), 1)
        return XFormWebSubmissionHandler(request.user, request=request). \
            update_submission_response(survey_response_id)
    except Exception as e:
        logger.exception("Exception in submission : \n%s" % e)
        send_email_on_exception(request.user,"Edit Web Submission",traceback.format_exc(),additional_details={'survey_response_id':survey_response_id})
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

    try:
        raw_excel = questionnaire.get_attachments('questionnaire.xls')
        excel_transformed = XlsProjectParser().parse(raw_excel)

        response = HttpResponse(mimetype="application/vnd.ms-excel")
        response['Content-Disposition'] = 'attachment; filename="%s.xls"' % slugify(project_name)

        wb = xlwt.Workbook()
        for sheet in excel_transformed:
            workbook_add_sheet(wb, excel_transformed[sheet], sheet)
        wb.save(response)
    except LookupError as e:
        response = HttpResponse(status=404)

    return response


def send_email_on_exception(user,error_type,stack_trace,additional_details=None):
    email_message = ''
    profile = user.get_profile()
    organization = Organization.objects.get(org_id=profile.org_id)
    file_contents = additional_details.pop('file_contents') if additional_details and additional_details.get('file_contents') else None
    email_message += '\nError Scenario : %s (%s)\n' % (organization.name, profile.org_id)
    email_message += '\nOrganization Details : %s (%s)' % (organization.name, profile.org_id)
    email_message += '\nUser Email Id : %s\n' % user.username
    email_message += '\n%s' % stack_trace
    email = EmailMessage(subject="[ERROR] %s" % error_type, body=repr(re.sub("\n","<br/>",email_message)),
                         from_email=EMAIL_HOST_USER, to=[HNI_SUPPORT_EMAIL_ID])
    email.content_subtype = "html"

    if file_contents:
        email.attach("errored_excel.xls",content=file_contents,mimetype='application/ms-excel')


    email.send()


def _perform_file_validations(request):
    errors = []
    if request.GET and request.GET.get("qqfile"):
        import os
        file_extension = os.path.splitext(request.GET["qqfile"])[1]
        if(file_extension not in [".xls",".xlsx"]):
            errors.append("Please upload an excel file")
    EXCEL_UPLOAD_FILE_SIZE = 10485760 # 10MB
    if request.META.get('CONTENT_LENGTH') and int(request.META.get('CONTENT_LENGTH')) > EXCEL_UPLOAD_FILE_SIZE:
        errors.append("Please upload an excel file less than or equal to 10MB in size")
    return errors