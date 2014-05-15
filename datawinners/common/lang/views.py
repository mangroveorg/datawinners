from collections import OrderedDict
import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_view_exempt, csrf_response_exempt
from django.views.generic.base import TemplateView, View
from datawinners import utils
from datawinners.accountmanagement.decorators import session_not_expired, is_datasender, is_not_expired
from datawinners.common.lang.messages import save_messages
from datawinners.common.lang.utils import customized_message_details
from datawinners.main.database import get_database_manager


class LanguagesView(TemplateView):
    template_name = 'languages.html'

    def get(self, request, *args, **kwargs):
        dbm = get_database_manager(request.user)
        organization = utils.get_organization(request)
        current_language_code = organization.language
        lang_dict = {}
        for row in dbm.load_all_rows_in_view("all_languages", include_docs=False):
            lang_dict.update({row.key: row.value})
        languages_list = _get_languages_sorted_by_name(lang_dict)
        return self.render_to_response({
            "available_languages": languages_list,
            "current_language": current_language_code
        })

    @method_decorator(csrf_view_exempt)
    @method_decorator(csrf_response_exempt)
    @method_decorator(login_required)
    @method_decorator(session_not_expired)
    @method_decorator(is_datasender)
    @method_decorator(is_not_expired)
    def dispatch(self, *args, **kwargs):
        return super(LanguagesView, self).dispatch(*args, **kwargs)


def _get_languages_sorted_by_name(lang_dict):
    languages_list = []
    sorted_language_dict = OrderedDict(sorted(lang_dict.items(), key=lambda x: x[1]))
    for code, language_name in sorted_language_dict.iteritems():
        languages_list.append({'code': code, 'name': language_name})
    return languages_list

class LanguagesAjaxView(View):
    def get(self, request, *args, **kwargs):
        dbm = get_database_manager(request.user)
        return HttpResponse(json.dumps(customized_message_details(dbm, request.GET.get('language'))),
                            content_type="text/javascript")

    def post(self, request, *args, **kwargs):
        data = json.loads(request.POST.get("data", {}))
        dbm = get_database_manager(request.user)
        customized_message_dict = OrderedDict()
        for customized_message in data.get('customizedMessages'):
            customized_message_dict.update({customized_message.get("code"): customized_message.get("message")})
        save_messages(dbm, data.get('language'), customized_message_dict)
        return HttpResponse("ok")

    @method_decorator(csrf_view_exempt)
    @method_decorator(csrf_response_exempt)
    @method_decorator(login_required)
    @method_decorator(session_not_expired)
    @method_decorator(is_datasender)
    @method_decorator(is_not_expired)
    def dispatch(self, *args, **kwargs):
        return super(LanguagesAjaxView, self).dispatch(*args, **kwargs)