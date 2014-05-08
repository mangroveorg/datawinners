import re
from django.contrib.auth.models import User
from django.utils.translation import ugettext
from datawinners.accountmanagement.models import NGOUserProfile
from datawinners.entity.helper import get_entity_type_fields, tabulate_data
from mangrove.datastore.entity import _from_row_to_entity
from mangrove.form_model.form_model import get_form_model_by_code, REPORTER
from mangrove.utils.types import is_empty


def load_data_senders(manager, short_codes):
    form_model = get_form_model_by_code(manager, 'reg')
    fields, labels, codes = get_entity_type_fields(manager)
    keys = [([REPORTER], short_code) for short_code in short_codes]
    rows = manager.view.by_short_codes(reduce=False, include_docs=True, keys=keys)
    data = [tabulate_data(_from_row_to_entity(manager, row), form_model, codes) for row in rows]
    return data, fields, labels


def remove_system_datasenders(datasender_list):
    for datasender in datasender_list:
        if datasender["short_code"] == "test":
            index = datasender_list.index(datasender)
            del datasender_list[index]


def get_user_profile_by_reporter_id(reporter_id, user):
    org_id = NGOUserProfile.objects.get(user=user).org_id
    user_profile = NGOUserProfile.objects.filter(reporter_id=reporter_id, org_id=org_id)
    return user_profile[0] if len(user_profile) else None


def get_datasender_user_detail(datasender, user):
    user_profile = get_user_profile_by_reporter_id(datasender['short_code'], user)

    datasender["is_user"] = False
    if user_profile:
        datasender_user_groups = list(user_profile.user.groups.values_list('name', flat=True))
        if "NGO Admins" in datasender_user_groups or "Project Managers" in datasender_user_groups \
            or "Read Only Users" in datasender_user_groups:
            datasender["is_user"] = True
        datasender['email'] = user_profile.user.email
        datasender['devices'] = "SMS,Web,Smartphone"
    else:
        datasender['email'] = None
        datasender['devices'] = "SMS"




email_re = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"' # quoted-string
    r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$', re.IGNORECASE)  # domain


class DataSenderRegistrationValidator(object):

    def validateForDataSenderEdit(self, values_dict):
        errors = {}
        cleaned_data = {}

        self._validate_name(cleaned_data, errors, values_dict)
        self._validate_telephone_number(cleaned_data, errors, values_dict)
        self._validate_location(cleaned_data, errors, values_dict)

        return errors, cleaned_data

    def validateForDataSenderRegister(self, values_dict):
        errors = {}
        cleaned_data = {}

        self._validate_name(cleaned_data, errors, values_dict)
        self._validate_email(cleaned_data, errors, values_dict)
        self._validate_telephone_number(cleaned_data, errors, values_dict)
        self._validate_location(cleaned_data, errors, values_dict)
        self._validate_short_code(cleaned_data, errors, values_dict)

        if values_dict.get('devices', None):
            cleaned_data['devices'] = values_dict['devices']

        return errors, cleaned_data


    def _geo_code_format_validations(self, lat_long):
        if len(lat_long) != 2:
            return False
        else:
            try:
                if not (-90 < float(lat_long[0]) < 90 and -180 < float(lat_long[1]) < 180):
                    return False
            except Exception:
                return False
        return True


    def _is_geo_code_valid(self, geo_code):
        geo_code_string = geo_code.strip()
        geo_code_string = (' ').join(geo_code_string.split())
        if not is_empty(geo_code_string):
            lat_long = filter(None, re.split("[ ,]", geo_code_string))
            return self._geo_code_format_validations(lat_long)
        return False


    def _validate_name(self, cleaned_data, errors, values_dict):
        if not values_dict['name']:
            errors['name'] = ugettext("This field is required.")
        elif re.search(r"[^A-Za-z'`-]+", values_dict['name']):
            errors['name'] = ugettext("Please enter a valid value containing only letters a-z or A-Z or symbols '`- ")
        else:
            cleaned_data['name'] = values_dict['name'].strip()

    def _validate_email(self, cleaned_data, errors, values_dict):
        if values_dict['email']:
            if not email_re.match(values_dict['email']):
                errors['email'] = ugettext('Enter a valid email address. Example:name@organization.com')
            else:
                email = values_dict['email'].strip()
                if User.objects.filter(email__iexact=email):
                    errors['email'] = ugettext(
                        'This email address is already in use. Please supply a different email address.')
                cleaned_data['email'] = email
        else:
            cleaned_data['email'] = ''
        if values_dict.get('devices', None) and not cleaned_data['email']:
            errors['email'] = ugettext("This field is required.")

    def _validate_telephone_number(self, cleaned_data, errors, values_dict):
        if not values_dict['telephone_number']:
            errors['telephone_number'] = ugettext("This field is required.")
        else:
            if not re.match(r"^(\(?[0-9]*?\)?)?[0-9- ]+$", values_dict['telephone_number']):
                errors['telephone_number'] = ugettext('Please enter a valid phone number.')
            elif len(values_dict['telephone_number']) < 5:
                errors['telephone_number'] = ugettext(
                    'Ensure this value has at least 5 digits (it has %d).' % len(values_dict['telephone_number']))
            else:
                cleaned_data['telephone_number'] = values_dict['telephone_number'].strip()

    def _validate_location(self, cleaned_data, errors, values_dict):
        if not values_dict['geo_code'] and not values_dict['location']:
            errors['location'] = ugettext("Please fill out at least one location field correctly.")
            errors['geo_code'] = ugettext("Please fill out at least one location field correctly.")
        elif values_dict['geo_code'] and not self._is_geo_code_valid(values_dict['geo_code']):
            errors['geo_code'] = ugettext(
                "Incorrect GPS format. The GPS coordinates must be in the following format: xx.xxxx,yy.yyyy. Example -18.8665,47.5315");
        else:
            cleaned_data['geo_code'] = values_dict['geo_code'].strip()
            cleaned_data['location'] = values_dict['location'].strip()

    def _validate_short_code(self, cleaned_data, errors, values_dict):
        if values_dict['short_code'] and re.search(r"[^a-zA-Z0-9]+", values_dict['short_code']):
            errors['short_code'] = ugettext('Only letters and numbers are valid')
        else:
            cleaned_data['short_code'] = values_dict['short_code'].strip()



