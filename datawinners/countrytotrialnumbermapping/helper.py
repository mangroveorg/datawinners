# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

def get_countries_in_display_format(countries):
    return {country.country_name:_get_formatted_country_name(country) for country in countries}

def _get_formatted_country_name(country):
    return country.country_name + ' (' + country.country_code + ')'
