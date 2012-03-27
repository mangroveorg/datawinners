# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext as _
from countrytotrialnumbermapping.models import Network
import re

def get_countries_in_display_format(countries):
    return [(country.country_name, _get_formatted_country_name(country)) for country in countries]


def _get_formatted_country_name(country):
    return _(country.country_name) + ' (' + country.country_code + ')'


def get_trial_numbers():
    networks = Network.objects.values_list('trial_sms_number', flat=True).distinct()
    return [network for network in networks if network != 'None']

