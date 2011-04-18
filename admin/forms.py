# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.forms.fields import CharField
from django.forms.forms import Form

class EntityType(Form):
    error_css_class = 'error'
    required_css_class = 'required'

    entity_type = CharField(required = True)

    