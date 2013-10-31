# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from copy import copy

from django.utils.translation import ugettext as _
from django.contrib.auth.models import User, Group
from django.core.validators import email_re
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import get_current_site
from django.core.mail.message import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import int_to_base36
from datawinners.accountmanagement.helper import get_all_registered_phone_numbers_on_trial_account
from datawinners.entity.datasender_validators import DataSenderImportValidator, Error
from datawinners.entity.helper import load_entity_registration_data
from datawinners.entity.player import FilePlayer
from datawinners.exceptions import InvalidEmailException, NameNotFoundException
from datawinners.utils import get_organization_from_manager
from mangrove.data_cleaner import TelephoneNumber
from mangrove.errors.MangroveException import MangroveException, DataObjectAlreadyExists
from mangrove.form_model.form_model import NAME_FIELD_CODE, SHORT_CODE, MOBILE_NUMBER_FIELD, REPORTER, case_insensitive_lookup
from mangrove.transport import Response
from mangrove.transport.contract.transport_info import TransportInfo
from mangrove.form_model.form_model import MOBILE_NUMBER_FIELD_CODE
from datawinners.accountmanagement.models import NGOUserProfile
from datawinners.settings import HNI_SUPPORT_EMAIL_ID, EMAIL_HOST_USER
from mangrove.transport.player.parser import XlsDatasenderParser
from mangrove.transport.work_flow import RegistrationWorkFlow


class DataSenderFileUpload(FilePlayer):
    def __init__(self, dbm, parser, channel_name, form_code, location_tree=None):
        FilePlayer.__init__(self, dbm, parser, channel_name, form_code, location_tree)

    def accept(self, file_contents):
        organization = get_organization_from_manager(self.dbm)
        rows = self.parser.parse(file_contents)
        form_model = self._get_form_model(rows)
        responses = []
        for (form_code, values) in rows:
                responses.append(self._import_datasender_entry(form_code, organization, values, form_model))
        return responses

    def _create_failure_response(self, errors, row_values):
        errors_as_dict = {}
        for error in errors:
            errors_as_dict[error.key] = error.message
        return Response(success=False, errors={
                                                "error": errors_as_dict,
                                                "row": row_values
                                              })

    def _import_datasender_entry(self, form_code, organization, values, form_model=None):
        errors = self._validate_entry(values)
        if len(errors) > 0:
            return self._create_failure_response(errors, values)

        self._append_country_for_location_field(form_model, values, organization)
        transport_info = TransportInfo(transport=self.channel_name, source=self.channel_name, destination="")
        submission = self._create_submission(transport_info, form_code, copy(values))
        try:
            values = self._get_datasender_values(form_model, values)
            log_entry = "message: " + str(values) + "|source: web|"
            response = self._import_data_sender(form_model, organization, submission, values)
            if not response.success:
                response.errors = dict(error=response.errors, row=values)
                log_entry += "Status: False"
            else:
                log_entry += "Status: True"
            self.logger.info(log_entry)
            return response
        except DataObjectAlreadyExists as e:
            if self.logger is not None:
                log_entry += "Status: False"
                self.logger.info(log_entry)
            return self._create_failure_response([Error("Short-Code-Exists", "reporter with Unique Identification Number (ID) = %s already exists." % e.data[1])], values)

    def _validate_entry(self, values):
        return DataSenderImportValidator(self.dbm).validate(row_entry=values)

    def _create_user(self, email, organization, response):
        user = User.objects.create_user(email, email, 'password')
        group = Group.objects.filter(name="Data Senders")[0]
        user.groups.add(group)
        user.first_name = case_insensitive_lookup(response.processed_data, NAME_FIELD_CODE)
        user.save()
        profile = NGOUserProfile(user=user, org_id=organization.org_id, title="Mr",
                                 reporter_id=case_insensitive_lookup(response.processed_data,
                                                                     SHORT_CODE))
        profile.save()
        return user

    def _import_data_sender(self, form_model, organization, submission, values):
        email = case_insensitive_lookup(values, "email")
        response = self.submit(form_model, values, submission, [])
        if email:
            user = self._create_user(email, organization, response)
            send_email_to_data_sender(user, _("en"))
        #else:
        #    response = self.submit(form_model, values, submission, [])
        return response

    def _get_phone_numbers(self, organization):
        return get_all_registered_phone_numbers_on_trial_account() \
            if organization.in_trial_mode else get_datasenders_mobile(self.dbm)

    def _get_datasender_values(self, form_model, values):
        values = RegistrationWorkFlow(self.dbm, form_model, self.location_tree).process(values)
        return values




def send_email_to_data_sender(user, language_code, request=None, type="activation"):
    site = get_current_site(request)
    ctx_dict = {
        'domain': site.domain,
        'uid': int_to_base36(user.id),
        'user': user,
        'token': default_token_generator.make_token(user),
        'protocol': 'http',
        'site': site,
    }
    types = dict({"activation":
                      dict({"subject": 'activatedatasenderemail/activation_email_subject_for_data_sender_account_',
                            "subject_param": False,
                            "template": 'activatedatasenderemail/activation_email_for_data_sender_account_'}),
                  "created_user":
                      dict({"subject": 'registration/created_user_email_subject_',
                            "subject_param": site.domain,
                            "template": 'registration/created_user_email_'})})
    if type not in types:
        return
    action = types.get(type)
    subject = render_to_string(action.get("subject") + str(language_code) + '.txt')
    subject = ''.join(subject.splitlines())
    if action.get("subject_param"):
        subject = subject % action.get("subject_param")

    if request is not None:
        ctx_dict.update({"creator_user": request.user.first_name})

    message = render_to_string(action.get("template") + language_code + '.html', ctx_dict)
    email = EmailMessage(subject, message, EMAIL_HOST_USER, [user.email], [HNI_SUPPORT_EMAIL_ID])
    email.content_subtype = "html"
    email.send()


def get_datasenders_mobile(manager):
    all_data_senders, fields, labels = load_entity_registration_data(manager, REPORTER)
    index = fields.index(MOBILE_NUMBER_FIELD)
    return [ds["cols"][index] for ds in all_data_senders]


