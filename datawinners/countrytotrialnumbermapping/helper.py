# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from datawinners.countrytotrialnumbermapping.models import Network

def get_countries_in_display_format(countries, language="en"):
    return [(country.country_name_en, _get_formatted_country_name(country, language)) for country in countries]


def _get_formatted_country_name(country, language):
    field = "country_name_"+language
    return getattr(country, field) + ' (' + country.country_code + ')'


def get_trial_numbers():
    trial_numbers = Network.objects.values_list('trial_sms_number', flat=True).distinct()
    return [trial_number.replace("+","") for trial_number in trial_numbers if trial_number != 'None']

