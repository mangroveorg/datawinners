from django.forms import CharField, HiddenInput, ChoiceField
from django.forms.forms import Form
from django.utils.translation import ugettext_lazy as _

from datawinners.project.questionnaire_fields import FormField, as_choices
from datawinners.project.subject_question_creator import SubjectQuestionFieldCreator


class EditSubmissionForm(Form):
    def __init__(self, manager, project, data):
        super(EditSubmissionForm, self).__init__(data=data)
        self.form_model = project
        self.fields['form_code'] = CharField(widget=HiddenInput, initial=project.form_code)
        choices = as_choices(project.get_data_senders(manager))
        self.fields['dsid'] = ChoiceField(label=_('I am submitting this data on behalf of'),
                                          choices=choices,
                                          help_text=_('Choose Data Sender from this list.'))

        for field in project.fields:
            if field.is_entity_field:
                self.fields[field.code] = SubjectQuestionFieldCreator(manager, self.form_model).create(field)
            else:
                form_field = FormField().create(field)
                form_field.initial = data.get(field.code) if data.get(field.code) is not None else data.get(
                    field.code.lower())
                self.fields[field.code] = form_field


    def populate(self, fields):
        for code, form_field in fields.iteritems():
            self.fields[code] = form_field
