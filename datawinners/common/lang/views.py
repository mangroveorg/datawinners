from collections import OrderedDict
import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext
from django.views.decorators.csrf import csrf_view_exempt, csrf_response_exempt
from django.views.generic.base import TemplateView, View
from datawinners import utils
from datawinners.accountmanagement.decorators import session_not_expired, is_datasender, is_not_expired
from datawinners.common.lang.messages import save_questionnaire_custom_messages, save_custom_messages, save_account_wide_sms_messages
from datawinners.common.lang.utils import questionnaire_customized_message_details, get_available_project_languages, create_new_questionnaire_reply_message_template, DuplicateLanguageException, account_wide_customized_message_details
from datawinners.main.database import get_database_manager


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
        })

    @method_decorator(csrf_view_exempt)
    @method_decorator(csrf_response_exempt)
    @method_decorator(login_required)
    @method_decorator(session_not_expired)
    @method_decorator(is_datasender)
    @method_decorator(is_not_expired)
    def dispatch(self, *args, **kwargs):
        return super(LanguagesView, self).dispatch(*args, **kwargs)

class LanguagesAjaxView(View):
    def get(self, request, *args, **kwargs):
        dbm = get_database_manager(request.user)
        return HttpResponse(json.dumps(questionnaire_customized_message_details(dbm, request.GET.get('language'))),
                            content_type="text/javascript")

    def post(self, request, *args, **kwargs):
        data = json.loads(request.POST.get("data", {}))
        dbm = get_database_manager(request.user)
        if data.get('isMessageModified'):
            questionnaire_customized_message_dict = get_reply_message_dictionary(data.get("messages"))
            save_questionnaire_custom_messages(dbm, data.get('language'), questionnaire_customized_message_dict)
        return HttpResponse(json.dumps({"success": True, "message": ugettext("Changes saved successfully.")}))

    @method_decorator(login_required)
    @method_decorator(session_not_expired)
    @method_decorator(is_datasender)
    @method_decorator(is_not_expired)
    def dispatch(self, *args, **kwargs):
        return super(LanguagesAjaxView, self).dispatch(*args, **kwargs)

class LanguageCreateView(View):
    def post(self,request,*args,**kwargs):
        language_name = request.POST.get('language_name')
        try:
            language_code = create_new_questionnaire_reply_message_template(get_database_manager(request.user), language_name)
            return HttpResponse(json.dumps({"language_code":language_code, "language_name":language_name}))
        except DuplicateLanguageException as e:
            return HttpResponse(json.dumps({"language_code":None, "message":e.message}))

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
            "account_messages": json.dumps(account_wide_customized_message_details(dbm))
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
            account_message_dict = get_reply_message_dictionary(data.get("messages"))
            save_account_wide_sms_messages(dbm,account_message_dict)

        return HttpResponse(json.dumps({"success": True, "message": ugettext("Changes saved successfully.")}))
