import base64

from django.http import HttpResponse
from django.contrib.auth import authenticate, login

#############################################################################
#
from datawinners.accountmanagement.decorators import is_sms_api_user
from datawinners.main.database import get_database_manager
from datawinners.project.couch_view_helper import get_all_projects
from mangrove.datastore.user_permission import get_questionnaires_for_user


def view_or_basicauth(view, request, is_authenticated_func, authenticate_func, realm="", *args, **kwargs):
    """
    This is a helper function used by both 'logged_in_or_basicauth' and
    'has_perm_or_basicauth' that does the nitty of determining if they
    are already logged in or if they have provided proper http-authorization
    and returning the view if all goes well, otherwise responding with a 401.
    """
    if is_authenticated_func(request.user):
        # Already logged in, just return the view.
        #
        return view(request, *args, **kwargs)

    # They are not logged in. See if they provided login credentials
    #
    if 'HTTP_AUTHORIZATION' in request.META:
        auth = request.META['HTTP_AUTHORIZATION'].split()
        if len(auth) == 2:
            # NOTE: We are only support basic authentication for now.
            #
            if auth[0].lower() == "basic":
                uname, passwd = base64.b64decode(auth[1]).split(':')
                user = authenticate_func(username=uname, password=passwd)
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        request.user = user
                        return view(request, *args, **kwargs)

    # Either they did not provide an authorization header or
    # something in the authorization attempt failed. Send a 401
    # back to them to ask them to authenticate.
    #
    response = HttpResponse()
    response.status_code = 401
    response['WWW-Authenticate'] = 'Basic realm="%s"' % realm
    return response


def httpbasic(view, realm="Datawinners"):
    """
    A simple decorator that requires a user to be logged in. If they are not
    logged in the request is examined for a 'authorization' header.

    If the header is present it is tested for basic authentication and
    the user is logged in with the provided credentials.

    If the header is not present a http 401 is sent back to the
    requestor to provide credentials.

    The purpose of this is that in several django projects I have needed
    several specific views that need to support basic authentication, yet the
    web site as a whole used django's provided authentication.

    The uses for this are for urls that are access programmatically such as
    by rss feed readers, yet the view requires a user to be logged in. Many rss
    readers support supplying the authentication credentials via http basic
    auth (and they do NOT support a redirect to a form where they post a
    username/password.)

    Use is simple:

    @logged_in_or_basicauth
    def your_view:
        ...

    You can provide the name of the realm to ask for authentication within.
    """

    def view_decorator(request, *args, **kwargs):
        return view_or_basicauth(view, request,
                                 lambda u: u.is_authenticated(),
                                 authenticate,
                                 realm, *args, **kwargs)

    return view_decorator


def is_not_datasender(func):
    def inner(*args, **kwargs):
        request = args[0]
        if request.user.get_profile().reporter:
            return HttpResponse(
                content="You do not have the required permissions to access "
                        "this information. Please contact your system administrator",
                status=400)
        return func(*args, **kwargs)

    return inner


def is_data_sender(request):
    return request.user.get_profile().reporter


def is_data_sender_for_project(request, project_id):
    return request.user.get_profile().reporter or _is_pm_data_sender_for_project(request.user, project_id)


def _is_pm_data_sender_for_project(user, project_id):
    if user.is_project_manager():
        questionnaires_as_datasender = [row['value'] for row in
                                        get_all_projects(get_database_manager(user), user.get_profile().reporter_id)]
        qn_as_ds = []
        for q_ds in questionnaires_as_datasender:
            qn_as_ds.append(q_ds.get('_id'))
        questionnaires_as_pm = get_questionnaires_for_user(user.id, get_database_manager(user))
        qn_as_pm = []
        for q_pm in questionnaires_as_pm:
            qn_as_pm.append(q_pm.get('_id'))
        questionnaires_only_as_datasender = list(set(qn_as_ds) - set(qn_as_pm))
        return project_id in questionnaires_only_as_datasender

    return False


def authenticate_api_user(username, password):
    user = authenticate(username=username, password=password)
    if is_sms_api_user(user):
        return user
    return None


def api_http_basic(view, realm="Datawinners"):
    def view_decorator(request, *args, **kwargs):
        return view_or_basicauth(view, request,
                                 lambda u: u.is_authenticated(),
                                 authenticate_api_user,
                                 realm, *args, **kwargs)

    return view_decorator
