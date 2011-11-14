# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from _collections import defaultdict
from threading import Lock
from django.contrib.gis.geos.point import Point
from django.db import connection
from datawinners.location.models import LocationLevel

ROOT = "root"
FILTER_LIMIT = 10

def get_location_groups_for_country(country, start_with):
    cursor = connection.cursor()
    search_string = start_with.lower().encode('utf-8')

    data_dict = {'like': search_string + '%'}
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

def get_location_hierarchy(lowest_level):
    """
    The reason why we are using UPPER and not ILIKE -
    Using UPPER() or LOWER() to change the case of the field before comparison;
    this approach can be better than 1) or 2) because these functions may be
    indexed, and thus if you are doing a "begins with" or "exact match" search
    your query may be indexed:
	SELECT * FROM sometable WHERE UPPER(textfield) LIKE (UPPER('value') || '%');
    """
    cursor = connection.cursor()
    sql = """(select distinct 'LEVEL4' as LEVEL, name_4||','||name_3||','||name_2||','||name_1||','||name_0 as NAME from location_locationlevel l where name_4=UPPER(%s) limit 10)
    union
    (select distinct 'LEVEL3' as LEVEL,  name_3||','||name_2||','||name_1||','||name_0 as NAME from location_locationlevel l where name_3=UPPER(%s) limit 10)
    union
    (select distinct 'LEVEL2' as LEVEL,  name_2||','||name_1||','||name_0 as NAME from location_locationlevel l where name_2=UPPER(%s) limit 5)
    union (select distinct 'LEVEL1' as LEVEL,  name_1||','||name_0 as NAME from location_locationlevel l where name_1=UPPER(%s) limit 5)
    union (select distinct 'LEVEL0' as LEVEL,  name_0 as NAME from location_locationlevel l where name_0=UPPER(%s) limit 5) order by LEVEL;"""
    cursor.execute(sql, [lowest_level, lowest_level, lowest_level, lowest_level, lowest_level])
    rows = cursor.fetchall()
    location_hierarchy = []
    for level, location in rows:
        location_hierarchy.append(location.split(','))
    return location_hierarchy[0] if len(location_hierarchy) > 0 else [lowest_level]

_tree = None
_tree_lock = Lock()


def get_location_tree():
    global _tree
    with _tree_lock:
        if _tree is None:
            _tree = LocationTree()
    return _tree


class LocationTree(object):

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



  