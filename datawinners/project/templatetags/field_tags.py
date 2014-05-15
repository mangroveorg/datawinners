# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django import template
from django.utils import translation
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

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
        return mark_safe("<label>%s<span class='optional_field'> %s</span></label>" % (label,_("Optional")))

@register.filter(name='widget_type')
def widget_type(value):
    return value.field.widget.__class__.__name__

@register.filter
def active_language(text):
    display_lang = {'en': {'English':"<b>English</b>",
                            'Fran&ccedil;ais':"Fran&ccedil;ais"},
                   'fr': {'English':"English",
                            'Fran&ccedil;ais':'<b>Fran&ccedil;ais</b>'}}
    return mark_safe(display_lang[translation.get_language()][text])
