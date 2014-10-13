# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import calendar, re
from django.forms import DecimalField

from django.forms.fields import CharField, ChoiceField, BooleanField
from django.forms.forms import Form
from django.utils.translation import ugettext_lazy as _, ugettext_lazy
from django.forms.widgets import RadioFieldRenderer, RadioInput
from django import forms
from datawinners.utils import convert_to_ordinal
from mangrove.form_model.form_model import REPORTER
from django.utils.encoding import force_unicode
from django.utils.html import escape, conditional_escape

class MySelect(forms.Select):
    def render_option(self, selected_choices, option_value, option_label):
        option_value = force_unicode(option_value)
        selected_html = (option_value in selected_choices) and u' selected="selected"' or ''
        options_labels = re.match(r'(.*?)(\d+$)', unicode(option_label))
        number_html = ''
        if options_labels is not None:
            option_label, number = options_labels.groups()
            number_html = ' number="%s"' % number
        return u'<option value="%s"%s%s>%s</option>' % (
            escape(option_value), selected_html, number_html,
            conditional_escape(force_unicode(option_label)))


class BroadcastMessageForm(forms.Form):

    text = CharField(label=ugettext_lazy("Text:"), required=True, max_length=160, widget=forms.Textarea)
    to = ChoiceField(label=ugettext_lazy("To:"),widget=MySelect(), choices=(("All", ugettext_lazy("All Data Senders")),
                                                         ("Associated", ugettext_lazy("Data Senders associated to my project")),
                                                         ("Additional", ugettext_lazy("Other People")),
                                                         ("AllSubmitted", ugettext_lazy("AllSubmitted"))),initial=("Asossciated"))
    others = CharField(label=ugettext_lazy("Other People:"), widget=forms.Textarea, required=False)

    def __init__(self, associated_ds=0, number_of_ds=0, unregistered_ds=0,*args, **kwargs):
        super(BroadcastMessageForm, self).__init__(*args, **kwargs)
        self.fields["to"].widget.choices = (("Associated", u"%s %s" % (ugettext_lazy("My registered Data Senders linked to this Questionnaire"), str(associated_ds))),
                                                        ("All", u"%s %s" % (ugettext_lazy("All registered Data Senders of all Questionnaires"), str(number_of_ds))),
                                                        ("Additional", ugettext_lazy("Other People")))
        self.fields["to"].widget.attrs["class"] = "none"
        self.fields['text'].widget.attrs['watermark'] = ugettext_lazy('Enter your SMS text')
        self.fields['text'].widget.attrs['id'] = 'sms_content'

    def clean_others(self):
        others = self.cleaned_data['others']
        return [number.strip() for number in others.split(',') if number.strip() !='']

class OpenDsBroadcastMessageForm(BroadcastMessageForm):

    def __init__(self, associated_ds=0, number_of_ds=0, unregistered_ds=0, *args, **kwargs):
        super(OpenDsBroadcastMessageForm, self).__init__(*args, **kwargs)
        unregistered_label = u"%s %s" % (ugettext_lazy("All people who submitted data (registered & un-registered)"), str(unregistered_ds))
        self.fields["to"].widget.choices = (("Associated", u"%s %s" % (ugettext_lazy("My registered Data Senders linked to this Questionnaire"), str(associated_ds))),
                                                        ("All", u"%s %s" % (ugettext_lazy("All registered Data Senders of all Questionnaires"), str(number_of_ds))),
                                                        ("AllSubmitted" , unregistered_label),
                                                        ("Additional", ugettext_lazy("Other People")))
        


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


