from django.forms import CharField, HiddenInput
from django.forms.forms import Form
from datawinners.project.questionnaire_fields import EntityField, FormField


class EditSubmissionForm(Form):
    def __init__(self, manager, questionnaire_form_model, data):
        super(EditSubmissionForm, self).__init__(data=data)
        self.form_model = questionnaire_form_model
        self.fields['form_code'] = CharField(widget=HiddenInput, initial=questionnaire_form_model.form_code)
        if questionnaire_form_model.entity_question is not None:
            entity_question = questionnaire_form_model.entity_question
            choices = EntityField(manager, questionnaire_form_model).create(entity_question, questionnaire_form_model.entity_type)
            self.fields[entity_question.code] = choices.get(entity_question.code)
            self.short_code_question_code = questionnaire_form_model.entity_question.code

        for field in questionnaire_form_model.fields:
            if not field.is_entity_field:
                form_field = FormField().create(field)
                form_field.initial = data.get(field.code) if data.get(field.code) is not None else data.get(
                    field.code.lower())
                self.fields[field.code] = form_field


    def populate(self, fields):
        for code, form_field in fields.iteritems():
            self.fields[code] = form_field
