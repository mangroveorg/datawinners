import logging

from datawinners.alldata.views import REPORTER_ENTITY_TYPE

from datawinners.main.database import get_db_manager
# noinspection PyUnresolvedReferences
from datawinners.search.datasender_index import update_datasender_index
from mangrove.datastore.entity import get_all_entities_include_voided
from migration.couch.utils import migrate, mark_as_completed

def undelete_datasenders_for_organization(db_name):
    logger = logging.getLogger(db_name)
    try:
        dbm = get_db_manager(db_name)
        for reporter in get_all_entities_include_voided(dbm, [REPORTER_ENTITY_TYPE]):
            try:
                if reporter.is_void():
                    reporter._doc.void = False
                    reporter.save()
            except Exception:
                logger.exception("Save of reporter with id: %s failed" % reporter.short_code)

    except Exception:
        logger.exception()
    mark_as_completed(db_name)


migrate(['hni_trailworks_lof792'], undelete_datasenders_for_organization, version=(14, 0, 2), threads=1)