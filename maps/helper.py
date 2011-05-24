# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8


def create_location_list(entity_list):
    location_list=[{"short_code": entity.short_code, "type":entity.geometry.get("type"), "latitude":entity.geometry.get("coordinates")[0], "longitude":entity.geometry.get("coordinates")[1]} for entity in entity_list]
    return location_list