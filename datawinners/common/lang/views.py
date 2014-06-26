from collections import OrderedDict
import json
import re
from django.utils import translation
from datawinners import utils

from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext
from django.views.decorators.csrf import csrf_view_exempt, csrf_response_exempt
from django.views.generic.base import TemplateView, View

from datawinners.accountmanagement.decorators import session_not_expired, is_datasender, is_not_expired
from datawinners.accountmanagement.models import Organization
from datawinners.common.lang.messages import save_questionnaire_custom_messages, save_account_wide_sms_messages
from datawinners.common.lang.utils import questionnaire_customized_message_details, get_available_project_languages, create_new_questionnaire_reply_message_template, DuplicateLanguageException, account_wide_customized_message_details, \
    questionnaire_reply_default_messages, account_wide_sms_default_messages
from datawinners.common.lang.utils import ERROR_MSG_MISMATCHED_SYS_VARIABLE
from datawinners.settings import EMAIL_HOST_USER, HNI_SUPPORT_EMAIL_ID
from datawinners.main.database import get_database_manager
from datawinners.utils import get_organization_language


class LanguagesView(TemplateView):
    template_name = 'questionnaire_reply_sms.html'


    def get(self, request, *args, **kwargs):
        dbm = get_database_manager(request.user)
        organization = utils.get_organization(request)
        current_language_code = organization.language
        languages_list = get_available_project_languages(dbm)
        return self.render_to_response({
            "available_languages": json.dumps(languages_list),
            "current_language": current_language_code,
            'active_language': translation.get_language()
        })

    @method_decorator(csrf_view_exempt)
    @method_decorator(csrf_response_exempt)
    @method_decorator(login_required)
    @method_decorator(session_not_expired)
    @method_decorator(is_datasender)
    @method_decorator(is_not_expired)
    def dispatch(self, *args, **kwargs):
        return super(LanguagesView, self).dispatch(*args, **kwargs)


def verify_inconsistency_in_system_variables(dbm, incoming_message_dict, language=None,
                                             is_account_wid_sms=False):
    if is_account_wid_sms:
        existing_message_list = account_wide_customized_message_details(dbm)
    else:
        existing_message_list = questionnaire_customized_message_details(dbm, language)

    existing_msg_dict = {}
    for msg_details in existing_message_list:
        existing_msg_dict.update({msg_details.get('code'): msg_details.get('message')})

    regex = re.compile("\{.*?\}")
    inconsistent_message_codes = []
    for code, message in incoming_message_dict.iteritems():
        modified_system_variable_list = regex.findall(message)
        existing_system_variable_list = regex.findall(existing_msg_dict[code])
        if not modified_system_variable_list == existing_system_variable_list:
            inconsistent_message_codes.append(code)

    errorred_message_list = []
    if inconsistent_message_codes:
        errorred_message_list = existing_message_list
        for msg_details in errorred_message_list:
            if msg_details.get('code') in inconsistent_message_codes:
                msg_details.update({'error': ERROR_MSG_MISMATCHED_SYS_VARIABLE, 'valid': False})
    return errorred_message_list


def _send_error_email(error_message_dict, request):
    email_message = ''
    profile = request.user.get_profile()
    organization = Organization.objects.get(org_id=profile.org_id)
    email_message += '\norganization_details : %s (%s)' % (organization.name, profile.org_id)
    email_message += '\nuser_email_id : %s' % request.user.username
    email_message += '\nbrowser : %s' % request.META.get('HTTP_USER_AGENT')
    email_message += '\nmessages : %s' % repr(error_message_dict)
    email = EmailMessage(subject="[ERROR] Modified system variable", body=repr(email_message),
                         from_email=EMAIL_HOST_USER, to=[HNI_SUPPORT_EMAIL_ID])
    email.send()


