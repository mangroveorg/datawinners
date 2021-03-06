from mock import MagicMock
from django.contrib.auth.models import User
from datawinners.accountmanagement.models import NGOUserProfile


def get_project_manager():
    user = MagicMock(spec=User)
    user.id = 1
    normal_profile = MagicMock(spec=NGOUserProfile)
    normal_profile.reporter = False
    normal_profile.reporter_id = 2
    user.is_ngo_admin.return_value = False
    user.is_extended_user.return_value = False
    user.get_profile.return_value = normal_profile
    return user


def get_reporter_user():
    user = MagicMock(spec=User)
    reporter_profile = MagicMock(spec=NGOUserProfile)
    reporter_profile.reporter = True
    reporter_profile.reporter_id = 2
    user.get_profile.return_value = reporter_profile
    return user


def get_ngo_admin():
    user = MagicMock(spec=User)
    ngo_admin_profile = MagicMock(spec=NGOUserProfile)
    ngo_admin_profile.reporter = False
    user.is_ngo_admin.return_value = True
    user.is_extended_user.return_value = False
    user.get_profile.return_value = ngo_admin_profile
    return user


def get_extended_user():
    user = MagicMock(spec=User)
    extended_user_profile = MagicMock(spec=NGOUserProfile)
    extended_user_profile.reporter = False
    user.is_ngo_admin.return_value = False
    user.is_extended_user.return_value = True
    user.get_profile.return_value = extended_user_profile
    return user
