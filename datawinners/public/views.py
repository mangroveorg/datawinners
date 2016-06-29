import json

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from datawinners.main.database import get_database_manager, get_db_manager
from mangrove.datastore.entity import get_all_entities
from mangrove.datastore.entity_share import get_entity_preference_by_share_token, get_entity_preference
from mangrove.errors.MangroveException import DataObjectNotFound


def geo_json_for_entity(request, entity_type):
    dbm = get_database_manager(request.user)
    location_list = []

    try:
        entity_all_fields = dbm.view.registration_form_model_by_entity_type(key=[entity_type], include_docs=True)[0]["doc"]["json_fields"]
        entity_all_field_labels = _get_all_field_labels(entity_all_fields)
        first_geocode_field = _get_first_geocode_field_for_entity_type(entity_all_fields)
        if first_geocode_field:
            unique_ids = get_all_entities(dbm, [entity_type], limit=1000)
            location_list.extend(get_location_list_for_entities(entity_all_field_labels,first_geocode_field, unique_ids))

    except DataObjectNotFound:
        pass

    location_geojson = {"type": "FeatureCollection", "features": location_list}
    return HttpResponse(json.dumps(location_geojson))


def render_map(request, share_token):
    entity_preference = get_entity_preference_by_share_token(get_db_manager("public"), share_token)
    return render_to_response('map.html',
                              {'entity_type': entity_preference.entity_type},
                              context_instance=RequestContext(request))


def _get_all_field_labels(entity_all_fields):
    dict_simplified = {}
    for field in entity_all_fields :
        dict_simplified[field['name']] = field['label']
    return dict_simplified


def _get_first_geocode_field_for_entity_type(entity_all_fields):
    geocode_fields = [f for f in
                      entity_all_fields if
                      f["type"] == "geocode"]
    return geocode_fields[0] if len(geocode_fields) > 0 else None


def get_location_list_for_entities(entity_all_field_labels, first_geocode_field, unique_ids):
    location_list = []
    for entity in unique_ids:
        value_dict = entity.data.get(first_geocode_field["name"])
        if value_dict and value_dict.has_key('value'):
            value = value_dict["value"]
            location_list.append(to_json_point(value,entity.data, entity_all_field_labels, entity.type_string))
    return location_list


def get_location_list_for_datasenders(entity_all_fields=None,datasenders=None):
    location_list = []
    for entity in datasenders:
        geocode = entity.geometry
        if geocode:
            value = (geocode["coordinates"][0], geocode["coordinates"][1])
            location_list.append(to_json_point(value,entity.data,entity_all_fields))
    return location_list


def to_json_point(value,data=None,entity_all_field_labels=None,entity_type=None):
    point_json = {"type": "Feature", "geometry":
        {
            "type": "Point",
            "coordinates": [
                value[1],
                value[0]
            ]
        },
        "properties": simplify_field_data(data, entity_all_field_labels, entity_type)
    }
    return point_json


def simplify_field_data(data,entity_all_field_labels=None, entity_type=None):
    simple_data = {}

    if entity_type is not None:
        simple_data['entity_type'] = {}
        simple_data['entity_type']["value"] = entity_type
        simple_data['entity_type']["label"] = ""

    for key,value_field in data.items():
        one_field_data = {}
        one_field_data["value"]= value_field["value"]

        if key != "entity_type":
            if key == "mobile_number" and entity_type is None:
                one_field_data["label"]= entity_all_field_labels["telephone_number"]
            else:
                one_field_data["label"]= entity_all_field_labels[key]
        else:
            one_field_data["label"] = ""

        simple_data[key] = one_field_data
    return simple_data
