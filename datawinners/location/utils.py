import os, glob
from django.contrib.gis.utils.layermapping import LayerMapping, LayerMapError
from datawinners.location.models import LocationLevel, location_level_mapping, madagascar_wgs84_mapping


def load_from_gdam_shp_file(file_name, verbose):
    ind_shp = os.path.abspath(os.path.join(os.path.dirname(__file__) + "/../", file_name))
    lm = LayerMapping(LocationLevel, ind_shp, location_level_mapping, transform=False, encoding='iso-8859-1')
    lm.save(strict=True, verbose=verbose)


def load_from_madagascar_ocha_wgs84_shp_file(root_directory, verbose=True):
    for root, dirs, files in os.walk(root_directory):
        files = glob.glob(root + '/*.shp')
        for file in files:
            try:
                lm = LayerMapping(LocationLevel, file, madagascar_wgs84_mapping, transform=True, encoding='iso-8859-1')
                lm.save(strict=True, verbose=verbose)
            except LayerMapError:
                continue
    print "Imported Shapefiles."
    print "Updating database with country name as Madagascar"
    LocationLevel.objects.update(name_0="Madagascar")
    print "Done"


def map_location_groups_to_categories(input, country):
    level_mapping = location_level_mapping.get(country.lower()) or {}
    categories = []
    for level, location in input.items():
        for loc in location:
            categories.append({'category': (level_mapping.get(level.lower()) or ""), 'label': loc.decode()})
    return categories