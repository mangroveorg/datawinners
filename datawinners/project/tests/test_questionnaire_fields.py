from unittest import TestCase
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MaxLengthValidator, RegexValidator
from mock import Mock
from datawinners.entity.fields import PhoneNumberField
from mangrove.form_model.form_model import LOCATION_TYPE_FIELD_NAME
from mangrove.form_model.validation import NumericRangeConstraint, TextLengthConstraint, RegexConstraint
from mangrove.form_model.field import SelectField, IntegerField, GeoCodeField, TextField, TelephoneNumberField, HierarchyField, ShortCodeField
from datawinners.project.questionnaire_fields import TextInputForFloat, FormField, GeoCodeValidator, as_choices
from django.utils.translation import activate


class TestTextInputForFloat(TestCase):
    def test_has_not_changed_for_different_string_representation_of_same_float_value(self):
        text_input = TextInputForFloat()
        self.assertFalse(text_input._has_changed('22.0', '22'))

    def test_has_not_changed_for_same_float_values(self):
        text_input = TextInputForFloat()
        self.assertFalse(text_input._has_changed(22.00, 22))

    def test_has_not_changed_for_none_values(self):
        text_input = TextInputForFloat()
        self.assertFalse(text_input._has_changed(None, None))

    def test_has_changed_for_different_strings(self):
        text_input = TextInputForFloat()
        self.assertTrue(text_input._has_changed('testone', 'testtwo'))

    def test_has_changed_for_a_string_and_float(self):
        text_input = TextInputForFloat()
        self.assertTrue(text_input._has_changed('testone', 22))


