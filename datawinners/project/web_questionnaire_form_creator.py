from django import forms
from django.forms.fields import ChoiceField
from django.forms.forms import Form
from django.forms.widgets import HiddenInput
from entity.import_data import load_all_subjects_of_type
from mangrove.form_model.field import SelectField, field_attributes

class WebQuestionnaireFormCreater(object):
    def __init__(self, subject_question_creator):
        self.subject_question_creator = subject_question_creator


    def create(self, form_model):
        properties = dict()
        subject_question = form_model.entity_question
        if subject_question is not None:
            properties.update(self._get_subject_web_question(subject_question))
            properties.update(self.subject_question_creator.create_code_hidden_field(subject_question))
        properties.update(
            {field.code: self._get_django_field(field) for field in form_model.fields if not field.is_entity_field})
        properties.update(self._get_form_code_hidden_field(form_model))

        return type('QuestionnaireForm', (Form, ), properties)

    def _get_subject_web_question(self, subject_question):
        return {subject_question.code: (self.subject_question_creator.create(subject_question))}

    def _get_form_code_hidden_field(self, form_model):
        return {'form_code': forms.CharField(widget=HiddenInput, initial=form_model.form_code)}

    def _get_django_field(self, field):
        try:
            field_creation_map = {SelectField: self._create_select_field}
            return field_creation_map[type(field)](field)
        except KeyError:
            return self._create_char_field(field)


    def _create_char_field(self, field):
        char_field = forms.CharField(label=field.name, initial=field.value, required=field.is_required(),
            help_text=field.instruction)
        char_field.widget.attrs["watermark"] = field.get_constraint_text()
        char_field.widget.attrs['style'] = 'padding-top: 7px;'

        return char_field

    def _create_select_field(self, field):
        if field.single_select_flag:
            return ChoiceField(choices=self._create_choices(field), required=field.is_required(), label=field.name,
                initial=field.value, help_text=field.instruction)
        return forms.MultipleChoiceField(label=field.name, widget=forms.CheckboxSelectMultiple,
            choices=self._create_choices(field),
            initial=field.value, required=field.is_required(), help_text=field.instruction)

    def _create_choices(self, field):
        choice_list = [('', '--None--')] if field.single_select_flag else []
        choice_list.extend([(option['val'], option['text']['en']) for option in field.options])
        choices = tuple(choice_list)
        return choices

    def _get_subject_question_code_hidden_field(self, subject_question):
        return {'subject_question_code':forms.CharField(widget=HiddenInput,initial=subject_question.code)}


class SubjectQuestionFieldCreator(object):
    def __init__(self, dbm, project,project_subject_loader=None):
        #for testing
        self.project_subject_loader=load_all_subjects_of_type if project_subject_loader is None else project_subject_loader
        self.project = project
        self.dbm = dbm

    def create(self, subject_field):
        reporter_entity_type = 'reporter'
        if self.project.is_on_type(reporter_entity_type):
            return self._data_sender_choice_fields(subject_field)
        return self._subjects_choice_fields(subject_field)

    def create_code_hidden_field(self,subject_field):
        return {'subject_question_code': forms.CharField(widget=HiddenInput, initial=subject_field.code)}

    def _get_choice_field(self, data_sender_choices, subject_field):
        return ChoiceField(required=subject_field.is_required(), choices=data_sender_choices, label=subject_field.name,
            initial=subject_field.value, help_text=subject_field.instruction)

    def _data_sender_choice_fields(self, subject_field):
        data_senders = self.project.get_data_senders(self.dbm)
        data_sender_choices = self._get_all_choices(data_senders)
        return self._get_choice_field(data_sender_choices, subject_field)


    def _get_all_choices(self, all_subjects):
        return [(data_sender['short_name'], data_sender[field_attributes.NAME]+'  ('+data_sender['short_name']+')')for data_sender in
                                                                               all_subjects]

    def _subjects_choice_fields(self, subject_field):
        all_subjects = self.project_subject_loader(self.dbm, type=self.project.entity_type)
        all_subject_choices = self._get_all_choices(all_subjects)
        return self._get_choice_field(all_subject_choices, subject_field)



