from datawinners.location.LocationTree import LocationTree
from mangrove.utils.types import is_empty

def _get_location_heirarchy_from_location_name(display_location):
    if is_empty(display_location):
        return None
    lowest_level_location, high_level_location = tuple(display_location.split(','))
    tree = LocationTree()
    location_hierarchy = tree.get_hierarchy_path(lowest_level_location)
    return location_hierarchy


def _get_location_hierarchy(display_location,geo_code):
    location_hierarchy = _get_location_heirarchy_from_location_name(display_location)
    if location_hierarchy is None and geo_code is not None:
        lat_string,long_string=tuple(geo_code.split())
        tree=LocationTree()
        location_hierarchy=tree.get_location_hierarchy_for_geocode(lat=float(lat_string),long=float(long_string))
    return location_hierarchy



def create_registration_submission(message_data):
    #TODO need to refactor this code. The master dictionary should be maintained by the registration form  model
    mapper = {'telephone_number': 'M', 'geo_code': 'G', 'Name': 'N', 'location': 'L'}
    data = dict()
    telephone_number = message_data.get('telephone_number')
    geo_code = message_data.get('geo_code')
    display_location=message_data.get('location')
    location_hierarchy = _get_location_hierarchy(display_location,geo_code)

    if telephone_number is not None:
        data[mapper['telephone_number']] = _get_telephone_number(telephone_number)
    if geo_code is not None:
        data[mapper['geo_code']] = geo_code
    if location_hierarchy is  not None:
    #TODO change this when we decide how we will process location
        data[mapper['location']] = location_hierarchy

    data[mapper['Name']] = message_data.get('first_name')
    data['form_code'] = REGISTRATION_FORM_CODE
    data['T'] = 'Reporter'
    return data

def submit_registration(message_data):
    web_player = WebPlayer(dbm,SubmissionHandler(dbm))
    return web_player.accept(Request(transport='web', message=message_data, source='web', destination='mangrove'))
