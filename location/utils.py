from django.contrib.gis.utils.layermapping import LayerMapping
import os
from datawinners.location.models import LocationLevel, location_level_mapping

def load_from_shp_file(file_name,verbose):
    ind_shp = os.path.abspath(os.path.join(os.path.dirname(__file__) + "/../", file_name))
    lm = LayerMapping(LocationLevel, ind_shp, location_level_mapping, transform=False, encoding='iso-8859-1')
    lm.save(strict=True,verbose=verbose)
