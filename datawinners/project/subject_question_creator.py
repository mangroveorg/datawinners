from django import forms
from django.forms.widgets import HiddenInput
from django.utils.translation import ugettext

from datawinners.utils import translate, get_text_language_by_instruction


class UniqueIdChoiceField(forms.ChoiceField):
    def __init__(self, entity_type, *args, **kwargs):
        super(UniqueIdChoiceField, self).__init__(*args, **kwargs)
        self.entity_type = entity_type


class SubjectQuestionFieldCreator(object):
    def __init__(self, project):
        self.project = project
        self.dbm = project._dbm

    def create(self, subject_field):
        return self._subjects_choice_fields(subject_field)

    def _get_choice_field(self, subject_choices, subject_field, help_text, widget=None):
        subject_choice_field = UniqueIdChoiceField(entity_type=subject_field.unique_id_type,
                                                   required=subject_field.is_required(), choices=subject_choices,
                                                   label=subject_field.name, widget=widget,
                                                   initial=subject_field.value, help_text=help_text)
        subject_choice_field.widget.attrs['class'] = 'subject_field'
        return subject_choice_field

    def _get_all_options(self, entity_type):
        start_key = [[entity_type]]
        end_key = [[entity_type], {}]
        rows = self.dbm.database.view("entity_name_by_short_code/entity_name_by_short_code", startkey=start_key,
                                      endkey=end_key).rows
        all_subject_choices = [(item["key"][1], item["value"] + "(" + item["key"][1] + ")") for item in rows]
        return all_subject_choices # [(u'cid001', u'Test (cid001)'),(u'cid002', u'Test(cid002')..]

    def _subjects_choice_fields(self, subject_field):
        unique_id_type = subject_field.unique_id_type
        all_subject_choices = self._get_all_options(unique_id_type)
        language = get_text_language_by_instruction(subject_field.instruction)
        instruction_for_subject_field = translate(
            "Choose %(entity_type)s from this list." % {'entity_type': unique_id_type}, func=ugettext,
            language=language) if all_subject_choices else ''
        return self._get_choice_field(all_subject_choices, subject_field, help_text=instruction_for_subject_field)

