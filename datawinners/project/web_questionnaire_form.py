from django.forms import Form, CharField, HiddenInput, RegexField
from entity.helper import get_country_appended_location
from mangrove.form_model.field import HierarchyField
from mangrove.form_model.form_model import LOCATION_TYPE_FIELD_NAME
from mangrove.form_model.validation import TextLengthConstraint
from project.questionnaire_fields import FormField, css_class
from questionnaire.helper import get_location_field_code
from django.utils.translation import ugettext_lazy as _
#
#
# class WebQuestionnaireForm(Form):
#     def __init__(self, subject_question_creator, form_model, is_update=False):
#         super(WebQuestionnaireForm, self).__init__()
#         self.country = None
#         self.form_model = form_model
#         self.is_update = is_update
#         self.subject_question_creator = subject_question_creator
#
#         if self.form_model.is_entity_registration_form():
#             self.fields[u't'] = CharField(widget=HiddenInput, initial=self.form_model.entity_type[0])
#             self.fields[u'short_code_question_code'] = self.form_model.entity_question.code
#             for field in self.form_model.fields[:-1]:
#                 form_field = FormField().create(field)
#                 self.fields[field.code] = form_field
#             self.fields[self.form_model.fields[-1].code] = self._get_short_code_django_field(self.form_model.fields[-1])
#         else:
#             subject_question = self.form_model.entity_question
#             if subject_question is not None:
#                 self.fields[subject_question.code] = (self.subject_question_creator.create(subject_question))
#                 self.fields['entity_question_code'] = CharField(required=False, widget=HiddenInput,
#                                                                 label=subject_question.code)
#                 self.fields[u'short_code_question_code'] = self.form_model.entity_question.code
#
#                 for field in self.form_model.fields:
#                     if not field.is_entity_field:
#                         self.fields[field.code] = FormField().create(field)
#
#     def _get_short_code_django_field(self, field):
#         max_length = None
#         min_length = None
#         for constraint in field.constraints:
#             if isinstance(constraint, TextLengthConstraint):
#                 max_length = constraint.max
#                 min_length = constraint.min
#         django_field = RegexField("^[a-zA-Z0-9]+$", label=field.label, initial=field.value,
#                                   required=field.is_required(), max_length=max_length, min_length=min_length,
#                                   help_text=field.instruction,
#                                   error_message=_("Only letters and numbers are valid"))
#         if self.is_update:
#             django_field.widget.attrs['readonly'] = 'readonly'
#         self._create_field_type_class(django_field, field)
#         return django_field
#
#     def _create_field_type_class(self, char_field, field):
#         self._insert_location_field_class_attributes(char_field, field)
#         self._put_subject_field_class_attributes(char_field, field)
#
#     def _insert_location_field_class_attributes(self, char_field, field):
#         if field.name == LOCATION_TYPE_FIELD_NAME and isinstance(field, HierarchyField):
#             char_field.widget.attrs['class'] = 'location_field'
#
#     def _put_subject_field_class_attributes(self, char_field, field):
#         if field.is_entity_field:
#             char_field.widget.attrs['class'] = 'subject_field'
#
#     def clean(self):
#         location_field_code = get_location_field_code(self.form_model)
#
#         # self.cleaned_data.pop('entity_question_code', '')
#         if location_field_code is None:
#             return self.cleaned_data
#
#         for question_code, values in self.cleaned_data.items():
#             if question_code == location_field_code:
#                 self.cleaned_data[question_code] = get_country_appended_location(values, self.country)
#
#         return self.cleaned_data
#

class WebForm(Form):
    def __init__(self, form_model, data):
        super(WebForm, self).__init__(data=data)
        self.form_model = form_model
        ## This case of checking for None entity question happens when we preview the questionnaire while creating a project.
        self.short_code_question_code = self.form_model.entity_question.code if self.form_model.entity_question else None
        self.fields['form_code'] = CharField(widget=HiddenInput, initial=form_model.form_code)


class SubjectRegistrationForm(WebForm):
    def __init__(self, form_model, data=None, country=None):
        super(SubjectRegistrationForm, self).__init__(form_model, data)
        self.country = country
        self.fields[u't'] = CharField(widget=HiddenInput, initial=self.form_model.entity_type[0])
        for field in self.form_model.fields:
            if not field.is_entity_field:
                self.fields[field.code] = FormField().create(field)
            else:
                self.fields[field.code] = self.regex_field(field)

    def regex_field(self, field):
        max_length = None
        min_length = None
        for constraint in field.constraints:
            if isinstance(constraint, TextLengthConstraint):
                max_length = constraint.max
                min_length = constraint.min
        regex_field = RegexField("^[a-zA-Z0-9]+$", label=field.label, initial=field.value,
                                 required=field.is_required(), max_length=max_length, min_length=min_length,
                                 help_text=field.instruction, error_message=_("Only letters and numbers are valid"),
        )
        regex_field.widget.attrs['class'] = css_class(field)
        return regex_field


    def clean(self):
        location_field_code = get_location_field_code(self.form_model)

        if location_field_code is None:
            return self.cleaned_data

        for question_code, values in self.cleaned_data.items():
            if question_code == location_field_code:
                self.cleaned_data[question_code] = get_country_appended_location(values, self.country)

        return self.cleaned_data


class SurveyResponseForm(WebForm):
    def __init__(self, form_model, subject_question_creator, data=None):
        super(SurveyResponseForm, self).__init__(form_model, data)
        for field in self.form_model.fields:
            if not field.is_entity_field:
                self.fields[field.code] = FormField().create(field)
            else:
                self.fields[field.code] = subject_question_creator.create(field)
                self.fields['entity_question_code'] = CharField(required=False, widget=HiddenInput,
                                                                label=field.code)
