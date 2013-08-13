import logging
import sys

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, ".")

from datawinners.main.database import get_db_manager
from migration.couch.utils import mark_start_of_migration, migrate
from mangrove.datastore.entity import get_by_short_code


def add_geometry_data(db_name):
    logger = logging.getLogger(db_name)

    logger.info('Start migration on database')
    try:
        manager = get_db_manager(db_name)
        mark_start_of_migration(db_name)

        entity = get_by_short_code(manager, "110701001", ["fokontany"])

        if not "coordinates" in entity.geometry:
            geometry = {'type': 'Point', 'coordinates': [0, 0]}
            entity.set_location_and_geo_code(entity.location_path, geometry)
            entity.save()

        logger.info('End migration on database')
    except Exception as e:
        logger.exception(e.message)


migrate(['hni_psi-madagascar_qmx864597'], add_geometry_data, version=(7, 0, 6))