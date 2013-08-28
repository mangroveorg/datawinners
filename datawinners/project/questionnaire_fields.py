import re
from string import strip

from django.core.exceptions import ValidationError
from django.forms import ChoiceField, FloatField, TextInput
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext
from django import forms
from django.utils.translation import ugettext_lazy as _

from datawinners.entity.fields import PhoneNumberField, DjangoDateField
from datawinners.entity.import_data import load_all_entities_of_type
from mangrove.form_model.validation import GeoCodeConstraint
from mangrove.form_model.form_model import LOCATION_TYPE_FIELD_NAME
from mangrove.form_model.field import SelectField, HierarchyField, TelephoneNumberField, IntegerField, GeoCodeField, DateField
from mangrove.utils.types import is_empty
from datawinners.utils import translate, get_text_language_by_instruction


class FormField(object):
    def create(self, field):
        try:
            field_creation_map = {SelectField: SelectFormField,
                                  TelephoneNumberField: PhoneNumberFormField,
                                  IntegerField: IntegerFormField,
                                  DateField: DateFormField,
            }
            return field_creation_map[type(field)]().create(field)
        except KeyError:
            return CharFormField().create(field)


class SelectFormField(object):
    def create(self, field):
        if field.single_select_flag:
            for opt in field.options:
                if opt['text'] == field.value:
                    field.value = opt['val']

            return ChoiceField(choices=self._create_choices(field), required=field.is_required(),
                               label=field.label,
                               initial=field.value, help_text=field.instruction)
        else:
            field_values = []
            if field.value is not None:
                field_labels = field.value.split(',')
                for opt in field.options:
                    if opt['text'] in field_labels:
                        field_values.append(opt['val'])

        return forms.MultipleChoiceField(label=field.label, widget=forms.CheckboxSelectMultiple,
                                         choices=self._create_choices(field),
                                         initial=field_values, required=field.is_required(),
                                         help_text=field.instruction)

    def _create_choices(self, field):
        choice_list = [('', '--None--')] if field.single_select_flag else []
        choice_list.extend([(option['val'], option['text']) for option in field.options])
        choices = tuple(choice_list)
        return choices


class PhoneNumberFormField(object):
    def create(self, field):
        telephone_number_field = PhoneNumberField(label=field.label, initial=field.value, required=field.is_required(),
                                                  help_text=field.instruction)
        telephone_number_field.widget.attrs["watermark"] = get_text_field_constraint_text(field)
        telephone_number_field.widget.attrs['style'] = 'padding-top: 7px;'
        if field.name == LOCATION_TYPE_FIELD_NAME and isinstance(field, HierarchyField):
            telephone_number_field.widget.attrs['class'] = 'location_field'
        return telephone_number_field


class TextInputForFloat(TextInput):
    def _has_changed(self, initial, data):
        if data is None:
            data_value = 0
        else:
            data_value = data
        if initial is None:
            initial_value = 0
        else:
            initial_value = initial
        try:
            return float(initial_value) != float(data_value)
        except ValueError:
            return force_unicode(initial_value) != force_unicode(data_value)


class IntegerFormField(object):
    def create(self, field):
        constraints = self._get_number_constraints(field)
        float_field = FloatField(label=field.label, initial=field.value,
                                 required=field.is_required(), help_text=field.instruction, widget=TextInputForFloat,
                                 **constraints)
        float_field.widget.attrs["watermark"] = self._get_number_field_constraint_text(field)
        float_field.widget.attrs['style'] = 'padding-top: 7px;'
        return float_field

    def _get_number_constraints(self, field):
        constraints = {}
        if not is_empty(field.constraints):
            constraint = field.constraints[0]
            if constraint.max is not None: constraints["max_value"] = float(constraint.max)
            if constraint.min is not None: constraints["min_value"] = float(constraint.min)
        return constraints

    def _get_number_field_constraint_text(self, field):
        max = min = None
        if len(field.constraints) > 0:
            constraint = field.constraints[0]
            min = constraint.min
            max = constraint.max
        if min is not None and max is None:
            constraint_text = _("Minimum %s") % min
            return constraint_text
        if min is None and max is not None:
            constraint_text = _("Upto %s") % max
            return constraint_text
        elif min is not None and max is not None:
            constraint_text = _("%s -- %s") % (min, max)
            return constraint_text
        return ""


class DateFormField(object):
    def create(self, field):
        format = field.DATE_DICTIONARY.get(field.date_format)
        date_field = DjangoDateField(input_formats=(format,), label=field.label, initial=field.value,
                                     required=field.is_required(), help_text=field.instruction)
        date_field.widget.attrs["watermark"] = get_text_field_constraint_text(field)
        date_field.widget.attrs['style'] = 'padding-top: 7px;'
        return date_field


