from django import forms
from django.forms.fields import CharField, ChoiceField, MultipleChoiceField
from django.forms.forms import Form
from django.forms.widgets import CheckboxSelectMultiple, HiddenInput
from mangrove.form_model.field import SelectField

class WebQuestionnaireFormCreater(object):
    def create(self, form_model):
        properties = {field.code: self._get_django_field(field) for field in form_model.fields}
        properties.update({'form_code': forms.CharField(widget=HiddenInput, initial=form_model.form_code)})
        
        return type('QuestionnaireForm', (Form, ), properties)

    def _get_django_field(self,field):

        try:
            field_creation_map={SelectField:self._create_select_field}
            return field_creation_map[type(field)](field)
        except KeyError:
            return self._create_char_field(field)


#        if isinstance(field, SelectField):
#            return  create_select_field(field, create_choices(field))
#        if field.is_entity_field:
#            return create_entity_select_field_for_reporter(field,associated_entities)
#        display_field = CharField(label=field.name, initial=field.value, required=field.is_required(), help_text=field.instruction)
#        display_field.widget.attrs["watermark"] = field.get_constraint_text()
#        display_field.widget.attrs['style'] = 'padding-top: 7px;'
#        #    display_field.widget.attrs["watermark"] = "18 - 1"
#        return display_field

    def _create_char_field(self,field):
        char_field = forms.CharField(label=field.name, initial=field.value, required=field.is_required(),
            help_text=field.instruction)
        char_field.widget.attrs["watermark"] = field.get_constraint_text()
        char_field.widget.attrs['style'] = 'padding-top: 7px;'

        return char_field

    def _create_select_field(self,field):
        if field.single_select_flag:
            return ChoiceField(choices=self._create_choices(field), required=field.is_required(), label=field.name, initial=field.value, help_text=field.instruction)
        return forms.MultipleChoiceField(label=field.name, widget=forms.CheckboxSelectMultiple, choices=self._create_choices(field),
                                  initial=field.value, required=field.is_required(), help_text=field.instruction)
    def _create_choices(self,field):
        choice_list = [('', '--None--')] if field.single_select_flag else []
        choice_list.extend([(option['val'], option['text']['en']) for option in field.options])
        choices = tuple(choice_list)
        return choices

def create_select_field(field, choices):
    if field.single_select_flag:
        return ChoiceField(choices=choices, required=field.is_required(), label=field.name, initial=field.value, help_text=field.instruction)
    return MultipleChoiceField(label=field.name, widget=CheckboxSelectMultiple, choices=choices,
                                  initial=field.value, required=field.is_required(), help_text=field.instruction)


def create_choices(field):
    choice_list = [('', '--None--')] if field.single_select_flag else []
    choice_list.extend([(option['val'], option['text']['en']) for option in field.options])
    choices = tuple(choice_list)
    return choices


def create_choices_for_reporter(choices):
    choice_list = [('', '--None--')]
    if choices is not None:
        choice_list.extend(choice for choice in choices)
    return tuple(choice_list)


def create_entity_select_field_for_reporter(field,associated_entities):
    choices = create_choices_for_reporter(associated_entities)
    return ChoiceField(choices = choices,required=field.is_required,label=field.name,initial=field.value,help_text=field.instruction)


