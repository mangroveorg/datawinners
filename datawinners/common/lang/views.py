import json
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_view_exempt, csrf_response_exempt
from django.views.generic.base import TemplateView
from datawinners import utils
from datawinners.accountmanagement.decorators import session_not_expired, is_datasender, is_not_expired
from datawinners.main.database import get_database_manager


class LanguagesView(TemplateView):
    template_name = 'languages.html'

    def get(self, request, *args, **kwargs):
        dbm = get_database_manager(request.user)
        organization = utils.get_organization(request)
        current_language_code = organization.language
        available_languages = {}
        for row in dbm.load_all_rows_in_view("all_languages",include_docs=False):
            available_languages.update({row.key:row.value})
        return self.render_to_response({
            "available_languages":available_languages.values(),
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



