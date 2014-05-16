# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from datawinners.accountmanagement.models import TEST_REPORTER_MOBILE_NUMBER
from datawinners.common.lang.utils import create_custom_message_templates
from datawinners.main.utils import  sync_views

from mangrove.bootstrap import initializer as mangrove_intializer
from mangrove.datastore.entity import create_entity, get_by_short_code_include_voided
from mangrove.errors.MangroveException import DataObjectNotFound
from mangrove.form_model.form_model import   MOBILE_NUMBER_FIELD, NAME_FIELD
from mangrove.transport.repository.reporters import REPORTER_ENTITY_TYPE


REPORTER_SHORT_CODE = 'test'
DEFAULT_LOCATION = ["madagascar"]

def create_default_reporter(manager):
    try:
        entity = get_by_short_code_include_voided(manager, REPORTER_SHORT_CODE, REPORTER_ENTITY_TYPE)
        entity.delete()
    except DataObjectNotFound:
        pass
    entity = create_entity(dbm=manager, entity_type=REPORTER_ENTITY_TYPE, short_code=REPORTER_SHORT_CODE,
                           location=DEFAULT_LOCATION)

    data = [(MOBILE_NUMBER_FIELD, TEST_REPORTER_MOBILE_NUMBER), (NAME_FIELD, 'TEST')]
    entity.add_data(data=data)


def run(manager):
    sync_views(manager)
    mangrove_intializer.run(manager)
    create_default_reporter(manager)
    create_custom_message_templates(manager)
