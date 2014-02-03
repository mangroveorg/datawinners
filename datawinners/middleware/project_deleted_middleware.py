import logging
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseRedirect
from datawinners.main.database import get_database_manager
from datawinners.project.models import Project
from django.conf import settings as django_settings


def get_redirect_url(dbm, project_id):
    dashboard_page = django_settings.HOME_PAGE + "?deleted=true"
    project = Project.load(dbm.database, project_id)
    if project.is_deleted():
        return HttpResponseRedirect(dashboard_page)
    else:
        return None


class ProjectDeletedMiddleware(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def process_view(self, request, view_func, view_args, view_kwargs):
        user = request.user
        if user == AnonymousUser():
            return None
        dbm = get_database_manager(user)
        if "project_id" in view_kwargs.keys():
            return get_redirect_url(dbm, view_kwargs['project_id'])

        key = filter(lambda v: v in request.POST.keys(), ["project_id", "pid"])
        if key:
            return get_redirect_url(dbm, request.POST[key])

        return None