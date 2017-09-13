from django.contrib.auth.models import User


def is_ngo_admin(self):
    return True if len(self.groups.filter(name__in=['NGO Admins'])) > 0 else False


def is_extended_user(self):
    return True if len(self.groups.filter(name__in=['Extended Users'])) > 0 else False


def is_project_manager(self):
    return True if len(self.groups.filter(name__in=['Project Managers'])) > 0 else False

def has_higher_privileges_than(self, user):
    if self.is_ngo_admin() and (user.is_extended_user() or user.is_project_manager() or user.is_no_delete_pm()):
        return True
    if self.is_extended_user() and (user.is_project_manager() or user.is_no_delete_pm()):
        return True
    return False

def is_no_delete_pm(self):
    return True if len(self.groups.filter(name__in=['No Delete PM'])) > 0 else False

User.add_to_class("is_ngo_admin", is_ngo_admin)
User.add_to_class("is_extended_user", is_extended_user)
User.add_to_class("is_project_manager", is_project_manager)
User.add_to_class("has_higher_privileges_than", has_higher_privileges_than)
User.add_to_class("is_no_delete_pm", is_no_delete_pm)
