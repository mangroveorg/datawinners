from datawinners.location.LocationTree import get_location_tree, get_location_hierarchy

class LocationBridge(object):
    def __init__(self,location_tree=None,get_loc_hierarchy=None):
        self.location_tree = location_tree or get_location_tree()
        self.get_location_hierarchy = get_loc_hierarchy or get_location_hierarchy

    def get_location_hierarchy_for_geocode(self, lat, long):
        return self.location_tree.get_location_hierarchy_for_geocode( lat, long)

    def get_centroid(self, location, level):
        return self.location_tree.get_centroid(location,level)

    def get_location_hierarchy(self,lowest_level):
        self.get_location_hierarchy(lowest_level)