class GeoCodeValidator(object):
    clean = lambda self, x: strip(x)

    def __call__(self, value):
        lat_long_string = self.clean(value)
        lat_long = lat_long_string.replace(",", " ")
        lat_long = re.sub(' +', ' ', lat_long).split(" ")
        try:
            if len(lat_long) != 2:
                raise Exception
            GeoCodeConstraint().validate(latitude=lat_long[0], longitude=lat_long[1])
        except Exception:
            raise ValidationError(_(
                "Incorrect GPS format. The GPS coordinates must be in the following format: xx.xxxx,yy.yyyy. Example -18.8665,47.5315"))
        return lat_long_string


class CharFormField(object):
    def create(self, field):
        constraints = self._get_chars_constraints(field)
        validators = [GeoCodeValidator()] if type(field) == GeoCodeField else []
        char_field = forms.CharField(label=field.label, initial=field.value, required=field.is_required(),
                                     help_text=field.instruction, validators=validators, **constraints)
        char_field.widget.attrs["watermark"] = "xx.xxxx,yy.yyyy" if type(
            field) == GeoCodeField else get_text_field_constraint_text(field)
        char_field.widget.attrs['style'] = 'padding-top: 7px;'
        char_field.widget.attrs['class'] = css_class(field)
        return char_field

    def _get_chars_constraints(self, field):
        constraints = {}
        if not is_empty(field.constraints):
            constraint = field.constraints[0]
            if constraint.max is not None: constraints["max_length"] = constraint.max
            if constraint.min is not None: constraints["min_length"] = constraint.min
        return constraints


class EntityField(object):
    def __init__(self, dbm, project):
        self.dbm = dbm
        self.project = project

    def create(self, subject_field, entity_type):
        reporter_entity_type = 'reporter'
        if self.project.is_on_type(reporter_entity_type):
            choice_fields = self._data_sender_choice_fields(subject_field)
        else:
            choice_fields = self._subject_choice_fields(entity_type, subject_field)

        return {subject_field.code: choice_fields}

    def _build_subject_choice_data(self, subjects, key_list):
        values = map(lambda x: x["cols"] + [x["short_code"]], subjects)
        key_list.append('unique_id')
        return [dict(zip(key_list, value_list)) for value_list in values]

    def _get_choice_field(self, data_sender_choices, subject_field, help_text):
        subject_choice_field = ChoiceField(required=subject_field.is_required(), choices=data_sender_choices,
                                           label=subject_field.name,
                                           initial=subject_field.value, help_text=help_text)
        subject_choice_field.widget.attrs['class'] = 'subject_field'
        return subject_choice_field

    def get_value(self, subject):
        return subject['name'] + '  (' + subject['short_code'] + ')'

    def choice(self, subject):
        return subject['unique_id'], self.get_value(subject)


    def _data_sender_choice_fields(self, subject_field):
        data_senders = self.project.get_data_senders(self.dbm)
        data_sender_choices = self._get_all_choices(data_senders)
        return self._get_choice_field(data_sender_choices, subject_field, help_text=subject_field.instruction)

    def _get_all_choices(self, entities):
        return [(entity['short_code'], entity['name'] + '  (' + entity['short_code'] + ')') for entity in entities]

    def _subject_choice_fields(self, entity_type, subject_field):
        subjects, fields, label = load_all_entities_of_type(self.dbm, type=entity_type)
        subjects = self._build_subject_choice_data(subjects, fields)
        language = get_text_language_by_instruction(subject_field.instruction)
        instruction_for_subject_field = translate("Choose Subject from this list.", language=language, func=ugettext)
        all_subject_choices = map(self.choice, subjects)
        choice_fields = self._get_choice_field(all_subject_choices, subject_field,
                                               help_text=instruction_for_subject_field)
        return choice_fields


def get_text_field_constraint_text(field):
    if not is_empty(field.constraints):
        length_constraint = field.constraints[0]
        min = length_constraint.min
        max = length_constraint.max
        if min is not None and max is None:
            constraint_text = _("Minimum %s characters") % min
            return constraint_text
        if min is None and max is not None:
            constraint_text = _("Upto %s characters") % max
            return constraint_text
        elif min is not None and max is not None:
            constraint_text = _("Between %s -- %s characters") % (min, max)
            return constraint_text
    return ""


def css_class(field):
    if field.is_entity_field:
        return 'subject_field'
    if field.name == LOCATION_TYPE_FIELD_NAME and isinstance(field, HierarchyField):
        return 'location_field'
    return None