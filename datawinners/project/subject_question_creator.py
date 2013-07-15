from django import forms
from django.forms.fields import ChoiceField
from django.forms.widgets import HiddenInput
from django.utils.translation import ugettext
from datawinners.entity.import_data import load_all_subjects_of_type
from datawinners.utils import translate, get_text_language_by_instruction


class SubjectQuestionFieldCreator(object):
    def __init__(self, dbm, project):
        self.project = project
        self.dbm = dbm

    def create(self, subject_field):
        reporter_entity_type = 'reporter'
        if self.project.is_on_type(reporter_entity_type):
            return self._data_sender_choice_fields(subject_field)
        return self._subjects_choice_fields(subject_field)

    def create_code_hidden_field(self, subject_field):
        return {'entity_question_code': forms.CharField(required=False, widget=HiddenInput, label=subject_field.code)}

    def get_key(self, subject):
        return subject['unique_id']

    def get_value(self, subject):
        return subject['name'] + '  (' + subject['short_code'] + ')'

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

    def _get_all_options(self):
        entity_type = self.project.entity_type
        start_key = [[entity_type]]
        end_key = [[entity_type], {}, {}]
        rows = self.dbm.database.view("entity_name_by_short_code/entity_name_by_short_code", start_key=start_key, end_key=end_key).rows
        all_subject_choices = [(item["key"][1], item["value"] + "(" + item["key"][1] + ")") for item in rows]
        return all_subject_choices # [(u'cid001', u'Test (cid001)'),(u'cid002', u'Test(cid002')..]

    def _subjects_choice_fields(self, subject_field):
        all_subject_choices = self._get_all_options()
        language = get_text_language_by_instruction(subject_field.instruction)
        instruction_for_subject_field = translate("Choose Subject from this list.", func=ugettext, language=language)
        return self._get_choice_field(all_subject_choices, subject_field, help_text=instruction_for_subject_field)


    def _data_to_choice(self, subject):
        return self.get_key(subject), self.get_value(subject)

    def _get_all_choices(self, entities):
        return [(entity['short_code'], entity['name'] + '  (' + entity['short_code'] + ')') for entity in entities]