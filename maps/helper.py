# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import json


def create_location_geojson(entity_list):
    location_list = [{"type": "Feature", "geometry": entity.geometry} for entity in entity_list]
    location_geojson = {"type": "FeatureCollection", "features": location_list}
    return json.dumps(location_geojson)
