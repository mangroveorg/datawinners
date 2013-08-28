import logging
import sys

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, ".")

from datawinners.main.database import get_db_manager
from migration.couch.utils import mark_start_of_migration, migrate
from mangrove.datastore.entity import Entity
from mangrove.datastore.documents import FormModelDocument, EntityDocument
from mangrove.form_model.form_model import FormModel
from datawinners.main.couchdb.utils import all_db_names


map_form_model_for_subject_questionnaires = """
function(doc) {
    if (doc.document_type == 'FormModel' && doc.form_code != 'reg'
        && doc.is_registration_model && !doc.void) {
        for (var i in doc.json_fields){
            var field = doc.json_fields[i];
            if (field.name == 'geo_code'){
	            emit(doc.form_code, doc);
            }
        }
    }
}"""

map_subject_entity_by_type = """
function(doc){
    if (doc.document_type == 'Entity' && !doc.geometry.hasOwnProperty('coordinates')
        && doc.aggregation_paths._type[0] != "reporter" && !doc.void) {
        emit(doc.aggregation_paths._type[0], doc);
    }
}"""


def get_instance_from_doc(manager, value, classname=FormModel, documentclassname=FormModelDocument):
    doc = documentclassname.wrap(value)
    instance = classname.new_from_doc(manager, doc)
    return instance

def add_geometry_data(db_name):
    logger = logging.getLogger(db_name)

    #logger.info('Start migration on database')
    try:
        manager = get_db_manager(db_name)
        
        subject_form_model_docs = manager.database.query(map_form_model_for_subject_questionnaires)
        mark_start_of_migration(db_name)

        for subject_form_model_doc in subject_form_model_docs:
            form_model = get_instance_from_doc(manager, subject_form_model_doc['value'])

            entity_docs = manager.database.query(map_subject_entity_by_type, key=form_model.entity_type[0])

            for entity_doc in entity_docs:

                entity = get_instance_from_doc(manager, entity_doc['value'], classname=Entity, documentclassname=EntityDocument)
                logger.info("    Database: " + db_name + "   type: " + form_model.entity_type[0] + "  short_code: " + entity.short_code)
        
                if not "coordinates" in entity.geometry:
                    geometry = {'type': 'Point', 'coordinates': [0, 0]}
                    entity.set_location_and_geo_code(entity.location_path, geometry)
                    entity.save()

        #logger.info('End migration on database')
    except Exception as e:
        logger.exception(e.message)


migrate(all_db_names(), add_geometry_data, version=(8, 0, 2))