import unittest

from mock import Mock

from mangrove.datastore.database import DatabaseManager
from mangrove.form_model.field import HierarchyField, TextField, DateField, GeoCodeField
from mangrove.form_model.form_model import FormModel, LOCATION_TYPE_FIELD_NAME, LOCATION_TYPE_FIELD_CODE, GEO_CODE
from datawinners.questionnaire.helper import get_location_field_code, get_geo_code_fields_question_code


class TestHelper(unittest.TestCase):
    def setUp(self):
        self.report_period_question_name = 'q1'
        self.datetime_format = 'dd.mm.yyyy'

    def test_should_give_location_code(self):
        form_model = self._get_form_model()
        form_model.add_field(self._get_location_field())
        self.assertEqual(LOCATION_TYPE_FIELD_CODE, get_location_field_code(form_model))

    def test_should_return_None_if_location_field_is_not_present(self):
        form_model = self._get_form_model()
        form_model.add_field(self._get_text_field())
        self.assertEqual(None, get_location_field_code(form_model))

    def test_should_give_geo_code(self):
        form_model = self._get_form_model()
        form_model.add_field(GeoCodeField(None, GEO_CODE, "label"))
        self.assertEqual([GEO_CODE], get_geo_code_fields_question_code(form_model))

    def test_should_give_fields_codes_for_multiple_geocode_questionnaire(self):
        GEO_CODE1 = "gc"
        form_model = self._get_form_model()
        form_model.add_field(GeoCodeField(None, GEO_CODE, "label"))
        form_model.add_field(GeoCodeField(None, GEO_CODE1, "label1"))
        self.assertEqual([GEO_CODE, GEO_CODE1], get_geo_code_fields_question_code(form_model))

    def test_should_return_None_if_geo_code_field_is_not_present(self):
        form_model = self._get_form_model()
        form_model.add_field(self._get_text_field())
        self.assertEqual([], get_geo_code_fields_question_code(form_model))

    def _get_form_model(self, is_registration_form=False):
        self.dbm = Mock(spec=DatabaseManager)
        self.form_code = "form_code"
        return FormModel(dbm=self.dbm, form_code=self.form_code, name="abc", fields=[],
            is_registration_model=is_registration_form)


    def _get_location_field(self):
        location_field = HierarchyField(name=LOCATION_TYPE_FIELD_NAME, code=LOCATION_TYPE_FIELD_CODE,
            label="anything")

        return location_field

    def _get_text_field(self):
        anything = "anything"
        text_field = TextField(name=anything, code=anything, label=anything,
            instruction=anything)
        return text_field

    def get_report_period_field(self):
        reporting_period_question = DateField(name=self.report_period_question_name,
            code=self.report_period_question_name,
            label=self.report_period_question_name,
            date_format=self.datetime_format, event_time_field_flag=True)
        return reporting_period_question
