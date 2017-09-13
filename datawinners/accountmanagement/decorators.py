import logging

from django.conf import settings as django_settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.utils.functional import wraps
from mangrove.datastore.user_permission import has_permission
from datawinners.project.couch_view_helper import get_all_projects
from datawinners.project.models import count_projects
from mangrove.errors.MangroveException import DataObjectNotFound

from datawinners.accountmanagement.models import NGOUserProfile, Organization
from datawinners.local_settings import CRS_ORG_ID
from datawinners.main.database import get_database_manager
from mangrove.form_model.project import Project

logger = logging.getLogger("django")


def is_datasender_allowed(f):
    def wrapper(*args, **kw):
        superuser = False
        user = args[0].user
        user_profile = user.get_profile()
        if not user_profile.reporter:
            superuser = True

        dbm = get_database_manager(user)
        try:
            questionnaire = Project.get(dbm, kw['project_id'])
        except DataObjectNotFound:
            questionnaire = None
        if not questionnaire or questionnaire.is_void():
            if superuser:
                return HttpResponseRedirect(
                    django_settings.HOME_PAGE + "?deleted=True") if superuser else HttpResponseRedirect(
                    django_settings.DATASENDER_DASHBOARD + "?associate=False")
        else:
            if not superuser and user_profile.reporter_id not in questionnaire.data_senders:
                return HttpResponseRedirect(django_settings.DATASENDER_DASHBOARD + "?associate=False")
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
        if not len(user.groups.filter(name__in=["NGO Admins", "Extended Users"])) > 0:
            return HttpResponseRedirect(django_settings.ACCESS_DENIED_PAGE)

        return f(*args, **kw)

    return wrapper


def for_super_admin_only(f):
    def wrapper(*args, **kw):
        from django.core.urlresolvers import resolve

        current_url = resolve(args[0].path_info).url_name if args[0].path_info else ''
        if not args[0].user.is_authenticated() and current_url == 'upgrade_from_mail' and kw.get('token'):
            try:
                args[0].user = User.objects.get(auth_token__key=kw.get('token'))
            except Exception:
                return HttpResponseRedirect(django_settings.HOME_PAGE)
        user = args[0].user
        if len(user.groups.filter(name__in=["NGO Admins"])) < 1:
            return HttpResponseRedirect(django_settings.ACCESS_DENIED_PAGE)

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


def is_allowed_to_view_reports(f, redirect_to='/questionnaire'):
    def wrapper(*args, **kw):
        request = args[0]
        user = request.user
        profile = user.get_profile()
        if CRS_ORG_ID != profile.org_id and profile.reporter:
            return HttpResponseRedirect(redirect_to)
        return f(*args, **kw)

    return wrapper


def is_pro_sms(f):
    def wrapper(*args, **kw):
        user = args[0].user
        profile = user.get_profile()
        organization = Organization.objects.get(org_id=profile.org_id)
        if organization.is_pro_sms:
            return HttpResponseRedirect(django_settings.HOME_PAGE)
        return f(*args, **kw)

    return wrapper


def is_new_user(f):
    def wrapper(*args, **kw):
        user = args[0].user
        if not count_projects(get_database_manager(args[0].user), False) and not user.groups.filter(
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
        questionnaire = Project.get(dbm, project_id)
        if "web" not in questionnaire.devices:
            referer = django_settings.HOME_PAGE
            return HttpResponseRedirect(referer)
        return f(*args, **kw)

    return wrapper


def valid_web_user(f):
    return login_required(not_api_user(session_not_expired(is_not_expired(f))), login_url="/login")


def is_sms_api_user(user):
    return user.groups.filter(name="SMS API Users").count() > 0


def is_super_admin(f):
    def wrapper(*args, **kw):
        request = args[0]
        user = request.user
        if not user.is_superuser:
            return HttpResponse(status='404')
        return f(*args, **kw)

    return wrapper


def restrict_access(f):
    @wraps(f)
    def wrapper(request, project_id, *args, **kw):
        user = request.user
        if user.is_project_manager() and not has_permission(get_database_manager(user), user.id, project_id):
            return HttpResponseRedirect(django_settings.ACCESS_DENIED_PAGE)

        return f(request, project_id, *args, **kw)

    return wrapper


def has_delete_permission(f):
    def wrapper(*args, **kw):
        user = args[0].user
        if user.is_no_delete_pm():
            return HttpResponseRedirect(django_settings.HOME_PAGE)

        return f(*args, **kw)

    return wrapper