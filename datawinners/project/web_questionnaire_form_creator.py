from django import forms
from django.utils.translation import ugettext_lazy as _
import django
from django.forms.fields import ChoiceField
from django.forms.forms import Form
from django.forms.widgets import HiddenInput
from django.utils.translation import ugettext
from datawinners.entity.helper import get_country_appended_location
from mangrove.form_model.validation import TextLengthConstraint
from mangrove.form_model.form_model import LOCATION_TYPE_FIELD_NAME
from datawinners.entity.import_data import load_all_subjects_of_type
from mangrove.form_model.field import SelectField, HierarchyField, TelephoneNumberField, IntegerField, GeoCodeField, DateField
from datawinners.entity.fields import PhoneNumberField, DjangoDateField
from datawinners.questionnaire.helper import get_location_field_code, get_geo_code_fields_question_code, make_clean_geocode_method
from mangrove.utils.types import is_empty

def question_form_init__(self, country=None, *args, **kwargs):
    self.country = country
    super(Form, self).__init__(*args, **kwargs)


def questionnaire_form_clean(self):
    location_field_code = get_location_field_code(self.form_model)

    self.cleaned_data.pop('entity_question_code', '')
    if location_field_code is None:
        return self.cleaned_data

    for question_code, values in self.cleaned_data.items():
        if question_code == location_field_code:
            self.cleaned_data[question_code] = get_country_appended_location(values, self.country)

    return self.cleaned_data


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


def get_chars_constraints(field):
    constraints = {}
    if not is_empty(field.constraints):
        constraint = field.constraints[0]
        if constraint.max is not None: constraints["max_length"] = constraint.max
        if constraint.min is not None: constraints["min_length"] = constraint.min
    return constraints


def get_number_constraints(field):
    constraints = {}
    if not is_empty(field.constraints):
        constraint = field.constraints[0]
        if constraint.max is not None: constraints["max_value"] = float(constraint.max)
        if constraint.min is not None: constraints["min_value"] = float(constraint.min)
    return constraints


def get_number_field_constraint_text(field):
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


class WebQuestionnaireFormCreator(object):
    def __init__(self, subject_question_creator, form_model, is_update=False):
        self.subject_question_creator = subject_question_creator
        self.form_model = form_model
        self.is_update = is_update

    def create(self):
        properties = dict()
        properties.update({'__init__': question_form_init__})
        properties.update({'form_model': self.form_model})
        properties.update({'clean': questionnaire_form_clean})
        geo_code_fields_code = get_geo_code_fields_question_code(self.form_model)
        for geo_code_field_code in geo_code_fields_code:
            properties.update({'clean_' + geo_code_field_code: make_clean_geocode_method(geo_code_field_code)})
        if self.form_model.is_entity_registration_form():
            properties.update({'__init__': question_form_init__})
            properties.update(self._get_entity_type_hidden_field())
            properties.update(self._get_short_code_question_code())
            properties.update(
                {field.code: self._get_django_field(field) for field in self.form_model.fields[:-1]})
            properties.update(self._get_short_code_django_field(self.form_model.fields[-1]))
        else:
            subject_question = self.form_model.entity_question
            if subject_question is not None:
                properties.update(self._get_subject_web_question(subject_question))
                properties.update(self.subject_question_creator.create_code_hidden_field(subject_question))
                properties.update(self._get_short_code_question_code())

            properties.update(
                {field.code: self._get_django_field(field) for field in self.form_model.fields if
                 not field.is_entity_field})

        properties.update(self._get_form_code_hidden_field())

        return type('QuestionnaireForm', (Form, ), properties)

    def _get_subject_web_question(self, subject_question):
        return {subject_question.code: (self.subject_question_creator.create(subject_question))}

    def _get_form_code_hidden_field(self):
        return {'form_code': forms.CharField(widget=HiddenInput, initial=self.form_model.form_code)}

    def _get_django_field(self, field):
        try:
            field_creation_map = {SelectField: self._create_select_field,
                                  TelephoneNumberField: self._create_phone_number_field,
                                  IntegerField: self._create_integer_field,
                                  DateField: self._create_date_field}
            return field_creation_map[type(field)](field)
        except KeyError:
            return self._create_char_field(field)


    def _insert_location_field_class_attributes(self, char_field, field):
        if field.name == LOCATION_TYPE_FIELD_NAME and isinstance(field, HierarchyField):
            char_field.widget.attrs['class'] = 'location_field'

    def _put_subject_field_class_attributes(self, char_field, field):
        if field.is_entity_field:
            char_field.widget.attrs['class'] = 'subject_field'

    def _create_field_type_class(self, char_field, field):
        self._insert_location_field_class_attributes(char_field, field)
        self._put_subject_field_class_attributes(char_field, field)

    def _create_char_field(self, field):
        constraints = get_chars_constraints(field)
        char_field = forms.CharField(label=field.label, initial=field.value, required=field.is_required(),
            help_text=field.instruction, **constraints)
        watermark = "xx.xxxx,yy.yyyy" if type(field) == GeoCodeField else get_text_field_constraint_text(field)
        char_field.widget.attrs["watermark"] = watermark
        char_field.widget.attrs['style'] = 'padding-top: 7px;'
        self._create_field_type_class(char_field, field)
        return char_field

    def _get_short_code_django_field(self, field):
        max_length = None
        min_length = None
        for constraint in field.constraints:
            if isinstance(constraint, TextLengthConstraint):
                max_length = constraint.max
                min_length = constraint.min
        django_field = forms.RegexField("^[a-zA-Z0-9]+$", label=field.label, initial=field.value,
            required=field.is_required(), max_length=max_length, min_length=min_length,
            help_text=field.instruction, error_message=_("Only letters and numbers are valid"))
        if self.is_update :
            django_field.widget.attrs['readonly'] = 'readonly'
        self._create_field_type_class(django_field, field)
        return {field.code: django_field}

    def _create_select_field(self, field):
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
            initial=field_values, required=field.is_required(), help_text=field.instruction)

    def _create_choices(self, field):
        choice_list = [('', '--None--')] if field.single_select_flag else []
        choice_list.extend([(option['val'], option['text']) for option in field.options])
        choices = tuple(choice_list)
        return choices


    def _get_entity_type_hidden_field(self):
        return {u't': forms.CharField(widget=HiddenInput, initial=self.form_model.entity_type[0])}

    def _create_phone_number_field(self, field):
        telephone_number_field = PhoneNumberField(label=field.label, initial=field.value, required=field.is_required(),
            help_text=field.instruction)
        telephone_number_field.widget.attrs["watermark"] = get_text_field_constraint_text(field)
        telephone_number_field.widget.attrs['style'] = 'padding-top: 7px;'
        if field.name == LOCATION_TYPE_FIELD_NAME and isinstance(field, HierarchyField):
            telephone_number_field.widget.attrs['class'] = 'location_field'

        return telephone_number_field

    def _create_date_field(self, field):
        format = field.DATE_DICTIONARY.get(field.date_format)
        date_field = DjangoDateField(input_formats=(format,), label=field.label, initial=field.value,
            required=field.is_required(), help_text=field.instruction)
        date_field.widget.attrs["watermark"] = get_text_field_constraint_text(field)
        date_field.widget.attrs['style'] = 'padding-top: 7px;'
        return date_field

    def _create_integer_field(self, field):
        constraints = get_number_constraints(field)
        float_field = django.forms.fields.FloatField(label=field.label, initial=field.value,
            required=field.is_required(),
            help_text=field.instruction, **constraints)
        float_field.widget.attrs["watermark"] = get_number_field_constraint_text(field)
        float_field.widget.attrs['style'] = 'padding-top: 7px;'
        return float_field

    def _get_short_code_question_code(self):
        return {u'short_code_question_code': self.form_model.entity_question.code}


