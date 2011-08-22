from django.contrib.gis.db import models


class LocationLevel(models.Model):
    name_0 = models.CharField(max_length=75, null=True, blank=True)
    name_1 = models.CharField(max_length=75, null=True, blank=True)
    name_2 = models.CharField(max_length=75, null=True, blank=True)
    name_3 = models.CharField(max_length=75, null=True, blank=True)
    name_4 = models.CharField(max_length=100, null=True, blank=True)
    geom = models.MultiPolygonField(srid=4326)
    objects = models.GeoManager()


location_level_mapping = {
    'name_0': 'NAME_0',
    'name_1': 'NAME_1',
    'name_2': 'NAME_2',
    'name_3': 'NAME_3',
    'name_4': 'NAME_4',
    'geom': 'MULTIPOLYGON',
    }


# Auto-generated `LayerMapping` dictionary for WorldBorders model
madagascar_wgs84_mapping = {
    'name_1': 'LIB_REG',
    'name_2': 'LIB_DIST',
    'name_3': 'LIB_COM',
    'name_4': 'LIB_FKT',
    'geom': 'MULTIPOLYGON',
    }

location_level_mapping = {
    "madagascar": {"level1": "Region",
                   "level2": "District",
                   "level3": "Commune",
                   "level4": "Fokontany"
    }
}

