# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import unittest

from mock import Mock, patch

from mangrove.transport.contract.response import Response
from mangrove.datastore.database import DatabaseManager
from datawinners.entity.import_data import _get_form_model_questions
from datawinners.entity.import_data import FilePlayer
from mangrove.form_model.form_model import FormModel
from datawinners.accountmanagement.models import Organization
from collections import OrderedDict


class TestImportData(unittest.TestCase):

    def test_should_not_append_country_to_if_location_field_is_empty_in_imported_excel(self):
        mock_dbm = Mock(spec=DatabaseManager)
        file_player = FilePlayer(mock_dbm, Mock, 'csv')
        form_model = Mock(spec=FormModel)
        with patch('datawinners.entity.import_data.get_location_field_code') as get_location_field_code:
            with patch('datawinners.entity.import_data.get_country_appended_location') as get_country_appended_location:
                get_location_field_code.return_value = 'q2'
                get_country_appended_location.return_value = 'loc,Madagascar'
                result = file_player._append_country_for_location_field(form_model, {'q1': 'val1', 'q2': ''},Mock(spec=Organization))
                self.assertEquals(result,{'q1': 'val1', 'q2': ''})

    def test_should_append_country_to_if_location_present_in_imported_excel(self):
            mock_dbm = Mock(spec=DatabaseManager)
            file_player = FilePlayer(mock_dbm, Mock, 'csv')
            form_model = Mock(spec=FormModel)
            with patch('datawinners.entity.import_data.get_location_field_code') as get_location_field_code:
                with patch('datawinners.entity.import_data.get_country_appended_location') as get_country_appended_location:
                    get_location_field_code.return_value = 'q2'
                    get_country_appended_location.return_value = 'loc,Madagascar'
                    result = file_player._append_country_for_location_field(form_model, {'q1': 'val1', 'q2': 'loc'},Mock(spec=Organization))
                    self.assertEquals(result,{'q1': 'val1', 'q2': 'loc,Madagascar'})

    def test_should_fetch_questions_from_form_model_for_non_subject_entity(self):
        manager = Mock(spec=DatabaseManager)
        with patch("datawinners.entity.import_data.get_form_model_by_code") as get_form_model_by_code:
            _get_form_model_questions(manager, (1, Response(form_code='formcode', entity_type=['clinic']))  )
            get_form_model_by_code.assert_called_with(manager, 'formcode')

    def test_should_fetch_questions_from_for_reporter(self):
        manager = Mock(spec=DatabaseManager)
        with patch("datawinners.entity.import_data.get_form_model_by_code") as get_form_model_by_code:
            return_dict = _get_form_model_questions(manager, (1, Response(form_code='formcode', entity_type=['reporter'])))
            self.assertEquals(return_dict, {'n':'&#39;Name&#39;', 'm':'&#39;Mobile Number&#39;'})


    def test_import_should_update_or_not_according_to_is_update_params(self):
        self.assertTrue(1)

        mock_dbm = Mock(spec=DatabaseManager)
        mock_dbm.database_name = "hni_testorg_slx364903"
        parser = Mock()
        parser.parse = Mock()
        expected_data = [(u'com', OrderedDict([(u'q2', u'Andry'), (u'q6', u'ranoum')]))]#,
            #(u'com', OrderedDict([(u'q2', u'Safidy'), (u'q6', u'Titi')]))]
        parser.parse.return_value = expected_data
        file_player = FilePlayer(mock_dbm, parser, 'csv')
        file_player2 = FilePlayer(mock_dbm, parser, 'csv', is_update=True)

        with patch("datawinners.utils.get_organization_from_manager") as get_ngo:
            get_ngo.return_value = Mock()
            with patch.object(FilePlayer, "_get_form_model") as get_form_model:
                get_form_model.return_value = Mock()
                with patch("mangrove.transport.player.player.Player.submit") as submit_patch:
                    with patch("datawinners.entity.import_data.get_location_field_code") as location_field_code:
                        from datawinners.entity.subject_template_validator import SubjectTemplateValidator
                        with patch.object(SubjectTemplateValidator, "validate") as subject_validator:
                            location_field_code.return_value = Mock()
                            subject_validator.return_value = Mock()
                            file_player.accept(file_contents=Mock())
                            submit_patch.assert_called_with(get_form_model(), expected_data[0][1], [], False)


                            file_player2.accept(file_contents=Mock())
                            submit_patch.assert_called_with(get_form_model(), expected_data[0][1], [], True)
        

def dummy_get_location_hierarchy(foo):
    return [u'arantany']

