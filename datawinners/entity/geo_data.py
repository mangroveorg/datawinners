import json
from collections import OrderedDict

from coverage.html import escape

from mangrove.datastore.entity import get_all_entities
from mangrove.errors.MangroveException import DataObjectNotFound
from mangrove.form_model.field import UniqueIdUIField, field_attributes


def geo_jsons(manager, entity_type, filters, details, specials):
    entity_fields = manager.view.registration_form_model_by_entity_type(key=[entity_type], include_docs=True)[0]["doc"]["json_fields"]

    geo_jsons = [{
        "name": entity_type.capitalize(),
        "data": _geo_json(manager, entity_type, entity_fields, dict(filters), details),
        "color": "rgb(104, 174, 59)"
    }]

    for special in specials:
        field = [field for field in entity_fields if field['code'] == special][0]
        group = {"group": field['label'], "data": []}
        total_number = 0
        for choice in specials[special]:
            filters_with_special = dict(filters)
            filters_with_special.update({special: choice['value']})
            is_geojson_for_special_required = True
            if special in filters.keys() and choice['value'] not in dict(filters).get(special):
                is_geojson_for_special_required = False
            matched_choices = [c['text'] for c in field['choices'] if c['val'] == choice['value']]
            if matched_choices:
                data = _geo_json(manager, entity_type, entity_fields, filters_with_special,
                                 details) if is_geojson_for_special_required else {'features': [],
                                                                                'type': 'FeatureCollection'}
                group["data"].append({
                    "name": matched_choices[0] + " (" + str(len(data['features'])) + ")",
                    "data": data,
                    "color": choice['color']

                })
                total_number += len(data['features'])
        group["group"] += " Total " + str(total_number)
        geo_jsons.append(group)

    return json.dumps(geo_jsons)


def get_first_geocode_field_for_entity_type(entity_all_fields):
    geocode_fields = [f for f in
                      entity_all_fields if
                      f["type"] == "geocode"]
    return geocode_fields[0] if len(geocode_fields) > 0 else None


def get_location_list_for_entities(first_geocode_field, unique_ids):
    location_list = []
    for entity in unique_ids:
        value_dict = entity.data.get(first_geocode_field["name"])
        if value_dict and value_dict.has_key('value'):
            value = value_dict["value"]
            location_list.append(_to_json_point(value))
    return location_list


def get_location_list_for_datasenders(datasenders):
    location_list = []
    for entity in datasenders:
        geocode = entity.geometry
        if geocode:
            value = (geocode["coordinates"][0], geocode["coordinates"][1])
            location_list.append(_to_json_point(value))
    return location_list


def _geo_json(dbm, entity_type, entity_fields, filters, details):
    location_list = []

    try:
        forward_filters, reverse_filters = _transform_filters(filters, entity_fields)
        first_geocode_field = get_first_geocode_field_for_entity_type(entity_fields)
        if first_geocode_field:
            unique_ids = get_all_entities(
                dbm, [entity_type], 1000, forward_filters, reverse_filters
            )
            details.extend(['q2'])
            fields_to_show = filter(lambda field: field['code'] in details, entity_fields)
            location_list.extend(_get_detail_list_for_entities(
                _get_field_labels(fields_to_show),
                first_geocode_field,
                unique_ids
            ))

    except DataObjectNotFound:
        pass

    return {"type": "FeatureCollection", "features": location_list}


def _transform_filters(filters, entity_all_fields):
    d = dict((field['code'], field) for field in entity_all_fields)
    forward_filters = {}
    reverse_filters = {}
    for f in filters:
        if len(f.split(",")) > 1 or d[f]["type"] == field_attributes.UNIQUE_ID_FIELD or d[f]["type"] == field_attributes.TEXT_FIELD:
            if "" not in filters[f]:
                if len(f.split(",")) > 1:
                    reverse_filters[filters[f][0]] = [d[qn]['name'] for qn in f.split(",")]
                else:
                    forward_filters[d[f]['name']] = filters[f][0]
        
        else:
            forward_filters[d[f]['name']] = \
                [choice['text'] for choice in d[f]['choices'] if choice['val'] in filters[f]]
    return forward_filters, reverse_filters


def _get_entity_options(dbm, entity_type):
    return [(entity.short_code, escape(entity.data['name']['value'])) for entity in get_all_entities(dbm, [entity_type])]


def _get_field_labels(entity_fields):
    dict_simplified = OrderedDict()
    for field in entity_fields :
        dict_simplified[field['name']] = field['label']
    return dict_simplified


def _get_detail_list_for_entities(entity_field_labels, first_geocode_field, unique_ids):
    detail_list = []
    for entity in unique_ids:
        value_dict = entity.data.get(first_geocode_field["name"])
        if value_dict and value_dict.has_key('value'):
            value = value_dict["value"]
            detail_list.append(_to_json_detail(value, entity_field_labels, entity.data, entity.type_string))
    return detail_list


def _to_json_detail(value, entity_field_labels, data=None, entity_type=None):
    detail_json = _to_json_point(value)
    detail_json['properties'] = _simplify_field_data(data, entity_field_labels, entity_type)
    return detail_json


def _to_json_point(value):
    point_json = { "type": "Feature", "geometry":
        {
            "type": "Point",
            "coordinates": [
                value[1],
                value[0]
            ]
        }
    }
    return point_json


def _simplify_field_data(data, entity_field_labels, entity_type=None):
    simple_data = OrderedDict()

    if entity_type is not None:
        simple_data['entity_type'] = {}
        simple_data['entity_type']["value"] = entity_type
        simple_data['entity_type']["label"] = ""

    entity_details = [(key, data.get(key)) for key in entity_field_labels if key in data.keys()]

    for key, value_field in entity_details:
        one_field_data = {}
        one_field_data["value"]= value_field["value"]

        if key != "entity_type":
            if key == "mobile_number" and entity_type is None:
                one_field_data["label"]= entity_field_labels["telephone_number"]
            else:
                one_field_data["label"]= entity_field_labels[key]
        else:
            one_field_data["label"] = ""

        simple_data[key] = one_field_data

    return simple_data
