import json
from django.contrib.auth.models import User

from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import translation
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _, get_language, activate
from django.views.generic.base import TemplateView

from datawinners.accountmanagement.decorators import valid_web_user, is_datasender
from datawinners.accountmanagement.helper import update_user_name_if_exists
from datawinners.accountmanagement.models import Organization
from datawinners.activitylog.models import UserActivityLog
from datawinners.common.constant import EDITED_DATA_SENDER, REGISTERED_DATA_SENDER
from datawinners.entity.data_sender import get_datasender_user_detail
from datawinners.entity.datasender_tasks import update_datasender_on_open_submissions
from datawinners.entity.forms import ReporterRegistrationForm, EditReporterRegistrationForm
from datawinners.entity.helper import _get_data, update_data_sender_from_trial_organization, \
    process_create_data_sender_form
from datawinners.entity.views import create_single_web_user
from datawinners.location.LocationTree import get_location_tree, get_location_hierarchy
from datawinners.main.database import get_database_manager
from datawinners.project.view_models import ReporterEntity
from datawinners.search.datasender_index import update_datasender_index_by_id
from datawinners.search.submission_index import update_submission_search_for_datasender_edition
from datawinners.submission.location import LocationBridge
from mangrove.datastore.entity import get_by_short_code, contact_by_short_code
from mangrove.errors.MangroveException import MangroveException, DataObjectAlreadyExists
from mangrove.form_model.form_model import REPORTER
from mangrove.transport import Request, TransportInfo
from mangrove.form_model.project import Project
from mangrove.transport.player.player import WebPlayer


class EditDataSenderView(TemplateView):
    template_name = 'edit_datasender_form.html'

    def get(self, request, reporter_id, *args, **kwargs):
        create_data_sender = False
        manager = get_database_manager(request.user)
        reporter_entity = ReporterEntity(get_by_short_code(manager, reporter_id, [REPORTER]))
        entity_links = {'registered_datasenders_link': reverse("all_datasenders")}
        datasender = {'short_code': reporter_id}
        get_datasender_user_detail(datasender, request.user)
        email = reporter_entity.email if reporter_entity.email != '--' else False
        name = reporter_entity.name
        phone_number = reporter_entity.mobile_number
        location = reporter_entity.location
        geo_code = reporter_entity.geo_code
        form = EditReporterRegistrationForm(initial={
            'name': name,
            'telephone_number': phone_number,
            'location': location,
            'geo_code': geo_code,
            'generated_id': 'no',
            'email': email
        })

        return self.render_to_response(RequestContext(request, {
            'reporter_id': reporter_id,
            'form': form,
            'project_links': entity_links,
            'email': email,
            'create_data_sender': create_data_sender
        }))

    def _send_email_to_datasender(self, email, org_id, reporter_entity, reporter_id, request):
        if not reporter_entity.is_contact and not User.objects.filter(email=email):
            create_single_web_user(org_id, email, reporter_id, request.LANGUAGE_CODE)
        return email

    def _update_user_activity_log(self, form, reporter_entity, reporter_id, request):
        detail_dict = {"Unique ID": reporter_id}
        activate("en")
        field_mapping = dict(mobile_number="telephone_number")
        for field in ["geo_code", "location", "mobile_number", "name"]:
            if getattr(reporter_entity, field) != form.cleaned_data.get(field_mapping.get(field, field)):
                label = u"%s" % form.fields[field_mapping.get(field, field)].label
                detail_dict.update({label: form.cleaned_data.get(field_mapping.get(field, field))})
        activate(get_language())
        if len(detail_dict) > 1:
            detail_as_string = json.dumps(detail_dict)
            UserActivityLog().log(request, action=EDITED_DATA_SENDER, detail=detail_as_string)

    def _update_name_in_postgres_if_exists(self, form, reporter_entity):
        current_name = reporter_entity.name
        current_email = reporter_entity.email
        data_sender_name = form.cleaned_data["name"]
        if current_email and current_name != data_sender_name:
            update_user_name_if_exists(current_email, data_sender_name)
        return data_sender_name

    def _edit_contact(self, form, manager, organization, reporter_id):
        web_player = WebPlayer(manager,
                               LocationBridge(location_tree=get_location_tree(),
                                              get_loc_hierarchy=get_location_hierarchy))
        response = web_player.accept(
            Request(message=_get_data(form.cleaned_data, organization.country_name(), reporter_id),
                    transportInfo=TransportInfo(transport='web', source='web', destination='mangrove'),
                    is_update=True))
        return response

    def _update_mobile_number_if_trial_organization(self, form, org_id, organization, reporter_entity):
        if organization.in_trial_mode:
            update_data_sender_from_trial_organization(reporter_entity.mobile_number,
                                                       form.cleaned_data["telephone_number"], org_id)

    def post(self, request, reporter_id, *args, **kwargs):
        reporter_id = reporter_id.lower()
        manager = get_database_manager(request.user)
        reporter_entity = ReporterEntity(contact_by_short_code(manager, reporter_id))
        email = reporter_entity.email
        org_id = request.user.get_profile().org_id
        form = EditReporterRegistrationForm(org_id=org_id, existing_email=email,  data=request.POST)
        message = None
        if form.is_valid():
            try:
                organization = Organization.objects.get(org_id=org_id)
                response = self._edit_contact(form, manager, organization, reporter_id)

                if response.success:
                    email = form.cleaned_data['email']
                    if email:
                        email = self._send_email_to_datasender(email, org_id, reporter_entity, reporter_id,
                                                               request)

                    self._update_mobile_number_if_trial_organization(form, org_id, organization, reporter_entity)

                    data_sender_name = self._update_name_in_postgres_if_exists(form, reporter_entity)

                    update_submission_search_for_datasender_edition(manager, reporter_id, data_sender_name)
                    message = _("Your changes have been saved.")

                    self._update_user_activity_log(form, reporter_entity, reporter_id, request)
                else:
                    form.update_errors(response.errors)

            except MangroveException as exception:
                message = exception.message

        entity_links = {'registered_datasenders_link': reverse("all_datasenders")}

        return render_to_response('edit_datasender_form.html',
                                  {
                                      'form': form,
                                      'message': message,
                                      'reporter_id': reporter_id,
                                      'email': email,
                                      'project_links': entity_links
                                  },
                                  context_instance=RequestContext(request))

    @method_decorator(valid_web_user)
    @method_decorator(is_datasender)
    def dispatch(self, *args, **kwargs):
        return super(EditDataSenderView, self).dispatch(*args, **kwargs)


