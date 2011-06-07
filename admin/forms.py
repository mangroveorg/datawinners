# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.forms.fields import CharField, RegexField
from django.forms.forms import Form


class EntityTypeForm(Form):
    error_css_class = 'error'
    required_css_class = 'required'

    entity_type = RegexField(regex="^[A-Za-z0-9,]+$", max_length=20, error_message="Only letters and numbers(with comma seperators)are valid", required=True, label="New Subject(eg clinic, waterpoint etc)")
