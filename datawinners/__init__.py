# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'datawinners.settings'

from datawinners.search.entity_search import entity_search_update, update_index
from mangrove.datastore.documents import EntityDocument, FormModelDocument


#Registering search update methods
EntityDocument.register_post_update(entity_search_update)
FormModelDocument.register_post_update(update_index)
