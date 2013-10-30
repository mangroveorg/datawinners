import re
from django.contrib.auth.models import User
from django.core.validators import email_re
from django.utils.translation import ugettext as _
from mangrove.data_cleaner import TelephoneNumber
from mangrove.form_model.form_model import MOBILE_NUMBER_FIELD_CODE, NAME_FIELD_CODE, LOCATION_TYPE_FIELD_CODE, GEO_CODE, EMAIL_FIELD_CODE, case_insensitive_lookup
from mangrove.transport.repository.reporters import is_datasender_with_mobile_number_present


def _is_value_missing(value):
    return True if value is None or value == "" else False


class MobileNumberValidator:
    def __init__(self, dbm):
        self.dbm = dbm

    def validate(self, values):
        errors = []
        mobile_number = case_insensitive_lookup(values, MOBILE_NUMBER_FIELD_CODE)
        if _is_value_missing(mobile_number):
            errors.append(Error("Mobile-Missing", _("Mobile number is missing.")))
            return errors
        mobile_number_cleaned = TelephoneNumber().clean(mobile_number)
        if len(mobile_number_cleaned) < 5:
            errors.append(Error("Mobile-Number-Too-Short", _("Mobile number is too short.")))
        elif len(mobile_number_cleaned) > 15:
            errors.append(Error("Mobile-Number-Too-Long", _("Mobile number is too long.")))
        elif is_datasender_with_mobile_number_present(self.dbm, mobile_number_cleaned):
            errors.append(Error("Mobile-Number-Not-Unique", _("Mobile number is not unique.")))
        return errors

class NameValidator:
    def validate(self, values):
        errors = []
        name = case_insensitive_lookup(values, NAME_FIELD_CODE)
        if _is_value_missing(name):
            errors.append(Error("Name-Missing", _("Name is missing.")))
            return errors
        if len(name) > 20:
            errors.append(Error("Data-Sender-Name-Length-Exceeded", _("Name has exceeded 20 characters.")))
        return errors


class CoordinatesValidator:
    def __init__(self):
        self.gps_format_incorrect_error = Error("GPS-Format-Incorrect",
                        _("Incorrect GPS format. The GPS coordinates must be in the following format: xx.xxxx,yy.yyyy"))

    def _validate_gps_format(self, lat_long):
        errors = []
        if len(lat_long) != 2:
            errors.append(self.gps_format_incorrect_error)
            return errors
        try:
            if not (-90 < float(lat_long[0]) < 90 and -180 < float(lat_long[1]) < 180):
                errors.append(self.gps_format_incorrect_error)
        except ValueError:
            errors.append(self.gps_format_incorrect_error)
        return errors

    def validate(self, values):
        coordinates = case_insensitive_lookup(values, GEO_CODE)
        if _is_value_missing(coordinates):
            return []
        lat_long = filter(None, re.split("[ ,]", coordinates))
        return self._validate_gps_format(lat_long)


class EmailValidator:
    def validate(self, values):
        errors = []
        email = case_insensitive_lookup(values, EMAIL_FIELD_CODE)
        if _is_value_missing(email):
            return []
        if not email_re.match(email):
            errors.append(Error("Email-Format-Incorrect", _("Email format is incorrect.")))
        elif User.objects.filter(email__iexact=email):
            errors.append(Error("Email-Not-Unique", _("Email is not unique.")))
        return errors


class LocationValidator:
    def validate(self, values):
        errors = []
        location = case_insensitive_lookup(values, LOCATION_TYPE_FIELD_CODE)
        coordinates = case_insensitive_lookup(values, GEO_CODE)
        if _is_value_missing(location) and _is_value_missing(coordinates):
            errors.append(Error("Location-GPS-Missing", _("Atleast GPS or Location needs to be present")))
        return errors


class DataSenderImportValidator:
    def __init__(self, dbm):
        self.validators = [NameValidator(), MobileNumberValidator(dbm), LocationValidator(), EmailValidator(),
                           CoordinatesValidator()]

    def validate(self, row_entry):
        errors = []
        for validator in self.validators:
            errors.extend(validator.validate(row_entry))
        return errors


class Error:
    def __init__(self, key, message):
        self.key = key
        self.message = message