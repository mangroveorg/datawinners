# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

register = template.Library()

@register.filter(name='is_datasender')
def is_datasender(user):
    groups = user.groups.all()
    return len(groups) == 1 and groups[0].name == "Data Senders"

@register.filter
def in_group(user, group):
	"""Returns True/False if the user is in the given group(s).
	Usage::
		{% if user|in_group:"Friends" %}
		or
		{% if user|in_group:"Friends,Enemies" %}
		...
		{% endif %}
	You can specify a single group or comma-delimited list.
	"""
	import re
	if re.search(',', group): group_list = group.split(',')
	elif re.search(' ', group): group_list = group.split()
	else: group_list = [group]
	user_groups = []
	for group in user.groups.all(): user_groups.append(str(group.name))
	if filter(lambda x:x in user_groups, group_list): return True
	else: return False
in_group.is_safe = True