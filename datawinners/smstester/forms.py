# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.forms.forms import Form
from django import forms
from django.forms.widgets import Textarea


class SMSTesterForm(Form):
    error_css_class = 'error'
    required_css_class = 'required'

    message = forms.CharField(required=True, label="SMS *", widget=Textarea({"cols": 30, "rows": 4}))
    to_number = forms.CharField(required=True, label="To *", initial="919880734937")
    from_number = forms.CharField(required=True, label="From *", initial="1234567890")
    response = forms.CharField(label="Response", max_length=140, widget=Textarea(), required=False)

    def clean_message(self):
        message = self.cleaned_data.get('message')
        self.cleaned_data['message'] = message.strip()
        return self.cleaned_data['message']
