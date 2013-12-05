# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.core.mail.message import EmailMessage
from django.template.loader import render_to_string
from registration.models import RegistrationProfile
from datawinners import settings
from datawinners.accountmanagement.models import PaymentDetails

def get_registration_processor(organization):
    return TrialAccountRegistrationProcessor(organization) if organization.in_trial_mode\
    else PaidAccountRegistrationProcessor(organization)


class TrialAccountRegistrationProcessor(object):
    def __init__(self, organization):
        self.organization = organization

    def process(self, user, site, language, kwargs=None):
        if not kwargs: kwargs = {}
        ctx_dict = {'activation_key': RegistrationProfile.objects.get(user=user).activation_key,
                    'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                    'site': site,
                    'username': user.first_name + ' ' + user.last_name}
        subject = render_to_string('registration/activation_email_subject_for_trial_account_in_'+language+'.txt')
        subject = ''.join(subject.splitlines()) # Email subject *must not* contain newlines
        message = render_to_string('registration/activation_email_for_trial_account_in_'+language+'.html',
                                   ctx_dict)
        email = EmailMessage(subject, message, settings.EMAIL_HOST_USER, [user.email], [settings.HNI_SUPPORT_EMAIL_ID])
        email.content_subtype = "html"
        email.send()


class PaidAccountRegistrationProcessor(object):
    def __init__(self, organization):
        self.organization = organization

    def process(self, user, site, language, kwargs):
        self._make_payment_details(kwargs)
        self._send_activation_email(site, user, language)

    def _make_payment_details(self, kwargs):
        invoice_period = kwargs['invoice_period']
        preferred_payment = kwargs['preferred_payment']
        payment_details = PaymentDetails.objects.model(organization=self.organization, invoice_period=invoice_period,
                                                       preferred_payment=preferred_payment)
        payment_details.save()

    def _send_activation_email(self, site, user, language):
        ctx_dict = {'activation_key': RegistrationProfile.objects.get(user=user).activation_key,
                    'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                    'site': site,
                    'username': user.first_name + ' ' + user.last_name}
        subject = render_to_string('registration/activation_email_subject_in_'+language+'.txt')
        subject = ''.join(subject.splitlines()) # Email subject *must not* contain newlines
        message = render_to_string('registration/activation_email_in_'+language+'.html',
                                   ctx_dict)
        email = EmailMessage(subject, message, settings.EMAIL_HOST_USER, [user.email], [settings.HNI_SUPPORT_EMAIL_ID])
        email.content_subtype = "html"
        email.send()

