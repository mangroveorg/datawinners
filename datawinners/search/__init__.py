from datawinners.search.mapping import form_model_change_handler
from datawinners.search.submission_index import update_submission_search_index, submission_update_on_entity_edition
from datawinners.search.subject_index import entity_search_update
from mangrove.datastore.documents import EntityDocument, FormModelDocument, SurveyResponseDocument

from datawinners.project.models import Project
from datawinners.search.datasender_index import update_datasender_for_project_change, create_ds_mapping

_postsave_registered = False
def register_postsave_handlers():
    global _postsave_registered
    if _postsave_registered: return
    EntityDocument.register_post_update(entity_search_update)

    FormModelDocument.register_post_update(form_model_change_handler)
    Project.register_post_update(update_datasender_for_project_change)

    SurveyResponseDocument.register_post_update(update_submission_search_index)
    EntityDocument.register_post_update(submission_update_on_entity_edition)
    _postsave_registered = True

register_postsave_handlers()