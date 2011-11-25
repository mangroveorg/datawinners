# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

register = template.Library()

@register.filter(name='is_datasender')
def is_datasender(user):
    return True if user.get_profile().reporter_id is not None else False
