# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.core.mail.message import EmailMessage
from django.template.loader import render_to_string
from registration.models import RegistrationProfile
from datawinners import settings
from datawinners.accountmanagement.models import PaymentDetails
from datawinners.accountmanagement.utils import PRO_MONTHLY_PRICING, PRO_HALF_YEARLY_PRICING, PRO_YEARLY_PRICING, \
    PRO_SMS_MONTHLY_PRICING, PRO_SMS_HALF_YEARLY_PRICING, PRO_SMS_YEARLY_PRICING
from django.utils.translation import ugettext as _

def get_registration_processor(organization):
    registration_processor_dict = {'Basic':TrialAccountRegistrationProcessor,
                                   'Pro':ProAccountRegistrationProcessor,
                                   'Pro SMS':ProSMSAccountRegistrationProcessor }
    registration_processor = registration_processor_dict.get(organization.account_type)
    return registration_processor(organization)

class TrialAccountRegistrationProcessor(object):
    def __init__(self, organization):
        self.organization = organization

    def process(self, user, site, language, kwargs=None):
        if not kwargs: kwargs = {}
        ctx_dict = {'activation_key': RegistrationProfile.objects.get(user=user).activation_key,
                    'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                    'site': site,
                    'username': user.first_name}
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
        invoice_total, period = self._get_invoice_total()
        ctx_dict = {'activation_key': RegistrationProfile.objects.get(user=user).activation_key,
                    'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                    'site': site,
                    'username': user.first_name,
                    'invoice_total': invoice_total,
                    'period':period}
        subject = render_to_string('registration/activation_email_subject_in_'+language+'.txt')
        subject = ''.join(subject.splitlines()) # Email subject *must not* contain newlines
        message = render_to_string('registration/' + self.template + '_in_'+language+'.html',
                                   ctx_dict)
        email = EmailMessage(subject, message, settings.EMAIL_HOST_USER, [user.email], [settings.HNI_SUPPORT_EMAIL_ID])
        email.content_subtype = "html"
        email.send()

    def _get_invoice_total(self):
        pass

class ProAccountRegistrationProcessor(PaidAccountRegistrationProcessor):
    def __init__(self, organization):
        super(ProAccountRegistrationProcessor, self).__init__(organization)
        self.template = 'pro_activation_email'
        

    def _get_invoice_total(self):
        payment_detail = PaymentDetails.objects.filter(organization=self.organization)[0]
        invoice_total_dict = {'pay_monthly': (PRO_MONTHLY_PRICING, _('1 month')),
                              'half_yearly': (PRO_HALF_YEARLY_PRICING * 6, _('6 months')),
                             'yearly': (PRO_YEARLY_PRICING * 12, _('12 months'))}
        return invoice_total_dict.get(payment_detail.invoice_period)

class ProSMSAccountRegistrationProcessor(PaidAccountRegistrationProcessor):
    def __init__(self, organization):
        super(ProSMSAccountRegistrationProcessor, self).__init__(organization)
        self.template = 'pro_sms_activation_email'


    def _get_invoice_total(self):
        payment_detail = PaymentDetails.objects.filter(organization=self.organization)[0]
        invoice_total_dict = {'pay_monthly': (PRO_SMS_MONTHLY_PRICING, _('1 month')),
                              'half_yearly': (PRO_SMS_HALF_YEARLY_PRICING * 6, _('6 months')),
                             'yearly': (PRO_SMS_YEARLY_PRICING * 12, _('12 months'))}
        return invoice_total_dict.get(payment_detail.invoice_period)