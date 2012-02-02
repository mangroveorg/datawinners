# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from datawinners.main.utils import get_database_manager
from datawinners.project import models

def get_all_project_for_user(user):
    if user.get_profile().reporter:
        return models.get_all_projects(get_database_manager(user), user.get_profile().reporter_id)
    return models.get_all_projects(get_database_manager(user))


def get_visibility_settings_for(user):
    if user.get_profile().reporter:
        return "disable_link_for_reporter", "none"
    return "",""