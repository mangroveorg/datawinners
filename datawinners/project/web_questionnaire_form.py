from django.forms import Form, CharField, HiddenInput, RegexField
from django.utils.translation import ugettext_lazy as _
from datawinners.entity.helper import get_country_appended_location, get_subject_field_instruction
from datawinners.project.questionnaire_fields import FormField, css_class
from datawinners.questionnaire.helper import get_location_field_code
from mangrove.form_model.field import UniqueIdField

from mangrove.form_model.validation import TextLengthConstraint
from datawinners.project.subject_question_creator import SubjectQuestionFieldCreator

class WebForm(Form):
    def __init__(self, form_model, data):
        super(WebForm, self).__init__(data=data)
        self.form_model = form_model
        ## This case of checking for None entity question happens when we preview the questionnaire while creating a project.
        #todo: Check what is this for
        self.short_code_question_code = self.form_model.entity_questions[0].code if self.form_model.entity_questions else None
        self.fields['form_code'] = CharField(widget=HiddenInput, initial=form_model.form_code)


class SubjectRegistrationForm(WebForm):
    def __init__(self, form_model, data=None, country=None):
        super(SubjectRegistrationForm, self).__init__(form_model, data)
        self.country = country
        self.fields[u't'] = CharField(widget=HiddenInput, initial=self.form_model.entity_type[0])
        for field in self.form_model.fields:
            if isinstance(field, UniqueIdField):
                self.fields[field.code] = SubjectQuestionFieldCreator(self.form_model,has_linked_idnr=True).create(field)
            elif field.is_entity_field:
                self.fields[field.code] = self.regex_field(field)
            else:
                field.set_instruction(get_subject_field_instruction(field, entity_type=self.form_model.entity_type[0]))
                self.fields[field.code] = FormField().create(field)

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


