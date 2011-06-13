# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django import forms

class SubjectUploadForm(forms.Form):
    error_css_class = 'error'
    required_css_class = 'required'

    file = forms.FileField(label='Import Subjects')

