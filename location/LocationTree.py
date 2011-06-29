# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.contrib.gis.geos.point import Point
from networkx import *
from datawinners.location.models import LocationLevel

ROOT = "root"
FILTER_LIMIT = 10


def _get_lowest_level(row):
    i = 0
    while(1):
        try:
            value = getattr(row, "name_%s" % (i,))
            i += 1
        except AttributeError as e:
            break;
    return i - 1


def _get_lowest_level_field_name(country):
    country_row = LocationLevel.objects.filter(name_0=country)[:1]
    level = _get_lowest_level(country_row[0])
    lowest_level_field_name = "name_" + str(level)
    return lowest_level_field_name


def _get_places(lowest_level_field_name, place):
    lowest_level_place = getattr(place, lowest_level_field_name)
    level_1_place = getattr(place, "name_1")
    return level_1_place, lowest_level_place


def get_locations_for_country(country, start_with):
    lowest_level_field_name = _get_lowest_level_field_name(country)
    startswith_field = lowest_level_field_name + "__istartswith"
    results = LocationLevel.objects.filter(**{startswith_field:start_with})[:FILTER_LIMIT]
    formatted_results=[]
    for place in results:
        level_1_place, lowest_level_place = _get_places(lowest_level_field_name, place)
        formatted_place="%s, %s" % (lowest_level_place,level_1_place)
        formatted_results.append(formatted_place)
    return formatted_results

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


  