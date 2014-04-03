from django.forms import CharField, HiddenInput, ChoiceField
from django.forms.forms import Form
from django.utils.translation import ugettext_lazy as _
from mangrove.form_model.field import UniqueIdField

from datawinners.project.questionnaire_fields import FormField, as_choices
from datawinners.project.subject_question_creator import SubjectQuestionFieldCreator
from django.core.exceptions import ValidationError

class BaseSubmissionForm(Form):
    def __init__(self, data, project, is_datasender, datasender_name):
        super(BaseSubmissionForm, self).__init__(data)
        self.form_model = project
        self.fields['form_code'] = CharField(widget=HiddenInput, initial=project.form_code)
        if not is_datasender:
            choices = as_choices(project.get_data_senders(project._dbm))

            if data:
                error_message = {'invalid_choice':_("The Data Sender %s (%s) is not linked to your Questionnaire.") % (datasender_name, data.get("dsid"))}
            else:
                error_message = None
            self.fields['dsid'] = ChoiceField(label=_('I am submitting this data on behalf of'),
                                          choices=choices,
                                          error_messages=error_message,
                                          help_text=_('Choose Data Sender from this list.'))


class SurveyResponseForm(BaseSubmissionForm):
    def __init__(self, project, data=None, is_datasender=False):
        super(SurveyResponseForm, self).__init__(data, project, is_datasender, "")

        for field in self.form_model.fields:
            if isinstance(field, UniqueIdField):
                self.fields[field.code] = SubjectQuestionFieldCreator(self.form_model).create(field)
            else:
                self.fields[field.code] = FormField().create(field)

    def clean(self):
        return self.cleaned_data


class EditSubmissionForm(BaseSubmissionForm):
    def __init__(self, project, data, datasender_name=""):
        super(EditSubmissionForm, self).__init__(data, project, False, datasender_name)


        for field in project.fields:
            if field.is_entity_field:
                self.fields[field.code] = SubjectQuestionFieldCreator(self.form_model).create(field)
            else:
                form_field = FormField().create(field)
                form_field.initial = data.get(field.code) if data.get(field.code) is not None else data.get(
                    field.code.lower())
                self.fields[field.code] = form_field


    def populate(self, fields):
        for code, form_field in fields.iteritems():
            self.fields[code] = form_field
