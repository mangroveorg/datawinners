# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.forms.fields import CharField, ChoiceField, MultipleChoiceField
from django.forms.forms import Form
from django.forms.widgets import RadioFieldRenderer, RadioInput
from django import forms


class MyRadioFieldRenderer(RadioFieldRenderer):
    def __init__(self, name, value, attrs, choices):
        self.name, self.value, self.attrs = name, value, attrs
        self.choices = choices

    def __iter__(self):
        for i, choice in enumerate(self.choices):
            attrs = self.attrs.copy()
            if choice[0] == 'public information':
                attrs['disabled'] = 'disabled'
            if choice[0] == 'survey':
                attrs['checked'] = True
            yield RadioInput(self.name, self.value, attrs, choice, i)


class MyRadioSelect(forms.RadioSelect):
    renderer = MyRadioFieldRenderer


class ProjectProfile(Form):
    PROJECT_TYPE_CHOICES = (('survey', 'Survey project: I want to collect data from the field'),
                            ('public information', 'Public information: I want to send information'))
    DEVICE_CHOICES = (('sms', 'SMS'), ('smartphone', 'Smart Phone'), ('web', 'Web'))
    id = CharField(required=False)
    name = CharField(required=True)
    goals = CharField(max_length=300, widget=forms.Textarea, label='Project Background And Goals', required=False)
    project_type = ChoiceField(label='Project Type', required=True, widget=MyRadioSelect, choices=PROJECT_TYPE_CHOICES)
    entity_type = ChoiceField(label="Subjects", required=True)
    devices = MultipleChoiceField(label='Device', widget=forms.CheckboxSelectMultiple, choices=DEVICE_CHOICES,
                                  initial=DEVICE_CHOICES[2], required=False)

    def __init__(self,entity_list , *args, **kwargs):
        super(ProjectProfile, self).__init__(*args, **kwargs)
        entity_list = entity_list
        self.fields['entity_type'].choices = [(t, '.'.join(t)) for t in entity_list]
