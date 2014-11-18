import json
import os
from datetime import timedelta
import xmltodict

COUNTRY_TIME_DELTA_LIST = None


def _get_country_time_delta_list():
    global COUNTRY_TIME_DELTA_LIST
    if COUNTRY_TIME_DELTA_LIST:
        return COUNTRY_TIME_DELTA_LIST['countries']
    current_directory = os.path.dirname(os.path.abspath(__file__))
    with open("%s/country_timezone.xml" % current_directory, "r") as json_file:
        data = json_file.read().replace('\n', '')
        COUNTRY_TIME_DELTA_LIST = xmltodict.parse(data)
    return COUNTRY_TIME_DELTA_LIST['countries']


def _parse_time_delta(time_delta_string):
    hours_with_sign = time_delta_string.split(":")[0]
    minutes = time_delta_string.split(":")[1]
    return hours_with_sign[0], int(hours_with_sign[1:]), int(minutes)


def get_country_time_delta(country_code):
    country_time_delta_list = _get_country_time_delta_list()
    if country_time_delta_list.get(country_code):
        return _parse_time_delta(country_time_delta_list[country_code])
    return '+', 0, 0


def convert_utc_to_localized(time_delta_tuple, datetime):
    sign = -1 if time_delta_tuple[0] == '-' else 1
    return datetime + timedelta(minutes=sign * (time_delta_tuple[1] * 60 + time_delta_tuple[2]))