class ReminderForm(Form):
    frequency_period = ChoiceField(choices=(('week', _('Week')), ('month', _('Month'))), widget=forms.Select,
                                   required=False, )
    deadline_month = ChoiceField(
        choices=(tuple([(n, convert_to_ordinal(n)) for n in range(1, 31)] + [(31, ugettext_lazy('Last Day'))])), widget=forms.Select,
        required=False)
    deadline_week = ChoiceField(choices=(get_translated_weekdays()), widget=forms.Select(attrs={'data-bind': 'random'}),
                                required=False)
    deadline_type_week = ChoiceField(choices=(('Same', _('Same week')), ('Following', _('Following week'))), widget=forms.Select(attrs={'class':'deadline_type'}),
                                required=False)

    deadline_type_month = ChoiceField(choices=(('Same', _('Same month')), ('Following', _('Following month'))), widget=forms.Select(attrs={'class':'deadline_type'}),
                                required=False)

    deadline_type = ChoiceField(choices=(('Same', _('Same')), ('Following', _('Following'))), widget=forms.Select,
                                required=False)

    should_send_reminders_before_deadline = BooleanField(required=False, initial=False)
    number_of_days_before_deadline = DecimalField(label=ugettext_lazy("days before deadline"), required=False)
    reminder_text_before_deadline = CharField(label=ugettext_lazy("Reminder text before deadline"),
                                              widget=forms.Textarea, required=False)

    should_send_reminders_on_deadline = BooleanField(label=ugettext_lazy("The day of the deadline"), required=False, initial=False)
    reminder_text_on_deadline = CharField(label=ugettext_lazy("Reminder text on deadline"),widget=forms.Textarea,
                                          required=False)

    should_send_reminders_after_deadline = BooleanField(label=ugettext_lazy("days after the deadline"), required=False, initial=False)
    number_of_days_after_deadline = DecimalField(required=False, label=ugettext_lazy("number of days after deadline"))
    reminder_text_after_deadline = CharField(label=ugettext_lazy("Reminder text after deadline"), widget=forms.Textarea,
                                             required=False)

    whom_to_send_message = BooleanField(label=ugettext_lazy("Only send Reminders to registered Data Senders who have not yet submitted data for the current deadline."),
                                       required=False, initial=True)

    def __init__(self, *args, **kwargs):
        data = kwargs.get("data")
        if data is not None:
            deadline_type = data.get('deadline_type')
            data.update({"deadline_type_week": deadline_type, "deadline_type_month": deadline_type})
            kwargs.update({"data": data})

        super(ReminderForm, self).__init__(*args, **kwargs)
        deadline_month = ChoiceField(
            choices=(tuple([(n, convert_to_ordinal(n)) for n in range(1, 31)] + [(31, ugettext_lazy('Last Day'))])), widget=forms.Select,
            required=False)
        self.fields["deadline_month"] = deadline_month

    def clean(self):

        msg = _("This field is required")

        if self.cleaned_data.get('should_send_reminders_before_deadline'):
            if self.cleaned_data.get('number_of_days_before_deadline') is None:
                self._errors['number_of_days_before_deadline'] = self.error_class([msg])
            if self.cleaned_data.get('reminder_text_before_deadline') == '':
                self.errors['reminder_text_before_deadline'] = self.error_class([msg])

        if self.cleaned_data.get('should_send_reminders_on_deadline') and self.cleaned_data.get('reminder_text_on_deadline') == '':
            self.errors['reminder_text_on_deadline'] = self.error_class([msg])

        if self.cleaned_data.get('should_send_reminders_after_deadline'):
            if self.cleaned_data.get('number_of_days_after_deadline') is None:
                self.errors['number_of_days_after_deadline'] = self.error_class([msg])
            if self.cleaned_data.get('reminder_text_after_deadline') == '':
                self.errors['reminder_text_after_deadline'] = self.error_class([msg])

        return self.cleaned_data

    def disable_all_field(self):
        self.fields['frequency_period'].widget.attrs['disabled'] = 'disabled'
        self.fields['should_send_reminders_before_deadline'].widget.attrs['disabled'] = 'disabled'
        self.fields['number_of_days_before_deadline'].widget.attrs['disabled'] = 'disabled'
        self.fields['reminder_text_before_deadline'].widget.attrs['disabled'] = 'disabled'
        self.fields['should_send_reminders_on_deadline'].widget.attrs['disabled'] = 'disabled'
        self.fields['reminder_text_on_deadline'].widget.attrs['disabled'] = 'disabled'
        self.fields['number_of_days_after_deadline'].widget.attrs['disabled'] = 'disabled'
        self.fields['reminder_text_after_deadline'].widget.attrs['disabled'] = 'disabled'
        self.fields['whom_to_send_message'].widget.attrs['disabled'] = 'disabled'
