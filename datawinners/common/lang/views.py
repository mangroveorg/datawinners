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
from datawinners.main.database import get_database_manager


class LanguagesView(TemplateView):
    template_name = 'languages.html'

    def get(self, request, *args, **kwargs):
        dbm = get_database_manager(request.user)
        organization = utils.get_organization(request)
        current_language_code = organization.language
        available_languages = OrderedDict()
        for row in dbm.load_all_rows_in_view("all_languages",include_docs=False):
            available_languages.update({row.key:row.value})
        languages_list = available_languages.values()
        languages_list.sort()
        return self.render_to_response({
            "available_languages": languages_list,
            "current_language":available_languages.get(current_language_code)

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
        return HttpResponse(json.dumps([{"title":"Successful Submission","code":"reply_success_submission","message":"Thank you we received your submission"},
                           {"title":"Submission with an Error","code":"reply_error_submission","message":"Error. Incorrect answer for question. Please review printed Questionnaire and resend entire SMS."}
        ]), content_type="text/javascript")
    def post(self, request, *args, **kwargs):
        data = json.loads(request.POST.get("data", {}))
        dbm = get_database_manager(request.user)
        save_messages(dbm, data.get('language'), data.get('language'), data.get('customizedMessages'))
        return HttpResponse("ok")

    @method_decorator(csrf_view_exempt)
    @method_decorator(csrf_response_exempt)
    @method_decorator(login_required)
    @method_decorator(session_not_expired)
    @method_decorator(is_datasender)
    @method_decorator(is_not_expired)
    def dispatch(self, *args, **kwargs):
        return super(LanguagesAjaxView, self).dispatch(*args, **kwargs)