class TestFormField(TestCase):

    def test_select_field_creation_with_single_select(self):
        select_field = SelectField("select something", "some_code", "what do u want to select",
                                   [('opt1', 'a'), ('opt2', 'b'), ('opt3', 'c')],
                                   "Choose 1 answer from the list. Example: a")
        select_field.value = 'a'
        choice_field = FormField().create(select_field)
        self.assertTrue(isinstance(choice_field.widget, forms.widgets.Select))
        self.assertEquals(choice_field.initial, 'a')
        self.assertEquals([('', '--None--'), ('a', 'opt1'), ('b', 'opt2'), ('c', 'opt3')], choice_field.choices)
        self.assertEqual(choice_field.help_text, "Choose 1 answer from the list. Example: a")
        #activate('fr')
        #from datawinners.project.helper import get_field_instruction
        #self.assertEqual(get_field_instruction(choice_field), u"Choisissez une reponse de la liste. Exemple: a")

    def test_select_field_creation_with_multi_select(self):
        select_field = SelectField("select something", "some_code", "what do u want to select",
                                   [('opt1', 'a'), ('opt2', 'b'), ('opt3', 'c')],
                                   "Choose 1 or more answers from the list. Example: a or ab ", single_select_flag=False)
        select_field.value = 'opt1,opt2'
        choice_field = FormField().create(select_field)
        self.assertTrue(isinstance(choice_field.widget, forms.CheckboxSelectMultiple))
        self.assertEquals(choice_field.initial, ['a', 'b'])
        self.assertEquals([('a', 'opt1'), ('b', 'opt2'), ('c', 'opt3')], choice_field.choices)
        self.assertEqual(choice_field.help_text, "Choose 1 or more answers from the list. Example: a or ab ")

    def test_integer_field_for_range(self):
        int_field = IntegerField("age", 'age', 'age', "Answer must be a number between 10-100.", constraints=[NumericRangeConstraint(min='10', max='100')])

        field = FormField().create(int_field)
        self.assertTrue(isinstance(field.widget, TextInputForFloat))
        self.assertEquals(field.widget.attrs['watermark'], '10 -- 100')
        self.assertEqual(field.max_value, 100)
        self.assertEqual(field.min_value, 10)
        self.assertEqual(field.help_text, "Answer must be a number between 10-100.")

    def test_integer_field_for_max_number(self):
        int_field = IntegerField("age", 'age', 'age', "Answer must be a number. The maximum is 100.", constraints=[NumericRangeConstraint(max='100')])

        field = FormField().create(int_field)
        self.assertTrue(isinstance(field.widget, TextInputForFloat))
        self.assertEquals(field.widget.attrs['watermark'], 'Upto 100')
        self.assertEqual(field.max_value, 100)
        self.assertEqual(field.min_value, None)
        self.assertEqual(field.help_text, "Answer must be a number. The maximum is 100.")

    def test_integer_field_for_min_number(self):
        int_field = IntegerField("age", 'age', 'age', "Answer must be a number. The minimum is 100.", constraints=[NumericRangeConstraint(min='100')])

        field = FormField().create(int_field)
        self.assertTrue(isinstance(field.widget, TextInputForFloat))
        self.assertEquals(field.widget.attrs['watermark'], 'Minimum 100')
        self.assertEqual(field.min_value, 100)
        self.assertEqual(field.max_value, None)
        self.assertEqual(field.help_text, "Answer must be a number. The minimum is 100.")

    def test_gps_field(self):
        field = GeoCodeField("gps 1", "gps1", "gps of this", "Answer must be GPS coordinates in the following format (latitude,longitude). Example: -18.1324,27.6547")
        geo_code_field = FormField().create(field)

        self.assertEquals(1, len(geo_code_field.validators))
        self.assertTrue(isinstance(geo_code_field.validators[0], GeoCodeValidator))
        self.assertEquals(geo_code_field.widget.attrs["watermark"], "xx.xxxx,yy.yyyy")
        self.assertIsNone(geo_code_field.widget.attrs.get('class'))
        self.assertEqual(field.instruction, "Answer must be GPS coordinates in the following format (latitude,longitude). Example: -18.1324,27.6547")

    def test_entity_field(self):
        field = ShortCodeField("name", "name", "what is ur name", instruction="Answer must be 20 characters maximum", constraints=[TextLengthConstraint(min=5, max=100)])
        entity_field = FormField().create(field)

        self.assertEquals(2, len(entity_field.validators))
        self.assertEquals(entity_field.widget.attrs["watermark"], "Between 5 -- 100 characters")
        self.assertEquals(entity_field.widget.attrs['class'], 'subject_field')
        self.assertEqual(entity_field.min_length, 5)
        self.assertEqual(entity_field.max_length, 100)
        self.assertEqual(field.instruction, "Answer must be 20 characters maximum")

    def test_phone_number_field(self):
        field = TelephoneNumberField('phone', 'phone_code', 'phone',
                                     constraints=[TextLengthConstraint(min=10, max=12),
                                                  RegexConstraint(reg='^[0-9]+$')],
                                     instruction="Answer must be country code plus telephone number. Example: 261333745269")
        phone_field = FormField().create(field)
        self.assertTrue(isinstance(phone_field, PhoneNumberField))
        self.assertEqual(len(phone_field.validators), 3)
        self.assertEqual(phone_field.widget.attrs['watermark'], 'Between 10 -- 12 characters')
        validator_types = []
        for validator in phone_field.validators:
            validator_types.append(type(validator))
        self.assertTrue(MinLengthValidator in validator_types)
        self.assertTrue(MaxLengthValidator in validator_types)
        self.assertTrue(RegexValidator in validator_types)
        self.assertEqual(field.instruction, "Answer must be country code plus telephone number. Example: 261333745269")

    def test_location_field(self):
        field = HierarchyField(LOCATION_TYPE_FIELD_NAME, "some_code", "some label", "Answer must be a word")
        location_field = FormField().create(field)
        self.assertEquals(location_field.widget.attrs['class'], 'location_field')
        self.assertEquals(location_field.widget.attrs['watermark'], '')
        self.assertEqual(field.instruction, "Answer must be a word")


class TestGeoCodeValidator(TestCase):
    def validation_error(self, value):
        try:
            GeoCodeValidator()(value)
            self.fail('Should fail for invalid value ' + value)
        except ValidationError as e:
            self.assertEquals(e.messages,
                              [
                                  u'Incorrect GPS format. The GPS coordinates must be in the following format: xx.xxxx,yy.yyyy. Example -18.8665,47.5315'])


    def test_fails_for_invalid_geo_codes(self):
        self.validation_error('1,')
        self.validation_error(',1')
        self.validation_error('')
        self.validation_error('1,1,1,1')


class TestWebSubmissionForm(TestCase):

    def test_should_populate_on_behalf_choice_with_name_and_short_code_when_datasender_name_present(self):
        entities = [{'name': 'name1', 'short_code': 'rep1'}, {'name': 'name2', 'short_code': 'rep2'}]

        actual_list = as_choices(entities)

        self.assertListEqual(actual_list, [('rep1', 'name1  (rep1)'), ('rep2', 'name2  (rep2)')])


    def test_should_populate_on_behalf_choice_with_mobile_number_and_short_code_when_datasender_name_not_present(self):
        entities = [{'name': '', 'short_code': 'rep1', 'mobile_number': '1234'}, {'name': 'name2', 'short_code': 'rep2'}]

        actual_list = as_choices(entities)

        self.assertListEqual(actual_list, [('rep1', '1234  (rep1)'), ('rep2', 'name2  (rep2)')])