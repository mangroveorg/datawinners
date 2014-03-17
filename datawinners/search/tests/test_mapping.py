import unittest

from mock import Mock, patch

from mangrove.datastore.database import DatabaseManager
from datawinners.search import form_model_change_handler
from mangrove.form_model.form_model import FormModel, EntityFormModel
from mangrove.datastore.documents import  FormModelDocument


class TestMapping(unittest.TestCase):
    def test_should_call_data_sender_mapping_update_for_registration_form_model(self):
        dbm = Mock(spec=DatabaseManager)
        form_model_document = Mock(spec= FormModelDocument)
        form_model_document.form_code = "reg"
        with patch("mangrove.form_model.form_model.EntityFormModel.new_from_doc") as new_from_doc:
            with patch("datawinners.search.mapping.create_ds_mapping") as create_ds_mapping:
                entity_form_model = EntityFormModel(dbm)
                entity_form_model._doc=form_model_document
                new_from_doc.return_value = entity_form_model
                form_model_change_handler(form_model_document, dbm)
                assert create_ds_mapping.called

    def test_should_call_subject_mapping_update_for_registration_form_model(self):
        dbm = Mock(spec=DatabaseManager)
        form_model_document = Mock(spec= FormModelDocument)
        form_model_document.form_code = "clinic"
        with patch("mangrove.form_model.form_model.EntityFormModel.new_from_doc") as new_from_doc:
            with patch("datawinners.search.mapping.create_subject_mapping") as create_subject_mapping:
                entity_form_model = EntityFormModel(dbm)
                entity_form_model._doc=form_model_document
                new_from_doc.return_value = entity_form_model
                form_model_change_handler(form_model_document, dbm)
                assert create_subject_mapping.called

    def test_should_call_submission_mapping_if_not_registration_form_model(self):
        dbm = Mock(spec=DatabaseManager)
        form_model_document = Mock(spec=FormModelDocument)
        with patch("mangrove.form_model.form_model.FormModel.new_from_doc") as new_from_doc:
            with patch("datawinners.search.mapping.create_submission_mapping") as create_submission_mapping:
                form_model = FormModel(dbm,form_code='clinic')
                form_model._doc=form_model_document
                new_from_doc.return_value = form_model
                form_model_change_handler(form_model_document, dbm)
                assert create_submission_mapping.called
