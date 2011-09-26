# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import calendar

from django.forms.fields import CharField, ChoiceField, MultipleChoiceField, BooleanField
from django.core.exceptions import ValidationError
from django.forms.forms import Form
from django.utils.translation import ugettext_lazy as _
from django.forms.widgets import RadioFieldRenderer, RadioInput, RadioSelect
from django import forms
from mangrove.form_model.form_model import REPORTER


class MyRadioFieldRenderer(RadioFieldRenderer):
    def __init__(self, name, value, attrs, choices):
        self.name, self.value, self.attrs = name, value, attrs
        self.choices = choices

    def __iter__(self):
        for i, choice in enumerate(self.choices):
            attrs = self.attrs.copy()
            if choice[0] == 'public information':
                attrs['disabled'] = 'disabled'
            if choice[0] == 'open':
                attrs['disabled'] = 'disabled'
            if choice[0] == 'survey':
                attrs['checked'] = True
            if choice[0] == 'close':
                attrs['checked'] = True
            yield RadioInput(self.name, self.value, attrs, choice, i)


class MyRadioSelect(forms.RadioSelect):
    renderer = MyRadioFieldRenderer

def convert_to_ordinal(n):
    if 10 < n < 14: return u'%sth' % n
    if n % 10 == 1: return u'%sst' % n
    if n % 10 == 2: return u'%snd' % n
    if n % 10 == 3: return u'%srd' % n
    return u'%sth' % n

class ProjectProfile(Form):
    PROJECT_TYPE_CHOICES = (('survey', _('Survey project: I want to collect data from the field')),
                            ('public information', _('Public information: I want to send information')))
    DEVICE_CHOICES = (('sms', 'SMS'),)
    SUBJECT_TYPE_CHOICES = (('yes',_('Work performed by the data sender (eg. monthly activity report)')),('no',_('Other Subject')))
    GROUP_TYPE_CHOICES = (('open',_('Open Data Sender Group. Anyone can send in data without registering')),('close',_('Closed Data Sender Group. Only registered data sender will be able to send data')))
    FREQUENCY_CHOICES = ((False, _("Whenever a DataSender has data for us")), (True, _("Every")))
    id = CharField(required=False)
    name = CharField(required=True, label=_("Name this Project"))
    goals = CharField(max_length=300, widget=forms.Textarea, label=_('Project Description'), required=False)
    project_type = ChoiceField(label=_('Project Type'), widget=MyRadioSelect, choices=PROJECT_TYPE_CHOICES)
    sender_group = ChoiceField(label=_('Open or Closed Group'), widget=MyRadioSelect, choices=GROUP_TYPE_CHOICES)
    activity_report = ChoiceField(label=_("What is this questionnaire about?"), widget=forms.RadioSelect, choices=SUBJECT_TYPE_CHOICES, initial=('no',_('Other Subject')))
    entity_type = ChoiceField(label=_("Other Subjects"), required=False)
    devices = MultipleChoiceField(label=_('Device'), widget=forms.CheckboxSelectMultiple, choices=DEVICE_CHOICES,
                                  initial=DEVICE_CHOICES[0], required=False)
    frequency_enabled = ChoiceField(label = _("How often do you need the data?"),
                                    choices=FREQUENCY_CHOICES, widget=forms.RadioSelect, required=True,initial=False)
    frequency_period = ChoiceField(choices=(('week', _('Week')), ('month', _('Month')),), widget=forms.Select(attrs={'style':'margin-left: -167px; margin-top: 19px;'}), required=False)
    has_deadline = ChoiceField(label=_("Do you want to set a deadline?"), widget=forms.RadioSelect, choices=((False, _('No')), (True, _('Yes'))), required=False, initial=False)
    deadline_month =  ChoiceField(choices=(tuple([(n,convert_to_ordinal(n)) for n in range(1,31)])), widget=forms.Select, required=False)
    deadline_week =  ChoiceField(choices=(tuple(zip(range(1,8), calendar.day_name))), widget=forms.Select(attrs={'data-bind':'random'}), required=False)
    deadline_type =  ChoiceField(choices=(('That', _('That')), ('Following', _('Following'))), widget=forms.Select, required=False)
    reminders_enabled = ChoiceField(choices=((True, _('Yes')), (False, _('No'))), label=_("Do you want to remind DataSenders to send in their data?"), required=False, initial=False, widget=forms.RadioSelect)


    def __init__(self, entity_list,  *args, **kwargs):
        assert isinstance(entity_list, list)
        super(ProjectProfile, self).__init__(*args, **kwargs)
        self.fields['entity_type'].choices = [(t[-1], t[-1]) for t in entity_list]
        self.fields['name'].widget.attrs['watermark'] = _("Enter a project name")
        self.fields['goals'].widget.attrs['watermark'] = _("Describe what your team hopes to achieve by collecting this data")


    def clean_entity_type(self):
        if self.cleaned_data.get('entity_type') == "" and self.cleaned_data.get("activity_report") == 'no' :
            raise ValidationError(_("This field is required"))
        return self.cleaned_data.get('entity_type')

    def clean(self):
        if self.cleaned_data.get("activity_report") == 'yes':
            self.cleaned_data['entity_type'] = REPORTER
            if self.errors.get('entity_type') is not None:
                self.errors['entity_type'] = ""

        return self.cleaned_data