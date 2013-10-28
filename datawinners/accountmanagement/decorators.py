import logging
from django.conf import settings as django_settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from datawinners.accountmanagement.models import NGOUserProfile, Organization
from datawinners.local_settings import CRS_ORG_ID
from datawinners.main.database import get_database_manager
from datawinners.project.models import get_all_projects, Project
from django.contrib.auth.models import User

logger = logging.getLogger("django")


def is_datasender_allowed(f):
    def wrapper(*args, **kw):
        user = args[0].user
        if user.get_profile().reporter:
            projects = get_all_projects(get_database_manager(user), user.get_profile().reporter_id)
        else:
            projects = get_all_projects(get_database_manager(user))
        project_ids = [project.id for project in projects]
        project_id = kw['project_id']
        if not project_id in project_ids:
            return HttpResponseRedirect(django_settings.DATASENDER_DASHBOARD)

        return f(*args, **kw)

    return wrapper


def is_datasender(f):
    def wrapper(*args, **kw):
        user = args[0].user
        if user.get_profile().reporter:
            return HttpResponseRedirect(django_settings.DATASENDER_DASHBOARD)

        return f(*args, **kw)

    return wrapper


def is_admin(f):
    def wrapper(*args, **kw):
        from django.core.urlresolvers import resolve
        current_url = resolve(args[0].path_info).url_name if args[0].path_info else ''
        if not args[0].user.is_authenticated() and current_url == 'upgrade_from_mail' and kw.get('token'):
            try:
                args[0].user = User.objects.get(auth_token__key=kw.get('token'))
            except Exception:
                return HttpResponseRedirect(django_settings.HOME_PAGE)
        user = args[0].user
        if not user.groups.filter(name="NGO Admins").count() > 0:
            return HttpResponseRedirect(django_settings.HOME_PAGE)

        return f(*args, **kw)

    return wrapper


def session_not_expired(f):
    def wrapper(*args, **kw):
        request = args[0]
        user = request.user
        try:
            user.get_profile()
        except NGOUserProfile.DoesNotExist:
            logger.exception("The session is expired")
            return HttpResponseRedirect(django_settings.INDEX_PAGE)
        except Exception as e:
            logger.exception("Caught exception when get user profile: " + e.message)
            return HttpResponseRedirect(django_settings.INDEX_PAGE)
        return f(*args, **kw)

    return wrapper


def is_not_expired(f):
    def wrapper(*args, **kw):
        request = args[0]
        user = request.user
        org = Organization.objects.get(org_id=user.get_profile().org_id)
        if org.is_expired():
            return HttpResponseRedirect(django_settings.TRIAL_EXPIRED_URL)
        return f(*args, **kw)

    return wrapper


def is_allowed_to_view_reports(f, redirect_to='/alldata'):
    def wrapper(*args, **kw):
        request = args[0]
        user = request.user
        profile = user.get_profile()
        if CRS_ORG_ID != profile.org_id and profile.reporter:
            return HttpResponseRedirect(redirect_to)
        return f(*args, **kw)

    return wrapper


def is_trial(f):
    def wrapper(*args, **kw):
        user = args[0].user
        profile = user.get_profile()
        organization = Organization.objects.get(org_id=profile.org_id)
        if not organization.in_trial_mode:
            return HttpResponseRedirect(django_settings.HOME_PAGE)
        return f(*args, **kw)

    return wrapper


def is_new_user(f):
    def wrapper(*args, **kw):
        user = args[0].user
        if not len(get_all_projects(get_database_manager(args[0].user))) and not user.groups.filter(
                name="Data Senders").count() > 0:
            return HttpResponseRedirect("/start?page=" + args[0].path)

        return f(*args, **kw)

    return wrapper


def not_api_user(f):
    def wrapper(*args, **kw):
        user = args[0].user
        if is_sms_api_user(user):
            return HttpResponseRedirect(django_settings.INDEX_PAGE)
        return f(*args, **kw)

    return wrapper


def project_has_web_device(f):
    def wrapper(*args, **kw):
        request = args[0]
        user = request.user
        dbm = get_database_manager(user)
        project_id = kw["project_id"]
        project = Project.load(dbm.database, project_id)
        if "web" not in project.devices:
            referer = django_settings.HOME_PAGE
            return HttpResponseRedirect(referer)
        return f(*args, **kw)

    return wrapper


def valid_web_user(f):
    return login_required(not_api_user(session_not_expired(is_not_expired(f))), login_url="/login")


def is_sms_api_user(user):
    return user.groups.filter(name="SMS API Users").count() > 0