from django.contrib.gis.db import models


class LocationLevel(models.Model):
    id_0 = models.IntegerField()
    iso = models.CharField(max_length=3)
    name_0 = models.CharField(max_length=75)
    id_1 = models.IntegerField()
    name_1 = models.CharField(max_length=75)
    id_2 = models.IntegerField()
    name_2 = models.CharField(max_length=75)
    id_3 = models.IntegerField()
    name_3 = models.CharField(max_length=75)
    id_4 = models.IntegerField()
    name_4 = models.CharField(max_length=100)
    varname_4 = models.CharField(max_length=100)
    type_4 = models.CharField(max_length=25)
    engtype_4 = models.CharField(max_length=25)
    validfr_4 = models.CharField(max_length=25)
    validto_4 = models.CharField(max_length=25)
    remarks_4 = models.CharField(max_length=50)
    shape_leng = models.FloatField()
    shape_area = models.FloatField()
    geom = models.MultiPolygonField(srid=4326)
    objects = models.GeoManager()


# Auto-generated `LayerMapping` dictionary for MDG4Borders model
location_level_mapping = {
    'id_0' : 'ID_0',
    'iso' : 'ISO',
    'name_0' : 'NAME_0',
    'id_1' : 'ID_1',
    'name_1' : 'NAME_1',
    'id_2' : 'ID_2',
    'name_2' : 'NAME_2',
    'id_3' : 'ID_3',
    'name_3' : 'NAME_3',
    'id_4' : 'ID_4',
    'name_4' : 'NAME_4',
    'varname_4' : 'VARNAME_4',
    'type_4' : 'TYPE_4',
    'engtype_4' : 'ENGTYPE_4',
    'validfr_4' : 'VALIDFR_4',
    'validto_4' : 'VALIDTO_4',
    'remarks_4' : 'REMARKS_4',
    'shape_leng' : 'Shape_Leng',
    'shape_area' : 'Shape_Area',
    'geom' : 'MULTIPOLYGON',
}
