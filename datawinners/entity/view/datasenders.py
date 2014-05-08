import json
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import translation
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _, get_language, activate
from django.views.generic.base import TemplateView
from datawinners.accountmanagement.decorators import valid_web_user
from datawinners.accountmanagement.models import Organization
from datawinners.activitylog.models import UserActivityLog
from datawinners.common.constant import EDITED_DATA_SENDER, REGISTERED_DATA_SENDER
from datawinners.entity.data_sender import get_datasender_user_detail, DataSenderRegistrationValidator
from datawinners.entity.helper import _get_data, update_data_sender_from_trial_organization, process_create_data_sender_form
from datawinners.entity.views import create_single_web_user
from datawinners.location.LocationTree import get_location_tree, get_location_hierarchy
from datawinners.main.database import get_database_manager
from datawinners.project.models import Project
from datawinners.project.view_models import ReporterEntity
from datawinners.submission.location import LocationBridge
from mangrove.datastore.entity import get_by_short_code
from mangrove.errors.MangroveException import MangroveException, DataObjectAlreadyExists
from mangrove.form_model.form_model import REPORTER, FormModel
from mangrove.transport import Request, TransportInfo
from mangrove.transport.player.player import WebPlayer


class EditDataSenderView(TemplateView):
    template_name = 'edit_datasender_form.html'

    def get(self, request, reporter_id, *args, **kwargs):
        #create_data_sender = False
        manager = get_database_manager(request.user)
        reporter_entity = ReporterEntity(get_by_short_code(manager, reporter_id, [REPORTER]))
        #entity_links = {'registered_datasenders_link': reverse("all_datasenders")}
        datasender = {'short_code': reporter_id}
        get_datasender_user_detail(datasender, request.user)
        email = datasender.get('email') if datasender.get('email') != '--' else ""
        reported_details = json.dumps({
            'name': reporter_entity.name,
            'phone_number': reporter_entity.mobile_number,
            'location': reporter_entity.location,
            'geo_code': reporter_entity.geo_code,
            'short_code': reporter_id,
            'email': email
        })
        return self.render_to_response({
                                           'reporter_details': repr(reported_details),
                                           'edit_datasender_url': reverse("edit_data_sender", args=[reporter_id])
                                       })

    def post(self, request, reporter_id, *args, **kwargs):
        reporter_id = reporter_id.lower()
        manager = get_database_manager(request.user)
        reporter_entity = ReporterEntity(get_by_short_code(manager, reporter_id, [REPORTER]))
        datasender = {'short_code': reporter_id}
        get_datasender_user_detail(datasender, request.user)
        org_id = request.user.get_profile().org_id
        errors, cleaned_data = DataSenderRegistrationValidator().validateForDataSenderEdit(request.POST)
        message = None
        success = False
        if not len(errors):
            try:
                org_id = request.user.get_profile().org_id
                current_telephone_number = reporter_entity.mobile_number
                organization = Organization.objects.get(org_id=org_id)
                web_player = WebPlayer(manager,
                                       LocationBridge(location_tree=get_location_tree(),
                                                      get_loc_hierarchy=get_location_hierarchy))
                response = web_player.accept(
                    Request(message=_get_data(cleaned_data, organization.country_name(), reporter_id),
                            transportInfo=TransportInfo(transport='web', source='web', destination='mangrove'),
                            is_update=True))
                if response.success:
                    if organization.in_trial_mode:
                        update_data_sender_from_trial_organization(current_telephone_number,
                                                                   cleaned_data["telephone_number"], org_id)

                    message = _("Your changes have been saved.")

                    detail_dict = {"Unique ID": reporter_id}
                    current_lang = get_language()
                    activate("en")
                    field_mapping = dict(mobile_number="telephone_number")
                    for field in ["geo_code", "location", "mobile_number", "name"]:
                        if getattr(reporter_entity, field) != cleaned_data.get(field_mapping.get(field, field)):
                            detail_dict.update({field: cleaned_data.get(field_mapping.get(field, field))})
                    activate(current_lang)
                    if len(detail_dict) > 1:
                        detail_as_string = json.dumps(detail_dict)
                        UserActivityLog().log(request, action=EDITED_DATA_SENDER, detail=detail_as_string)
                else:
                    if 'm' in response.errors:
                        errors['telephone_number'] = _(u'Sorry, the telephone number %s has already been registered.') % cleaned_data.get('telephone_number')

                success = response.success
            except MangroveException as exception:
                message = exception.message
                success = False

        return HttpResponse(
            json.dumps(
                {
                    "success": success,
                    "message": message,
                    "errors": errors
                }), mimetype='application/json', content_type='application/json')


    @method_decorator(valid_web_user)
    def dispatch(self, *args, **kwargs):
        return super(EditDataSenderView, self).dispatch(*args, **kwargs)

class RegisterDatasenderView(TemplateView):
    template_name = "project/register_datasender_popup.html"

    def get(self, request,*args, **kwargs):
        return self.render_to_response({
                                           'project_id': request.GET.get('project_id', ""),
                                           'current_language': translation.get_language()
                                       })

    def post(self, request, *args, **kwargs):
        dbm = get_database_manager(request.user)
        org_id = request.user.get_profile().org_id
        errors, cleaned_data = DataSenderRegistrationValidator().validateForDataSenderRegister(request.POST)
        try:
            reporter_id, message = process_create_data_sender_form(dbm, org_id, cleaned_data, errors)
        except DataObjectAlreadyExists as e:
            message = _("Data Sender with Unique Identification Number (ID) = %s already exists.") % e.data[1]
        if len(errors) == 0 and cleaned_data.get('devices',None) == "web" and reporter_id:
            email_id = request.POST['email']
            create_single_web_user(org_id=org_id, email_address=email_id, reporter_id=reporter_id,
                                   language_code=request.LANGUAGE_CODE)

        if message is not None and reporter_id:
            if request.POST.get('project_id',None):
                questionnaire = Project.get(dbm, request.POST['project_id'])
                questionnaire.associate_data_sender_to_project(dbm, reporter_id)
                questionnaire = questionnaire.name
            else:
                questionnaire = ""
            if not len(errors):
                UserActivityLog().log(request, action=REGISTERED_DATA_SENDER,
                                      detail=json.dumps(dict({"Unique ID": reporter_id})), project=questionnaire)
        return HttpResponse(
                    json.dumps(
                        {
                            "success": reporter_id is not None,
                            "message": message,
                            "errors": errors
                        }), mimetype='application/json', content_type='application/json')


    @method_decorator(valid_web_user)
    def dispatch(self, *args, **kwargs):
        return super(RegisterDatasenderView, self).dispatch(*args, **kwargs)
