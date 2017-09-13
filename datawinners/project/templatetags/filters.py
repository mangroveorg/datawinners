from django.template.defaulttags import register
from django.utils.translation import ugettext


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def list_to_comma_separated_string(l):
    try:
        return ', '.join(l)
    except:
        return None


@register.filter
def join_by_attr(the_list, attr_name='name', separator=', '):
    a_list = list()
    for item in the_list:
        a_list.append(item[str(attr_name)])
    return separator.join(a_list)


@register.filter
def friendly_name(name):
    role_map = {'NGO Admins': 'Account Administrator', 'Project Managers': 'Project Manager',
                'Extended Users': 'Administrator', 'No Delete PM': 'Project Manager (without delete permission)'};
    if role_map[name] is not None:
        return ugettext(role_map[name])
    return name


@register.filter
def has_higher_privileges_than(current_user, user):
    return current_user.has_higher_privileges_than(user)
