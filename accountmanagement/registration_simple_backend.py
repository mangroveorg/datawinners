from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.template.context import RequestContext

from registration import signals
from registration.forms import RegistrationForm
from datawinners.accountmanagement.models import Organization
from datawinners.accountmanagement.organization_id_creator import OrganizationIdCreator


class SimpleBackend(object):
    """
    A registration backend which implements the simplest possible
    workflow: a user supplies a username, email address and password
    (the bare minimum for a useful account), and is immediately signed
    up and logged in.

    """
    def register(self, request, **kwargs):
        """
        Create and immediately log in a new user.

        """
        username, email, password = kwargs['email'], kwargs['email'], kwargs['password1']
        new_user = User.objects.create_user(username, email, password)
        new_user.first_name = kwargs.get('first_name')
        new_user.last_name =  kwargs.get('last_name')
        new_user.save()
        organization = Organization(name = kwargs.get('organization_name'), sector = kwargs.get('organization_sector')
                                             , addressline1 = kwargs.get('organization_addressline1'), addressline2 = kwargs.get('organization_addressline2')
                                             , city = kwargs.get('organization_city'), state = kwargs.get('organization_state')
                                             , country = kwargs.get('organization_country'), zipcode = kwargs.get('organization_zipcode')
                                             , office_phone = kwargs.get('organization_office_phone'), website = kwargs.get('organization_website')
                                             , org_id=OrganizationIdCreator().generateId()
                                             )
        organization.save()
#        new_user.save()

        # authenticate() always has to be called before login(), and
        # will return the user we just created.
#        new_user = authenticate(username=username, password=password)
#        login(request, new_user)
        signals.user_registered.send(sender=self.__class__,
                                     user=new_user,
                                     request=request)
        return new_user

    def activate(self, **kwargs):
        raise NotImplementedError

    def registration_allowed(self, request):
        """
        Indicate whether account registration is currently permitted,
        based on the value of the setting ``REGISTRATION_OPEN``. This
        is determined as follows:

        * If ``REGISTRATION_OPEN`` is not specified in settings, or is
          set to ``True``, registration is permitted.

        * If ``REGISTRATION_OPEN`` is both specified and set to
          ``False``, registration is not permitted.

        """
        return getattr(settings, 'REGISTRATION_OPEN', True)

    def get_form_class(self, request):
        return RegistrationForm

    def post_registration_redirect(self, request, user):
        """
        Return the name of the URL to redirect to after successful
        user registration.

        """
        return ('/registration_complete', (), {'user':user})


    def post_activation_redirect(self, request, user):
        raise NotImplementedError
