from datawinners.search.entity_search import entity_search_update, update_index
from mangrove.datastore.documents import EntityDocument, FormModelDocument


#Registering search update methods
EntityDocument.register_post_update(entity_search_update)
FormModelDocument.register_post_update(update_index)