class SubjectQuestionFieldCreator(object):
    def __init__(self, dbm, project, project_subject_loader=None):
        #for testing
        self.project_subject_loader = load_all_subjects_of_type if project_subject_loader is None else project_subject_loader
        self.project = project
        self.dbm = dbm

    def create(self, subject_field):
        reporter_entity_type = 'reporter'
        if self.project.is_on_type(reporter_entity_type):
            return self._data_sender_choice_fields(subject_field)
        return self._subjects_choice_fields(subject_field)

    def create_code_hidden_field(self, subject_field):
        return {'entity_question_code': forms.CharField(required=False, widget=HiddenInput, label=subject_field.code)}

    def _get_choice_field(self, data_sender_choices, subject_field, help_text):
        subject_choice_field = ChoiceField(required=subject_field.is_required(), choices=data_sender_choices,
            label=subject_field.name,
            initial=subject_field.value, help_text=help_text)
        subject_choice_field.widget.attrs['class'] = 'subject_field'
        return subject_choice_field

    def _data_sender_choice_fields(self, subject_field):
        data_senders = self.project.get_data_senders(self.dbm)
        data_sender_choices = self._get_all_choices(data_senders)
        return self._get_choice_field(data_sender_choices, subject_field, help_text=subject_field.instruction)

    def _build_subject_choice_data(self, subjects, key_list):
        values = map(lambda x: x["cols"] + [x["short_code"]], subjects)
        key_list.append('unique_id')

        return [dict(zip(key_list, value_list)) for value_list in values]

    def _subjects_choice_fields(self, subject_field):
        subjects, fields, label = self.project_subject_loader(self.dbm, type=self.project.entity_type)
        subject_data = self._build_subject_choice_data(subjects, fields)
        all_subject_choices = map(self._data_to_choice, subject_data)
        instruction_for_subject_field = ugettext("Choose Subject from this list.")
        return self._get_choice_field(all_subject_choices, subject_field, help_text=instruction_for_subject_field)

    def get_key(self, subject):
        return subject['unique_id']

    def get_value(self, subject):
        return subject['name'] + '  (' + subject['short_code'] + ')'

    def _data_to_choice(self, subject):
        return self.get_key(subject), self.get_value(subject)

    def _get_all_choices(self, entities):
        return [(entity['short_code'], entity['name'] + '  (' + entity['short_code'] + ')') for entity in entities]