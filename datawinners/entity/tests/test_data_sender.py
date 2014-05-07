from django.contrib.auth.models import User
from django.utils.unittest.case import TestCase
from mock import patch, Mock

from datawinners.entity.data_sender import remove_system_datasenders, DataSenderRegistrationValidator


class TestDataSender(TestCase):
    def test_remove_test_datasenders(self):
        ds_list = [{"short_code": "non-test"}, {"short_code":"test"}]
        remove_system_datasenders(ds_list)
        self.assertEqual(ds_list, [{"short_code": "non-test"}])


class TestDataSenderRegistrationValidator(TestCase):
    def test_should_return_no_errors_when_all_valid_details_entered(self):
        values = {
            'name': "ds",
            'email': "jim@gmail.com",
            'devices': 'web',
            'telephone_number': '1123123122',
            'location': 'loc123',
            'geo_code': '1.11,2.22',
            'short_code': '',
        }

        with patch("datawinners.entity.data_sender.User") as UserMock:
            objects_filter_mock = Mock()
            UserMock.objects = objects_filter_mock
            objects_filter_mock.filter.return_value = None
            errors, cleaned_data = DataSenderRegistrationValidator().validate(values)

        self.assertDictEqual(errors, {})
        self.assertDictEqual(cleaned_data, values)

    def test_should_return_mandatory_field_errors_when_mandatory_fields_not_present(self):
        values = {
            'name': "",
            'email': "",
            'telephone_number': '',
            'location': '',
            'geo_code': '',
            'short_code': '',
        }

        errors, cleaned_data = DataSenderRegistrationValidator().validate(values)


        expected_errors = {
                            'name': 'This field is required.',
                            'telephone_number': 'This field is required.',
                            'location': 'Please fill out at least one location field correctly.',
                            'geo_code': 'Please fill out at least one location field correctly.'
                          }
        self.assertDictEqual(errors, expected_errors)

    def test_should_return_no_location_related_errors_when_location_name_is_present(self):
        values = {
            'name': "dsname",
            'email': "",
            'telephone_number': '12312312',
            'location': 'loc2',
            'geo_code': '',
            'short_code': '',
        }

        errors, cleaned_data = DataSenderRegistrationValidator().validate(values)


        self.assertDictEqual(errors, {})

    def test_should_return_no_location_related_errors_when_geo_code_is_present(self):
        values = {
            'name': "dsname",
            'email': "",
            'telephone_number': '12312312',
            'location': '',
            'geo_code': '1.11,2.22',
            'short_code': '',
        }

        errors, cleaned_data = DataSenderRegistrationValidator().validate(values)
        self.assertDictEqual(errors, {})

    def test_should_return_geo_code_error_when_geo_code_format_is_incorrect(self):
        values = {
            'name': "dsname",
            'email': "",
            'telephone_number': '12312312',
            'location': '',
            'geo_code': '2.22',
            'short_code': '',
        }

        errors, cleaned_data = DataSenderRegistrationValidator().validate(values)
        self.assertDictEqual(errors, {
                                'geo_code': 'Incorrect GPS format. The GPS coordinates must be in the following format: xx.xxxx,yy.yyyy. Example -18.8665,47.5315'
                            })

    def test_should_return_error_when_name_has_special_characters(self):
        values = {
            'name': "dsname((",
            'email': "",
            'telephone_number': '12312312',
            'location': '',
            'geo_code': '1.11,2.22',
            'short_code': '',
        }

        errors, cleaned_data = DataSenderRegistrationValidator().validate(values)

        self.assertDictEqual(errors, {
                                'name': "Please enter a valid value containing only letters a-z or A-Z or symbols '`- "
                            })


    def test_should_return_error_when_email_is_of_incorrect_format(self):
        values = {
            'name': "dsname",
            'email': "jkjlk",
            'telephone_number': '12312312',
            'location': '',
            'geo_code': '1.11,2.22',
            'short_code': '',
        }

        errors, cleaned_data = DataSenderRegistrationValidator().validate(values)

        self.assertDictEqual(errors, {
                                'email': "Enter a valid email address. Example:name@organization.com"
                            })

    def test_should_return_error_for_duplicate_email_address(self):
        values = {
            'name': "dsname",
            'email': "dup@gmail.com",
            'telephone_number': '12312312',
            'location': '',
            'geo_code': '1.11,2.22',
            'short_code': '',
        }

        with patch("datawinners.entity.data_sender.User") as UserMock:
            objects_filter_mock = Mock()
            UserMock.objects = objects_filter_mock
            objects_filter_mock.filter.return_value = User()
            errors, cleaned_data = DataSenderRegistrationValidator().validate(values)

        self.assertDictEqual(errors, {
                                'email': "This email address is already in use. Please supply a different email address."
                            })

    def test_should_not_return_error_for_unique_email_address(self):
        values = {
            'name': "dsname",
            'email': "new@gmail.com",
            'telephone_number': '12312312',
            'location': '',
            'geo_code': '1.11,2.22',
            'short_code': '',
        }

        with patch("datawinners.entity.data_sender.User") as UserMock:
            objects_filter_mock = Mock()
            UserMock.objects = objects_filter_mock
            objects_filter_mock.filter.return_value = None
            errors, cleaned_data = DataSenderRegistrationValidator().validate(values)

        self.assertDictEqual(errors, {})


    def test_should_return_error_when_web_access_required_and_email_is_not_specified(self):
        values = {
            'name': "dsname",
            'email': "",
            'devices': 'web',
            'telephone_number': '12312312',
            'location': '',
            'geo_code': '1.11,2.22',
            'short_code': '',
        }

        with patch("datawinners.entity.data_sender.User") as UserMock:
            objects_filter_mock = Mock()
            UserMock.objects = objects_filter_mock
            objects_filter_mock.filter.return_value = None
            errors, cleaned_data = DataSenderRegistrationValidator().validate(values)

        self.assertDictEqual(errors, {'email': 'This field is required.'})




    def test_should_return_no_error_when_valid_email_address_format_is_entered(self):
        values = {
            'name': "dsname",
            'email': "dc@email.com",
            'telephone_number': '12312312',
            'location': '',
            'geo_code': '1.11,2.22',
            'short_code': '',
        }

        with patch("datawinners.entity.data_sender.User") as UserMock:
            objects_filter_mock = Mock()
            UserMock.objects = objects_filter_mock
            objects_filter_mock.filter.return_value = None
            errors, cleaned_data = DataSenderRegistrationValidator().validate(values)

        self.assertDictEqual(errors, {})

    def test_should_return_error_when_phone_number_is_less_than_5_digits(self):
        values = {
            'name': "dsname",
            'email': "",
            'telephone_number': '1234',
            'location': '',
            'geo_code': '1.11,2.22',
            'short_code': '',
        }

        errors, cleaned_data = DataSenderRegistrationValidator().validate(values)

        self.assertDictEqual(errors, {
                          'telephone_number': 'Ensure this value has at least 5 digits (it has 4).'
                        })

    def test_should_return_error_when_phone_number_is_of_incorrect_format(self):
        values = {
            'name': "dsname",
            'email': "",
            'telephone_number': '1234uuu',
            'location': '',
            'geo_code': '1.11,2.22',
            'short_code': '',
        }

        errors, cleaned_data = DataSenderRegistrationValidator().validate(values)
        self.assertDictEqual(errors, {
                          'telephone_number': 'Please enter a valid phone number.'
                        })

    def test_should_return_error_when_unique_id_has_special_characters(self):
        values = {
            'name': "dsname",
            'email': "",
            'telephone_number': '1234847',
            'location': '',
            'geo_code': '1.11,2.22',
            'short_code': '^asdas**',
        }

        errors, cleaned_data = DataSenderRegistrationValidator().validate(values)
        self.assertDictEqual(errors, {
                          'short_code': 'Only letters and numbers are valid'
                        })





