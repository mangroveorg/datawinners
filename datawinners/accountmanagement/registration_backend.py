# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.conf import settings
from django.contrib.sites.models import RequestSite
from django.contrib.sites.models import Site
from django.contrib.auth.models import Group

from registration import signals
from registration.forms import RegistrationForm
from registration.models import RegistrationProfile
from datawinners.accountmanagement.models import Organization
from datawinners.accountmanagement.registration_processors import get_registration_processor

class RegistrationBackend(object):
    """
    A registration backend which follows a simple workflow:

    1. User signs up, inactive account is created.

    2. Email is sent to user with activation link.

    3. User clicks activation link, account is now active.

    Using this backend requires that

    * ``registration`` be listed in the ``INSTALLED_APPS`` setting
      (since this backend makes use of models defined in this
      application).

    * The setting ``ACCOUNT_ACTIVATION_DAYS`` be supplied, specifying
      (as an integer) the number of days from registration during
      which a user may activate their account (after that period
      expires, activation will be disallowed).

    * The creation of the templates
      ``registration/activation_email_subject_in_en.txt`` and
      ``registration/activation_email_in_en.html``, which will be used for
      the activation email. See the notes for this backends
      ``register`` method for details regarding these templates.

    Additionally, registration can be temporarily closed by adding the
    setting ``REGISTRATION_OPEN`` and setting it to
    ``False``. Omitting this setting, or setting it to ``True``, will
    be interpreted as meaning that registration is currently open and
    permitted.

    Internally, this is accomplished via storing an activation key in
    an instance of ``registration.models.RegistrationProfile``. See
    that model and its custom manager for full documentation of its
    fields and supported operations.

    """


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
        """
        Return the default form class used for user registration.

        """
        return RegistrationForm

    def register(self, request, **kwargs):
        """
        Given a username, email address and password, register a new
        user account, which will initially be inactive.

        Along with the new ``User`` object, a new
        ``registration.models.RegistrationProfile`` will be created,
        tied to that ``User``, containing the activation key which
        will be used for this account.

        An email will be sent to the supplied email address; this
        email should contain an activation link. The email will be
        rendered using two templates. See the documentation for
        ``RegistrationProfile.send_activation_email()`` for
        information about these templates and the contexts provided to
        them.

        After the ``User`` and ``RegistrationProfile`` are created and
        the activation email is sent, the signal
        ``registration.signals.user_registered`` will be sent, with
        the new ``User`` as the keyword argument ``user`` and the
        class of this backend as the sender.

        """
        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)


        organization = self.create_respective_organization(kwargs)
        organization.save()
        organization.organization_setting.save()

        new_user = self._create_user(site, kwargs)

        registration_processor = get_registration_processor(organization)
        registration_processor.process(new_user, site, request.LANGUAGE_CODE, kwargs)
        new_user.save()

        signals.user_registered.send(sender=self.__class__,
                                     user=new_user,
                                     request=request, title=kwargs.get("title"), organization_id=organization.org_id,
                                     organization=organization, mobile_phone=kwargs.get("mobile_phone"), 
                                     reporter_id=kwargs.get('reporter_id'))

        return new_user

    def is_subscription_registration(self, kwargs):
        return 'organization_address' in kwargs and 'organization_zipcode' in kwargs

    def create_respective_organization(self, kwargs):
        if self.is_subscription_registration(kwargs):
            organization = Organization.create_organization(kwargs)
        else:
            organization = Organization.create_trial_organization(kwargs)
        return organization

    def post_registration_redirect(self, request, user):
        """
        Return the name of the URL to redirect to after successful
        user registration.

        """
        return '/registration_complete', (), {}

    def _create_user(self, site, kwargs):
        email, password = kwargs['email'], kwargs['password1']
        new_user = RegistrationProfile.objects.create_inactive_user(email, email, password, site, send_email=False)
        new_user.first_name = kwargs['full_name']
        group = Group.objects.filter(name="NGO Admins")
        new_user.groups.add(group[0])
        return new_user