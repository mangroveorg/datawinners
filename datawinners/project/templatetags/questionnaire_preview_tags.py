# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import re

from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import get_language, ugettext as _


register = template.Library()

@register.filter(name='format_organization_number')
def format_organization_number(value):
    lang = re.sub("-.*", "", get_language())
    link = '/' + lang + '/your-account-phone-number/'
    return mark_safe('<a class="org_number_link" href="%s" target="_blank">%s</a>' % (link,_('Your Trial Account Phone Number'))) if isinstance(value, list) else value