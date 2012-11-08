# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.contrib.auth.models import User, Group
from mangrove.datastore.entity import get_by_short_code, create_entity
from datawinners.main.utils import get_database_manager
from mangrove.datastore.entity_type import define_type
from datawinners.entity.helper import create_registration_form
from datawinners.common.constant import DEFAULT_LANGUAGE
from django.utils.translation import activate
from mangrove.errors.MangroveException import EntityTypeAlreadyDefined, DataObjectNotFound
from mangrove.datastore.datadict import create_datadict_type, get_datadict_type_by_slug
from mangrove.form_model.form_model import DESCRIPTION_FIELD, MOBILE_NUMBER_FIELD, NAME_FIELD

FIRST_NAME_FIELD = "firstname"

def load_manager_for_default_test_account():
    DEFAULT_USER = "tester150411@gmail.com"
    user = User.objects.get(username=DEFAULT_USER)
    group = Group.objects.filter(name="NGO Admins")
    user.groups.add(group[0])
    return get_database_manager(user)

def create_entity_types(manager, entity_types):
    for entity_type in entity_types:
        try:
            define_type(manager, entity_type)
            activate(DEFAULT_LANGUAGE)
            create_registration_form(manager, entity_type)
        except EntityTypeAlreadyDefined:
            pass

def create_data_dict(dbm, name, slug, primitive_type, description=None):
    try:
        existing = get_datadict_type_by_slug(dbm, slug)
        existing.delete()
    except DataObjectNotFound:
        pass
    return create_datadict_type(dbm, name, slug, primitive_type, description)

def define_entity_instance(manager, entity_type, location, short_code, geometry, name=None, mobile_number=None,
                           description=None, firstname=None):
    name_type = create_data_dict(manager, name='Name Type', slug='name', primitive_type='string')
    first_name_type = create_data_dict(manager, name='Name Type', slug='firstname', primitive_type='string')
    mobile_type = create_data_dict(manager, name='Mobile Number Type', slug='mobile_number', primitive_type='string')
    description_type = create_data_dict(manager, name='Description', slug='description', primitive_type='string')
    entity = EntityBuilder(manager, entity_type, short_code)\
    .geometry(geometry)\
    .location(location)\
    .add_data(data=[(NAME_FIELD, name, name_type)])\
    .add_data([(FIRST_NAME_FIELD, firstname, first_name_type)])\
    .add_data([(MOBILE_NUMBER_FIELD, mobile_number, mobile_type)])\
    .add_data([(DESCRIPTION_FIELD, description, description_type)]).build()

    return entity

def create_or_update_entity(manager, entity_type, location, aggregation_paths, short_code, geometry=None):
    try:
        entity = get_by_short_code(manager, short_code, entity_type)
        entity.delete()
    except DataObjectNotFound:
        pass
    return create_entity(manager, entity_type, short_code, location, aggregation_paths, geometry)

def register(manager, entity_type, data, location, short_code, geometry=None):
    return EntityBuilder(manager,entity_type,short_code,).geometry(geometry).location(location).add_data(data).build()

class EntityBuilder(object):
    def __init__(self, manager, entity_type, short_code):
        self._manager = manager
        self._entity_type = entity_type
        self._short_code = short_code
        self._geometry, self._aggregation_paths, self._location = [None]*3
        self._data = []

    def aggregation_paths(self, aggregation_paths):
        self._aggregation_paths = aggregation_paths
        return self

    def geometry(self, geometry):
        self._geometry = geometry
        return self

    def location(self, location):
        self._location = location
        return self

    def add_data(self,data):
        self._data.append(data)
        return self

    def build(self):
        entity = create_or_update_entity(self._manager, entity_type=self._entity_type, short_code=self._short_code,
            aggregation_paths=self._aggregation_paths, location=self._location, geometry=self._geometry)
        for each in self._data: entity.add_data(each)
        return entity

