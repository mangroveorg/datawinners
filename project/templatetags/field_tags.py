# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='field_type')
def field_type(value):
    return value.field.__class__.__name__

@register.filter(name='field_label')
def field_label(value):
    label = unicode(value.label)
    required = value.field.required

    if required:
        return mark_safe("<label>%s</label>" % label)
    else:
        return mark_safe("<label>%s<span class='optional_field'> Optional</span></label>" % label)

@register.filter(name='widget_type')
def widget_type(value):
    return value.field.widget.__class__.__name__