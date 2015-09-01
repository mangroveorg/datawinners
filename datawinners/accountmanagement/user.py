from django.contrib.auth.models import User
from mangrove.datastore.user_permission import has_permission
from datawinners.main.database import get_database_manager


def is_ngo_admin(self):
    return True if len(self.groups.filter(name__in=['NGO Admins'])) > 0 else False


def is_extended_user(self):
    return True if len(self.groups.filter(name__in=['Extended Users'])) > 0 else False


def is_project_manager(self):
    return True if len(self.groups.filter(name__in=['Project Managers'])) > 0 else False

def has_higher_privileges_than(self, user):
    if self.is_ngo_admin() and (user.is_extended_user() or user.is_project_manager()):
        return True
    if self.is_extended_user() and user.is_project_manager():
        return True
    return False

def can_manage_questionnaire(self, questionnaire_id):
    if self.is_ngo_admin() or self.is_extended_user():
        return True
    if self.is_project_manager() and has_permission(get_database_manager(self), self.id, questionnaire_id):
        return True
    return False


User.add_to_class("is_ngo_admin", is_ngo_admin)
User.add_to_class("is_extended_user", is_extended_user)
User.add_to_class("is_project_manager", is_project_manager)
User.add_to_class("has_higher_privileges_than", has_higher_privileges_than)
User.add_to_class("can_manage_questionnaire", can_manage_questionnaire)