class RegisterDatasenderView(TemplateView):
    template_name = "datasender_form.html"

    def _get_save_button_text(self, project_id):
        return _("Register") if project_id else _("Add Contact")

    def get(self, request, *args, **kwargs):
        if request.GET.get('project_id'):
            form = ReporterRegistrationForm(initial={'project_id': request.GET.get('project_id')})
        else:
            form = ReporterRegistrationForm()
        save_button_text = self._get_save_button_text(request.GET.get('project_id'))

        return self.render_to_response(RequestContext(request, {
            'form': form,
            'current_language': translation.get_language(),
            'registration_link': '/entity/datasender/register/',
            'button_text': save_button_text
        }))

    def _give_web_access_to_successful_datasender_registration(self, form, org_id, reporter_id, request):
        if len(form.errors) == 0 and form.requires_web_access() and reporter_id and \
                        form.cleaned_data['project_id'] != "":
            email_id = form.cleaned_data['email']
            create_single_web_user(org_id=org_id, email_address=email_id, reporter_id=reporter_id,
                                   language_code=request.LANGUAGE_CODE)

    def _associate_datasender_to_questionnaire(self, dbm, reporter_id, questionnaire_id):
        questionnaire = Project.get(dbm, questionnaire_id)
        reporters_to_associate = [reporter_id]
        questionnaire.associate_data_sender_to_project(dbm, reporters_to_associate)
        for data_senders_code in reporters_to_associate:
            update_datasender_index_by_id(data_senders_code, dbm)

        return questionnaire.name

    def _update_activity_log(self, form, questionnaire_name, reporter_id, request):
        if not len(form.errors):
            UserActivityLog().log(request, action=REGISTERED_DATA_SENDER,
                                  detail=json.dumps(dict({"Unique ID": reporter_id})), project=questionnaire_name)

    def post(self, request, *args, **kwargs):
        entity_links = {'registered_datasenders_link': reverse("all_datasenders")}
        dbm = get_database_manager(request.user)
        org_id = request.user.get_profile().org_id
        project_id = request.POST.get('project_id')
        form = ReporterRegistrationForm(org_id=org_id, data=request.POST)
        reporter_id = None
        try:
            reporter_id, message = process_create_data_sender_form(dbm, form, org_id)
            update_datasender_on_open_submissions.delay(dbm.database_name, reporter_id)

        except DataObjectAlreadyExists as e:
            message = _("Data Sender with Unique Identification Number (ID) = %s already exists.") % e.data[1]

        self._give_web_access_to_successful_datasender_registration(form, org_id, reporter_id, request)

        if message is not None and reporter_id:
            questionnaire_id = form.cleaned_data['project_id']

            if questionnaire_id != "":
                questionnaire_name = self._associate_datasender_to_questionnaire(dbm, reporter_id, questionnaire_id)
            else:
                questionnaire_name = ""

            self._update_activity_log(form, questionnaire_name, reporter_id, request)
            form = ReporterRegistrationForm(initial={'project_id': questionnaire_id})

        save_button_text = self._get_save_button_text(project_id)
        message_text = self._get_message_text(message, project_id, reporter_id)

        return render_to_response('datasender_form.html',
                                  {
                                      'form': form,
                                      'message': message_text,
                                      'success': (reporter_id is not None),
                                      'project_inks': entity_links,
                                      'current_language': translation.get_language(),
                                      'registration_link': '/entity/datasender/register/',
                                      'button_text': save_button_text
                                  },
                                  context_instance=RequestContext(request))


    @method_decorator(valid_web_user)
    @method_decorator(is_datasender)
    def dispatch(self, *args, **kwargs):
        return super(RegisterDatasenderView, self).dispatch(*args, **kwargs)

    def _get_message_text(self, message, project_id, reporter_id):
        if reporter_id:
            return message if project_id else "%s %s %s" % (
                _("Your contact(s) have been added."), _("ID is:"), reporter_id )
        else:
            return message




