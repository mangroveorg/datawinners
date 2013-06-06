from django.forms.forms import Form
from datawinners.entity.helper import get_country_appended_location
from datawinners.questionnaire.helper import get_location_field_code, get_geo_code_fields_question_code
from datawinners.project.questionnaire_fields import SubjectCodeField, SubjectField, FormField, FormCodeField
from datawinners.questionnaire.helper import make_clean_geocode_method

class SubmissionForm(Form):

    @staticmethod
    def create(manager, project, questionnaire_form_model):
        properties = dict()
        properties.update({'form_model': questionnaire_form_model})

        geo_code_fields_code = get_geo_code_fields_question_code(questionnaire_form_model)
        for geo_code_field_code in geo_code_fields_code:
            properties.update({'clean_' + geo_code_field_code: make_clean_geocode_method(geo_code_field_code)})

        subject_question = questionnaire_form_model.entity_question
        if subject_question is not None:
            properties.update(SubjectField(manager,project).create(subject_question, project.entity_type))
            properties.update(SubjectCodeField().create(subject_question.code))
            properties.update({u'short_code_question_code': questionnaire_form_model.entity_question.code})

        properties.update({field.code: FormField().create(field) for field in questionnaire_form_model.fields if
                           not field.is_entity_field})
        properties.update(FormCodeField().create(questionnaire_form_model.form_code))
        return type('BoundSubmissionForm', (SubmissionForm,), properties)

    def __init__(self, country=None, *args, **kwargs):
        self.country = country
        super(SubmissionForm, self).__init__(*args, **kwargs)

    def initial_values(self, initial):
        for field_name, field in self.fields.iteritems():
            if not field.widget.is_hidden:
                field.initial = initial.get(field_name) if initial.get(field_name) is not None else initial.get(field_name.lower())

    def bind(self, data):
        if data:
            self.data = data
            self.is_bound = True

    def clean(self):
        location_field_code = get_location_field_code(self.form_model)
        self.cleaned_data.pop('entity_question_code', '')
        if location_field_code is None:
            return self.cleaned_data

        for question_code, values in self.cleaned_data.items():
            if question_code == location_field_code:
                self.cleaned_data[question_code] = get_country_appended_location(values, self.country)

        return self.cleaned_data

