# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import json


def create_location_geojson(entity_list):
    location_list=[]
    for entity in entity_list:
        geometry = entity.geometry
        if geometry:
            geometry["coordinates"] = [geometry["coordinates"][1], geometry["coordinates"][0]]
            location_list.append({"type": "Feature", "geometry": entity.geometry})
    location_geojson = {"type": "FeatureCollection", "features": location_list}
    return json.dumps(location_geojson)
