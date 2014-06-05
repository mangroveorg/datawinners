import json
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext
from django.views.generic.base import TemplateView
from django.contrib import messages
from datawinners.accountmanagement.decorators import session_not_expired, is_datasender, is_not_expired
from datawinners.common.lang.utils import get_available_project_languages
from datawinners.main.database import get_database_manager
from datawinners.project.models import Project
from datawinners.project.utils import make_project_links

class QuestionnaireLanguageView(TemplateView):
    template_name = 'project/project_language_selection.html'

    def get(self, request, project_id):
        dbm = get_database_manager(request.user)
        questionnaire = Project.get(dbm, project_id)
        languages_list = get_available_project_languages(dbm)
        current_project_language = questionnaire.language

        return self.render_to_response({
                                'project': questionnaire,
                                'project_links': make_project_links(questionnaire),
                                'languages_list': languages_list,
                                'languages_link': reverse('languages'),
                                'current_project_language': current_project_language,
                                'post_url': reverse("project-language", args=[project_id])
                              })


    def post(self, request, project_id):
        dbm = get_database_manager(request.user)
        questionnaire = Project.get(dbm, project_id)
        try:
            questionnaire.activeLanguages = [request.POST['selected_language']]
            questionnaire.is_outgoing_sms_replies_enabled = request.POST['enable_sms_replies'] == 'true'
            questionnaire.save()
            is_success = True
            if request.POST['has_callback'] == 'false':
                messages.info(request,ugettext('Your changes have been saved.'),extra_tags='success')
        except:
            is_success = False

        return HttpResponse(json.dumps({'success': is_success}), mimetype='application/json', content_type='application/json')

    @method_decorator(login_required)
    @method_decorator(session_not_expired)
    @method_decorator(is_datasender)
    @method_decorator(is_not_expired)
    def dispatch(self, *args, **kwargs):
        return super(QuestionnaireLanguageView, self).dispatch(*args, **kwargs)
