from django.forms import CharField, HiddenInput, ChoiceField
from django.forms.forms import Form
from django.utils.translation import ugettext_lazy as _, gettext
from mangrove.form_model.field import UniqueIdField

from datawinners.project.questionnaire_fields import FormField, as_choices
from datawinners.project.subject_question_creator import SubjectQuestionFieldCreator
from django.core.exceptions import ValidationError
from operator import itemgetter

class BaseSubmissionForm(Form):
    def __init__(self, project, data, is_datasender, datasender_name, reporter_id, reporter_name,
                 is_linked, is_anonymous_submission, initial=None):
        super(BaseSubmissionForm, self).__init__(data, initial=initial)
        self.form_model = project
        self.fields['form_code'] = CharField(widget=HiddenInput, initial=project.form_code)
        self.is_datasender = is_datasender
        if not is_datasender:

            default_choice = [("", gettext("Choose Data Sender"))]
            list_ds = (as_choices(project.get_data_senders(project._dbm)))
            if not is_linked:
                list_ds.append((reporter_id, reporter_name))
            list_sorted = sorted(list_ds, key=itemgetter(1))
            default_choice.extend(list_sorted)
            if data:
                error_message = {'invalid_choice':_("The Data Sender %s (%s) is not linked to your Questionnaire.") % (datasender_name, data.get("dsid"))}
            else:
                error_message = None

            if not is_anonymous_submission:
                self.fields['dsid'] = ChoiceField(label=_('I want to submit this data on behalf of a registered Data Sender'),
                                          choices=default_choice,
                                          error_messages=error_message)


class SurveyResponseForm(BaseSubmissionForm):
    def __init__(self, project, data=None, is_datasender=False, datasender_name='', reporter_id=None,
                 reporter_name=None, is_linked=False, is_anonymous_submission=False, initial=None):
        super(SurveyResponseForm, self).__init__(project, data, is_datasender, datasender_name, reporter_id,
                                                 reporter_name, is_linked, is_anonymous_submission, initial)

        for field in self.form_model.fields:
            if isinstance(field, UniqueIdField):
                self.fields[field.code] = SubjectQuestionFieldCreator(self.form_model).create(field)
            else:
                form_field = FormField().create(field)
                if data:
                    form_field.initial = data.get(field.code)
                self.fields[field.code] = form_field

    def clean(self):
        cleaned_data = self.cleaned_data
        #cleaned_data = super(SurveyResponseForm, self).clean()
        cleaned_data.pop('dsid', None)
        return cleaned_data

#
# class SurveyResponseForm(SurveyResponseForm):
#     def __init__(self, project, data, datasender_name=""):
#         super(EditSubmissionForm, self).__init__(project, data, False, datasender_name)

    #
    #     for field in project.fields:
    #         if field.is_entity_field:
    #             self.fields[field.code] = SubjectQuestionFieldCreator(self.form_model).create(field)
    #         else:
    #             form_field = FormField().create(field)
    #             form_field.initial = data.get(field.code) if data.get(field.code) else data.get(field.code.lower())
    #             self.fields[field.code] = form_field
    #
    # def clean(self):
    #     cleaned_data = self.cleaned_data
    #     cleaned_data.pop('dsid')
    #     return cleaned_data
    #
    # def populate(self, fields):
    #     for code, form_field in fields.iteritems():
    #         self.fields[code] = form_field
