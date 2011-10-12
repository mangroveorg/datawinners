# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from _collections import defaultdict
from threading import Lock
from django.contrib.gis.geos.point import Point
from django.db import connection
from networkx import *
import psycopg2
from datawinners.location.models import LocationLevel


ROOT = "root"
FILTER_LIMIT = 10

def get_location_groups_for_country(country, start_with):
    cursor = connection.cursor()
    search_string = start_with.lower().encode('utf-8')

    data_dict = {}
    data_dict['like'] = search_string + '%'
    sql = """
    (select distinct 'LEVEL4' as LEVEL, name_4||','||name_3||','||name_2||','||name_1 as NAME
  from location_locationlevel l
where name_4  ILIKE CAST(%(like)s as TEXT) limit 10)
                 union
(select distinct 'LEVEL3' as LEVEL,  name_3||','||name_2||','||name_1 as NAME
  from location_locationlevel l
where name_3  ILIKE CAST(%(like)s as TEXT) limit 10)
                union
(select distinct 'LEVEL2' as LEVEL,  name_2||','||name_1 as NAME
  from location_locationlevel l
where name_2  ILIKE CAST(%(like)s as TEXT) limit 5)
  union
(select distinct 'LEVEL1' as LEVEL,  name_1 as NAME
  from location_locationlevel l
where name_1  ILIKE CAST(%(like)s as TEXT) limit 5)
order by LEVEL
    """

    cursor.execute(sql, data_dict)
    rows = cursor.fetchall()
    location_dict = defaultdict(list)
    for level, location in rows:
        location_dict[level].append(location)
    return location_dict

_tree = None
_tree_lock = Lock()


def get_location_tree():
    global _tree
    with _tree_lock:
        if _tree is None:
            _tree = LocationTree()
    return _tree


class LocationTree(object):
    def __init__(self):
        self.tree = DiGraph()
        self.loadfromdb()

    def loadfromdb(self):
        rows = LocationLevel.objects.values('name_0', 'name_1', 'name_2', 'name_3', 'name_4')
        for row in rows:
            path_list = ['root']
            i = 0
            while 1:
                field = "name_%s" % (i,)
                try:
                    value = row[field]
                except KeyError as e:
                    break
                i += 1
                path_list.append(value.lower())
            self.tree.add_path(path_list)

    def get_hierarchy_path(self, location_name):
        try:
            return nx.shortest_path(self.tree, ROOT, location_name.lower())[1:]
        except NetworkXError:
            return [location_name]

    def _exists(self, location):
        return location.lower() in self.tree.nodes()

    def get_location_hierarchy_for_geocode(self, lat, long):
        row = self._get_location_level_row_for_geo_code(lat, long)
        lowest_level = self._get_lowest_level(row)
        location = []
        for i in range(0, lowest_level + 1):
            field = "name_%s" % i
            location.append(getattr(row, field).lower())
        return location

    def _get_lowest_level(self, row):
        i = 0
        while 1:
            try:
                value = getattr(row, "name_%s" % (i,))
                i += 1
            except AttributeError as e:
                break
        return i - 1

    def get_centroid(self, location, level):
        column = 'name_%s' % level
        exactly_matches = column + '__iexact'
        row = LocationLevel.objects.filter(**{exactly_matches: location}).centroid(model_att='c')
        if not row:
            return None
        point = row[0].c
        return point.x, point.y

    def _get_location_level_row_for_geo_code(self, lat, long):
        point = Point(long, lat)
        rows = list(LocationLevel.objects.filter(geom__contains=point))
        if not len(rows):
            return None
        return rows[0]



  