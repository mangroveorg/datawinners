import os, glob
from django.contrib.gis.utils.layermapping import LayerMapping, LayerMapError
from datawinners.location.models import LocationLevel, location_level_mapping, madborder_mapping

def load_from_gdam_shp_file(file_name,verbose):
    ind_shp = os.path.abspath(os.path.join(os.path.dirname(__file__) + "/../", file_name))
    lm = LayerMapping(LocationLevel, ind_shp, location_level_mapping, transform=False, encoding='iso-8859-1')
    lm.save(strict=True,verbose=verbose)
    
def load_from_ocha_shp_file(root_directory,verbose):
    for root, dirs, files in os.walk(root_directory):
        files = glob.glob(root + '/lim_com*.shp')
        for file in files:
            try:
                lm = LayerMapping(LocationLevel, file, madborder_mapping, transform=True, encoding='iso-8859-1')
                lm.save(strict=True,verbose=verbose)
            except LayerMapError:
                continue

    location_level = LocationLevel.objects.all()
    for location in location_level:
        location.name_0 = "Madagascar"
        location.save()

def load_from_wgs_shp_file(root_directory,verbose):
    for root, dirs, files in os.walk(root_directory):
        files = glob.glob(root + '/lim_com*.shp')
        for file in files:
            try:
                lm = LayerMapping(LocationLevel, file, madborder_mapping, transform=True, encoding='iso-8859-1')
                lm.save(strict=True,verbose=verbose)
            except LayerMapError:
                continue
    location_level = LocationLevel.objects.all()
    for location in location_level:

