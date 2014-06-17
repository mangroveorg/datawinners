# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import json
import random


def _get_lowest_administrative_boundary(location_path):
    lowest_admin_boundary = location_path[len(location_path) - 1] if len(location_path) > 0 else None
    return lowest_admin_boundary, len(location_path) - 1


def _get_geo_json_from_geo_code(geometry):
    geometry["coordinates"] = [geometry["coordinates"][1], geometry["coordinates"][0]]
    geometry_geo_json = {"type": "Feature", "geometry": geometry}
    return geometry_geo_json


def _get_geo_json_from_location(lowest_admin_boundary, level, tree):
    geo_code = tree.get_centroid(lowest_admin_boundary, level)
    if geo_code is None:
        return None
    geo_json_geometry = {"type": "Point", "coordinates": [geo_code[0], geo_code[1]]}
    geojson_feature = {"type": "Feature", "geometry": geo_json_geometry}
    return geojson_feature


def _get_geo_json_from_location_path(location_path, tree):
    lowest_admin_boundary, level = _get_lowest_administrative_boundary(location_path)
    geojson_feature = None
    if lowest_admin_boundary is not None:
        geojson_feature = _get_geo_json_from_location(lowest_admin_boundary, level, tree)
    return geojson_feature


def create_location_geojson(entity_list):
    location_list = []
    for entity in entity_list:
        geometry_geo_json = None
        if entity.geometry:
            try:
                geometry_geo_json = _get_geo_json_from_geo_code(entity.geometry)
            except IndexError:
                geometry_geo_json = None
        if geometry_geo_json is not None:
            location_list.append(geometry_geo_json)

    location_geojson = {"type": "FeatureCollection", "features": location_list}
    return json.dumps(location_geojson)
