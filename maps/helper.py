# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8


def create_location_geojson(entity_list):
    location_list=[{"type":"feature", "geometry":entity.geometry} for entity in entity_list]
    return str(location_list)