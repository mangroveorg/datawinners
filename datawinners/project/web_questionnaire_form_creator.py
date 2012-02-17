from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
import django
from django.forms.fields import ChoiceField, Field
from django.forms.forms import Form
from django.forms.widgets import HiddenInput
from django.utils.translation import ugettext
from mangrove.errors.MangroveException import GeoCodeFormatException
from mangrove.form_model.form_model import LOCATION_TYPE_FIELD_NAME
from mangrove.form_model.validation import GeoCodeConstraint
from datawinners.entity.import_data import load_all_subjects_of_type
from mangrove.form_model.field import SelectField, HierarchyField, TelephoneNumberField, IntegerField, GeoCodeField
from datawinners.entity.fields import PhoneNumberField
from datawinners.questionnaire.helper import get_location_field_code, get_geo_code_field_question_code

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


def clean_geocode(self):
    geo_code_field_code = get_geo_code_field_question_code(self.form_model)
    lat_long_string = self.cleaned_data[geo_code_field_code]
    lat_long = lat_long_string.replace(",", " ").strip().split()
    try:
        if len(lat_long) < 2:
            raise Exception
        GeoCodeConstraint().validate(latitude=lat_long[0], longitude=lat_long[1])
    except Exception:
            raise ValidationError(_(
                "Incorrect GPS format. The GPS coordinates must be in the following format: xx.xxxx,yy.yyyy. Example -18.8665,47.5315"))
    return self.cleaned_data[geo_code_field_code]


def get_country_appended_location(location_hierarchy, country):
    return location_hierarchy + "," + country if location_hierarchy is not None else None


class WebQuestionnaireFormCreater(object):
    def __init__(self, subject_question_creator, form_model):
        self.subject_question_creator = subject_question_creator
        self.form_model = form_model

    def create(self):
        properties = dict()
        language = self.form_model.activeLanguages[0]
        properties.update({'__init__': question_form_init__})
        properties.update({'form_model': self.form_model})
        properties.update({'clean': questionnaire_form_clean})
        geo_code_field_code = get_geo_code_field_question_code(self.form_model)
        if geo_code_field_code is not None:
            properties.update({'clean_' + geo_code_field_code: clean_geocode})
        if self.form_model.is_registration_form():
            properties.update({'__init__': question_form_init__})
            properties.update(self._get_entity_type_hidden_field())
            properties.update(self._get_short_code_question_code())
            properties.update(
                {field.code: self._get_django_field(field, language) for field in self.form_model.fields})
        else:
            subject_question = self.form_model.entity_question
            if subject_question is not None:
                properties.update(self._get_subject_web_question(subject_question))
                properties.update(self.subject_question_creator.create_code_hidden_field(subject_question))
                properties.update(self._get_short_code_question_code())

            properties.update(
                {field.code: self._get_django_field(field, language) for field in self.form_model.fields if
                 not field.is_entity_field})

        properties.update(self._get_form_code_hidden_field())

        return type('QuestionnaireForm', (Form, ), properties)

    def _get_subject_web_question(self, subject_question):
        return {subject_question.code: (self.subject_question_creator.create(subject_question))}

    def _get_form_code_hidden_field(self):
        return {'form_code': forms.CharField(widget=HiddenInput, initial=self.form_model.form_code)}

    def _get_django_field(self, field, language):
        try:
            field_creation_map = {SelectField: self._create_select_field,
                                  TelephoneNumberField: self._create_phone_number_field,
                                  IntegerField: self._create_integer_field}
            return field_creation_map[type(field)](field, language)
        except KeyError:
            return self._create_char_field(field, language)


    def _insert_location_field_class_attributes(self, char_field, field):
        if field.name == LOCATION_TYPE_FIELD_NAME and isinstance(field, HierarchyField):
            char_field.widget.attrs['class'] = 'location_field'

    def _put_subject_field_class_attributes(self, char_field, field):
        if field.is_entity_field:
            char_field.widget.attrs['class'] = 'subject_field'

    def _create_field_type_class(self, char_field, field):
        self._insert_location_field_class_attributes(char_field, field)
        self._put_subject_field_class_attributes(char_field, field)

    def _create_char_field(self, field, language):
        char_field = forms.CharField(label=field.label[language], initial=field.value, required=field.is_required(),
            help_text=_(field.instruction))
        watermark = "xx.xxxx,yy.yyyy" if type(field) == GeoCodeField else field.get_constraint_text()
        char_field.widget.attrs["watermark"] = watermark
        char_field.widget.attrs['style'] = 'padding-top: 7px;'
        self._create_field_type_class(char_field, field)
        return char_field

    def _create_select_field(self, field, language):
        if field.single_select_flag:
            return ChoiceField(choices=self._create_choices(field, language), required=field.is_required(),
                label=field.label[language],
                initial=field.value, help_text=field.instruction)
        return forms.MultipleChoiceField(label=field.label[language], widget=forms.CheckboxSelectMultiple,
            choices=self._create_choices(field, language),
            initial=field.value, required=field.is_required(), help_text=field.instruction)

    def _create_choices(self, field, language):
        choice_list = [('', '--None--')] if field.single_select_flag else []
        choice_list.extend([(option['val'], option['text'][language]) for option in field.options])
        choices = tuple(choice_list)
        return choices


    def _get_entity_type_hidden_field(self):
        return {u't': forms.CharField(widget=HiddenInput, initial=self.form_model.entity_type[0])}

    def _create_phone_number_field(self, field, language):
        telephone_number_field = PhoneNumberField(label=field.label[language], required=field.is_required(),
            help_text=field.instruction)
        telephone_number_field.widget.attrs["watermark"] = field.get_constraint_text()
        telephone_number_field.widget.attrs['style'] = 'padding-top: 7px;'
        if field.name == LOCATION_TYPE_FIELD_NAME and isinstance(field, HierarchyField):
            telephone_number_field.widget.attrs['class'] = 'location_field'

        return telephone_number_field

    def _create_integer_field(self, field, language):
        integer_field = django.forms.fields.IntegerField(label=field.label[language], required=field.is_required(),
            error_messages={'invalid': _('Enter a valid integer')})
        integer_field.widget.attrs["watermark"] = field.get_constraint_text()
        integer_field.widget.attrs['style'] = 'padding-top: 7px;'
        return integer_field

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


    def _get_all_choices(self, all_subjects):
        return [(data_sender['short_code'], data_sender['name'] + '  (' + data_sender['short_code'] + ')')for
                                                                                                          data_sender in
                                                                                                          all_subjects]

    def _get_all_subject(self):
        all_subjects, fields, label = self.project_subject_loader(self.dbm, type=self.project.entity_type)
        return [dict(zip(fields, data["cols"])) for data in all_subjects]

    def _subjects_choice_fields(self, subject_field):
        all_subjects = self._get_all_subject()
        all_subject_choices = self._get_all_choices(all_subjects)
        instruction_for_subject_field = ugettext("Choose Subject from this list.")
        return self._get_choice_field(all_subject_choices, subject_field, help_text=instruction_for_subject_field)