# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from mangrove.form_model.form_model import NAME_FIELD, MOBILE_NUMBER_FIELD, LOCATION_TYPE_FIELD_NAME


class ReporterEntity(object):
    def __init__(self, entity):
        self.entity = entity

    @property
    def mobile_number(self):
        return self.entity.value(MOBILE_NUMBER_FIELD)

    @property
    def location(self):
        return ','.join(self.entity.value(LOCATION_TYPE_FIELD_NAME))

    @property
    def geo_code(self):
        return ','.join(map(str, self.entity.geometry.get('coordinates', '')))


    @property
    def name(self):
        return self.entity.value(NAME_FIELD)
