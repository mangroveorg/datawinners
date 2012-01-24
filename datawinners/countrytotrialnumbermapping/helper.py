# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.utils.datastructures import SortedDict

def get_countries_in_display_format(countries):
    country_dict = SortedDict()
    for country in countries:
        country_dict[country.country_name] = _get_formatted_country_name(country)
    return country_dict

def _get_formatted_country_name(country):
    return country.country_name + ' (' + country.country_code + ')'
