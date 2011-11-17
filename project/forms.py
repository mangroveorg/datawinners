# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import calendar
from django.db.models.fields import TextField
from django.forms import DecimalField

from django.forms.fields import CharField, ChoiceField, MultipleChoiceField, BooleanField
from django.core.exceptions import ValidationError
from django.forms.forms import Form
from django.utils.translation import ugettext_lazy as _, ugettext_lazy
from django.forms.widgets import RadioFieldRenderer, RadioInput
from django import forms
from datawinners.utils import convert_to_ordinal
from mangrove.form_model.form_model import REPORTER

class BroadcastMessageForm(forms.Form):

    text = CharField(label=ugettext_lazy("Text:"), required=True, max_length=160, widget=forms.Textarea)
    to = ChoiceField(label=ugettext_lazy("To:"),choices=(("All", ugettext_lazy("All Data Senders")),
                                                         ("Associated", ugettext_lazy("Data Senders associated to my project")),
                                                         ("Additional", ugettext_lazy("Other People"))),initial=("All"))
    others = CharField(label=ugettext_lazy("Other People:"), max_length=160, widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super(BroadcastMessageForm, self).__init__(*args, **kwargs)
        self.fields['text'].widget.attrs['watermark'] = ugettext_lazy('Enter your SMS text')
        self.fields['text'].widget.attrs['id'] = 'sms_content'
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

class CreateProject(Form):

    QUESTIONNAIRE_CHOICES = (('yes', _("This is general activity report.")),
                             ('no', _("I am collecting data about a specific subject.")))
    CATEGORY_CHOICE = (('A person', _('A person')), ('A place', _('A place')),
                       ('A thing', _('A thing')), ('An event', _('An event')), )
    SUBJECT_CHOICE = (('Patient', _('Patient')), ('Farmer', _('Farmer')),
                      ('Child', _('Child')), ('Employee', _('Employee')), )
    LANGUAGES = (('en', 'English'), ('fr', 'Français'),('mg', 'Malagasy'))

    DEVICE_CHOICES = (('sms', 'SMS'), ('web', 'WEB'))

    name = CharField(required=True, label=_("Name"))
    goals = CharField(max_length=300, widget=forms.Textarea, label=_('Description'), required=False)
    activity_report = ChoiceField(label=_("What is this questionnaire about?"),
                                  choices=QUESTIONNAIRE_CHOICES,
                                  widget=forms.RadioSelect, required=False, initial='yes')
    language = ChoiceField(label=_("Choose your language for success and error messages to Data Senders"),
                           widget=forms.RadioSelect,
                           choices=LANGUAGES, initial='en')
    devices = MultipleChoiceField(label=_('Device'), widget=forms.CheckboxSelectMultiple, choices=DEVICE_CHOICES,
                                  initial=['sms', 'web'], required=False)
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
    FREQUENCY_CHOICES = ((False, _("No deadline. Senders can submit data any time.")), (True, _("Every")))
    has_deadline = ChoiceField(label=_("Time Period"),
                                    choices=FREQUENCY_CHOICES, widget=forms.RadioSelect, initial=False)
    frequency_period = ChoiceField(choices=(('week', _('Week')), ('month', _('Month'))), widget=forms.Select,
                                   required=False, )
    deadline_month = ChoiceField(
        choices=(tuple([(n, convert_to_ordinal(n)) for n in range(1, 31)] + [(31, 'Last Day')])), widget=forms.Select,
        required=False)
    deadline_week = ChoiceField(choices=(get_translated_weekdays()), widget=forms.Select(attrs={'data-bind': 'random'}),
                                required=False)
    deadline_type = ChoiceField(choices=(('Same', _('Same')), ('Following', _('Following'))), widget=forms.Select,
                                required=False)

    should_send_reminders_before_deadline = BooleanField(required=False, initial=False)
    number_of_days_before_deadline = DecimalField(label="days before deadline", required=False)
    reminder_text_before_deadline = CharField(widget=forms.Textarea, required=False)

    should_send_reminders_on_deadline = BooleanField(label="The day of the deadline", required=False, initial=False)
    reminder_text_on_deadline = CharField(widget=forms.Textarea, required=False)

    should_send_reminders_after_deadline = BooleanField(label="days after the deadline", required=False, initial=False)
    number_of_days_after_deadline = DecimalField(required=False)
    reminder_text_after_deadline = CharField(widget=forms.Textarea, required=False)

    whom_to_send_message = BooleanField(label="Only send reminders to senders who have not already submitted data for the current deadline",
                                       required=False, initial=True)
