# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import calendar
from django.db.models.fields import TextField

from django.forms.fields import CharField, ChoiceField, MultipleChoiceField
from django.core.exceptions import ValidationError
from django.forms.forms import Form
from django.utils.translation import ugettext_lazy as _, ugettext_lazy
from django.forms.widgets import RadioFieldRenderer, RadioInput
from django import forms
from datawinners.utils import convert_to_ordinal
from mangrove.form_model.form_model import REPORTER

class BroadcastMessageForm(forms.Form):

    text = CharField(label=ugettext_lazy("Text:"), required=True, max_length=160, widget=forms.Textarea)
    to = ChoiceField(label=ugettext_lazy("To:"),choices=(("Associated", ugettext_lazy("Data Senders from my project")), ("All", ugettext_lazy("All Data Senders"))),
                     widget=forms.RadioSelect, initial=("Associated"))
    others = CharField(label=ugettext_lazy("Other People:"), max_length=160, widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super(BroadcastMessageForm, self).__init__(*args, **kwargs)
        self.fields['text'].widget.attrs['watermark'] = ugettext_lazy('Enter your SMS text')
        self.fields['others'].widget.attrs['watermark'] = ugettext_lazy('Enter your recipient(s) telephone number. Use a comma (,) to separate the numbers.')


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


def get_translated_weekdays():
    translated_weekdays = []
    weekdays = tuple(zip(range(1, 8), calendar.day_name))
    for weekday in weekdays:
        translated_weekdays.append((weekday[0], _(weekday[1])))
    return tuple(translated_weekdays)


class ProjectProfile(Form):
    PROJECT_TYPE_CHOICES = (('survey', _('Survey project: I want to collect data from the field')),
                            ('public information', _('Public information: I want to send information')))
    DEVICE_CHOICES = (('sms', 'SMS'), ('web', 'WEB'))
    SUBJECT_TYPE_CHOICES = (
        ('yes', _('Work performed by the data sender (eg. monthly activity report)')), ('no', _('Other Subject')))
    sender_close_group_description = 'Closed Data Sender Group. Only registered data sender will be able to send data'
    sender_open_group_description = 'Open Data Sender Group. Anyone can send in data without registering'
    GROUP_TYPE_CHOICES = (('open', _(sender_open_group_description)), ('close', _(
        sender_close_group_description)))
    FREQUENCY_CHOICES = ((False, _("Whenever a data sender has data for us")), (True, _("Every")))
    LANGUAGES = (('en', 'English'), ('fr', 'Français'))
    id = CharField(required=False)
    name = CharField(required=True, label=_("Name this Project"))
    goals = CharField(max_length=300, widget=forms.Textarea, label=_('Project Description'), required=False)
    project_type = ChoiceField(label=_('Project Type'), widget=MyRadioSelect, choices=PROJECT_TYPE_CHOICES)
    sender_open_close_group_header = 'Open or Closed Group'
    sender_close_group_header = 'Closed Group'
    sender_group = ChoiceField(label=_(sender_open_close_group_header), widget=MyRadioSelect,
                               choices=GROUP_TYPE_CHOICES)
    activity_report = ChoiceField(label=_("What is this questionnaire about?"), widget=forms.RadioSelect,
                                  choices=SUBJECT_TYPE_CHOICES, initial=('no', _('Other Subject')))
    entity_type = ChoiceField(label=_("Other Subjects"), required=False)
    devices = MultipleChoiceField(label=_('Device'), widget=forms.CheckboxSelectMultiple, choices=DEVICE_CHOICES,
                                  initial=['sms', 'web'], required=False)
    language = ChoiceField(label=_("Choose your language for success and error messages to Data Senders"),
                           widget=forms.RadioSelect,
                           choices=LANGUAGES, initial='en')
    frequency_enabled = ChoiceField(label=_("How often do you need the data?"),
                                    choices=FREQUENCY_CHOICES, widget=forms.RadioSelect, required=True, initial=False)
    frequency_period = ChoiceField(choices=(('week', _('Week')), ('month', _('Month')),),
                                   widget=forms.Select(attrs={'style': 'margin-left: -167px; margin-top: 19px;'}),
                                   required=False)
    has_deadline = ChoiceField(label=_("Do you want to set a deadline?"), widget=forms.RadioSelect,
                               choices=((False, _('No')), (True, _('Yes'))), required=False, initial=False)
    deadline_month = ChoiceField(
        choices=(tuple([(n, convert_to_ordinal(n)) for n in range(1, 31)] + [(31, 'Last Day')])), widget=forms.Select,
        required=False)
    deadline_week = ChoiceField(choices=(get_translated_weekdays()), widget=forms.Select(attrs={'data-bind': 'random'}),
                                required=False)
    deadline_type = ChoiceField(choices=(('Same', _('Same')), ('Following', _('Following'))), widget=forms.Select,
                                required=False)
    reminders_enabled = ChoiceField(choices=((False, _('No')), (True, _('Yes'))),
                                    label=_("Do you want to remind DataSenders to send in their data?"), required=False,
                                    initial=False, widget=forms.RadioSelect)


    def __init__(self, entity_list, *args, **kwargs):
        assert isinstance(entity_list, list)
        super(ProjectProfile, self).__init__(*args, **kwargs)
        self.fields['entity_type'].choices = [(t[-1], t[-1]) for t in entity_list]
        self.fields['name'].widget.attrs['watermark'] = _("Enter a project name")
        self.fields['goals'].widget.attrs['watermark'] = _(
            "Describe what your team hopes to achieve by collecting this data")


    def clean_entity_type(self):
        if self.cleaned_data.get('entity_type') == "" and self.cleaned_data.get("activity_report") == 'no':
            raise ValidationError(_("This field is required"))
        return self.cleaned_data.get('entity_type')

    def clean(self):
        if self.cleaned_data.get("activity_report") == 'yes':
            self.cleaned_data['entity_type'] = REPORTER
            if self.errors.get('entity_type') is not None:
                self.errors['entity_type'] = ""

        return self.cleaned_data


class CreateProject(Form):
    FREQUENCY_CHOICES = ((False, _("Whenever a data sender has data for us")), (True, _("Every")))

    QUESTIONNAIRE_CHOICES = (('yes', _("This is general activity report.")),
                             ('no', _("I am collecting data about a specific subject.")))
    CATEGORY_CHOICE = (('A person', _('A person')), ('A place', _('A place')),
                       ('A thing', _('A thing')), ('An event', _('An event')), )
    SUBJECT_CHOICE = (('Patient', _('Patient')), ('Farmer', _('Farmer')),
                      ('Child', _('Child')), ('Employee', _('Employee')), )
    LANGUAGES = (('en', 'English'), ('fr', 'Français'),('mg', 'Malagasy'))

    name = CharField(required=True, label=_("Name"))
    goals = CharField(max_length=300, widget=forms.Textarea, label=_('Description'), required=False)

    frequency_enabled = ChoiceField(label=_("Time Period"),
                                    help_text=ugettext_lazy("How often do you need data?"),
                                    choices=FREQUENCY_CHOICES, widget=forms.RadioSelect, required=True, initial=True)
    frequency_period = ChoiceField(choices=(('week', _('Week')), ('month', _('Month')),
                                            ('quarter', _('Quarter')), ), widget=forms.Select(
        attrs={'style': 'margin-left: 100px; margin-top: -58px; position: absolute'}),
                                   required=False, )
    activity_report = ChoiceField(label=_("What is this questionnaire about?"),
                                  choices=QUESTIONNAIRE_CHOICES,
                                  widget=forms.RadioSelect, required=False, initial='no')
    language = ChoiceField(label=_("Choose your language for success and error messages to Data Senders"),
                           widget=forms.RadioSelect,
                           choices=LANGUAGES, initial='en')

#TO-DO introduce this when we introduce categories
#    category = ChoiceField(choices=CATEGORY_CHOICE, required=False)

    entity_type = ChoiceField(required=False)

    def clean(self):

        if self.cleaned_data.get('entity_type') == "" and self.cleaned_data.get("activity_report") == 'no':
            self.errors['entity_type'] = _("This field is required")

        if self.cleaned_data.get("activity_report") == 'yes':
            self.cleaned_data['entity_type'] = REPORTER
            if self.errors.get('entity_type') is not None:
                self.errors['entity_type'] = ""

        return self.cleaned_data


    def __init__(self, entity_list, *args, **kwargs):
        assert isinstance(entity_list, list)
        super(CreateProject, self).__init__(*args, **kwargs)
        self.fields['entity_type'].choices = [(t[-1], t[-1]) for t in entity_list]
        self.fields['name'].widget.attrs['watermark'] = _("Enter a project name")
        self.fields['goals'].widget.attrs['watermark'] = _(
            "Describe what your team hopes to achieve by collecting this data")


class ReminderForm(Form):
    FREQUENCY_CHOICES = ((False, _("Whenever a data sender has data for us")), (True, _("Every")))
    frequency_enabled = ChoiceField(label=_("Time Period"),
                                    choices=FREQUENCY_CHOICES, widget=forms.RadioSelect, required=True, initial=False)
    frequency_period = ChoiceField(choices=(('week', _('Week')), ('month', _('Month')),
                                            ('quarter', _('Quarter')), ), widget=forms.Select(
        attrs={'style': 'margin-left: -138px; margin-top: 19px; position: absolute'}),
                                   required=False, )
    has_deadline = ChoiceField(label=_("Do you want to set a deadline?"), widget=forms.RadioSelect,
                               choices=((False, _('No')), (True, _('Yes'))), required=False, initial=False)
    deadline_month = ChoiceField(
        choices=(tuple([(n, convert_to_ordinal(n)) for n in range(1, 31)] + [(31, 'Last Day')])), widget=forms.Select,
        required=False)
    deadline_week = ChoiceField(choices=(get_translated_weekdays()), widget=forms.Select(attrs={'data-bind': 'random'}),
                                required=False)
    deadline_type = ChoiceField(choices=(('Same', _('Same')), ('Following', _('Following'))), widget=forms.Select,
                                required=False)
    reminders_enabled = ChoiceField(choices=((False, _('No')), (True, _('Yes'))),
                                    label=_("Do you want to remind DataSenders to send in their data?"), required=False,
                                    initial=False, widget=forms.RadioSelect)
