# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.contrib.gis.geos.point import Point
from networkx import *
from datawinners.location.models import LocationLevel

ROOT = "root"

class LocationTree(object):
    def __init__(self):
        self.tree=DiGraph()
        self.countries=[]
        self.loadfromdb()

    def loadfromdb(self):
        rows = LocationLevel.objects.all()
        geo_countries = LocationLevel.objects.values('name_0').distinct()
        self.countries= [geo_country['name_0'] for geo_country in geo_countries]
        for row in rows:
            path_list = ['root']
            i = 0
            while(1):
                field = "name_%s" % (i,)
                try:
                    value = getattr(row,field)
                except AttributeError as e:
                    break;
                i += 1
                path_list.append(value)
            self.tree.add_path(path_list)

    def nodes(self):
        return self.tree.nodes()

    def get_next_level(self, parent):
        return self.tree.neighbors(parent)

    def get_hierarchy_path(self, location_name):
        return nx.shortest_path(self.tree, ROOT,location_name)[1:]

    def exists(self, location):
        return location in self.tree.nodes()

    def get_location_for_geocode(self, lat, long):
        point = Point(long, lat)
        row = LocationLevel.objects.filter(geom__contains=point)[0]
        field = "name_%s" % (self._get_lowest_level(row))
        return getattr(row,field)

    def _get_lowest_level(self, row):
        i = 0
        while(1):
            try:
                value = getattr(row, "name_%s" % (i,))
                i += 1
            except AttributeError as e:
                break;
        return i - 1

  