class LanguagesAjaxView(View):
    def get(self, request, *args, **kwargs):
        dbm = get_database_manager(request.user)
        return HttpResponse(json.dumps(questionnaire_customized_message_details(dbm, request.GET.get('language'))),
                            content_type="text/javascript")

    def post(self, request, *args, **kwargs):
        data = json.loads(request.POST.get("data", {}))
        dbm = get_database_manager(request.user)
        if data.get('isMessageModified'):
            modified_messages = data.get("messages")
            language = data.get('language')
            questionnaire_customized_message_dict = get_reply_message_dictionary(modified_messages)

            error_message_dict = verify_inconsistency_in_system_variables(dbm,
                                                                          questionnaire_customized_message_dict,
                                                                          language)
            if error_message_dict:
                _send_error_email(modified_messages, request)
                return HttpResponse(json.dumps({"success": False, "messages": error_message_dict}))

            save_questionnaire_custom_messages(dbm, language, questionnaire_customized_message_dict)
        return HttpResponse(json.dumps({"success": True, "message": ugettext("Changes saved successfully.")}))

    @method_decorator(login_required)
    @method_decorator(session_not_expired)
    @method_decorator(is_datasender)
    @method_decorator(is_not_expired)
    def dispatch(self, *args, **kwargs):
        return super(LanguagesAjaxView, self).dispatch(*args, **kwargs)


class LanguageCreateView(View):
    def post(self, request, *args, **kwargs):
        language_name = request.POST.get('language_name')
        try:
            language_code = create_new_questionnaire_reply_message_template(get_database_manager(request.user),
                                                                            language_name)
            return HttpResponse(json.dumps({"language_code": language_code, "language_name": language_name}))
        except DuplicateLanguageException as e:
            return HttpResponse(json.dumps({"language_code": None, "message": e.message}))

    @method_decorator(csrf_view_exempt)
    @method_decorator(csrf_response_exempt)
    @method_decorator(login_required)
    @method_decorator(session_not_expired)
    @method_decorator(is_datasender)
    @method_decorator(is_not_expired)
    def dispatch(self, *args, **kwargs):
        return super(LanguageCreateView, self).dispatch(*args, **kwargs)


def get_reply_message_dictionary(message_list):
    customized_message_dict = OrderedDict()
    for customized_message in message_list:
        customized_message_dict.update({customized_message.get("code"): customized_message.get("message")})
    return customized_message_dict


class AccountMessagesView(TemplateView):
    template_name = 'account_wide_sms.html'

    def get(self, request, *args, **kwargs):
        dbm = get_database_manager(request.user)
        return self.render_to_response({
            "account_messages": json.dumps(account_wide_customized_message_details(dbm)),
            'active_language': translation.get_language()
        })

    @method_decorator(login_required)
    @method_decorator(session_not_expired)
    @method_decorator(is_datasender)
    @method_decorator(is_not_expired)
    def dispatch(self, *args, **kwargs):
        return super(AccountMessagesView, self).dispatch(*args, **kwargs)


    def post(self, request, *args, **kwargs):
        data = json.loads(request.POST.get("data", {}))
        dbm = get_database_manager(request.user)
        if data.get('isMessageModified'):
            modified_messages = data.get("messages")
            incoming_message_dict = get_reply_message_dictionary(data.get("messages"))
            error_message_dict = verify_inconsistency_in_system_variables(dbm, incoming_message_dict,
                                                                          is_account_wid_sms=True)
            if error_message_dict:
                _send_error_email(modified_messages, request)
                return HttpResponse(json.dumps({"success": False, "messages": error_message_dict}))

            save_account_wide_sms_messages(dbm, incoming_message_dict)

        return HttpResponse(json.dumps({"success": True, "message": ugettext("Changes saved successfully.")}))


@csrf_view_exempt
@csrf_response_exempt
def get_default_messages(request):
    language_code = request.POST.get('code')
    message_code = request.POST.get("message_code")
    if language_code:
        return HttpResponse(questionnaire_reply_default_messages(language_code).get(message_code))
    else:
        dbm = get_database_manager(request.user)
        account_language = get_organization_language(dbm)
        return HttpResponse(account_wide_sms_default_messages(account_language).get(message_code))

