from unittest.case import TestCase

from mock import Mock, patch
from django.contrib.auth.models import User

from datawinners.entity.helper import add_imported_data_sender_to_trial_organization, get_country_appended_location, question_code_generator, create_registration_form
from datawinners.accountmanagement.models import Organization


class TestHelper(TestCase):
    def setUp(self):
        self.manager = Mock()

    def test_should_build_question_code(self):
        generator = question_code_generator()
        self.assertEqual('q1', generator.next())
        self.assertEqual('q2', generator.next())
        self.assertEqual('q3', generator.next())

    def test_should_add_imported_data_senders_to_trial_organization(self):
        self.org_id = "QZJ729195"
        with patch.object(User, "get_profile") as get_profile:
            get_profile.return_value = dict(org_id=self.org_id)
        request = Mock()
        request.user = Mock(spec=User)
        ds_mobile_numbers = ["0333333333", "0333733333"]
        with patch("datawinners.entity.helper.add_data_sender_to_trial_organization") as add_ds_to_trial:
            with patch("datawinners.accountmanagement.models.Organization.objects.get") as get_organization_mock:
                get_organization_mock.return_value = self.get_organization(org_id=self.org_id)
                org = Organization.objects.get(org_id="AK29")
                self.assertEqual(org.org_id, self.org_id)

                all_data_senders = [dict(cols=[mobile_number], short_code="rep%d" % key)
                                    for key, mobile_number in enumerate(ds_mobile_numbers)]
                add_imported_data_sender_to_trial_organization(request, ['rep0', 'rep1'], all_data_senders)
                self.assertEqual(add_ds_to_trial.call_count, 2)

    def test_should_append_country_in_case_location_hierarchy_does_not_have_it(self):
        country_appended_location = get_country_appended_location('Pune', 'India')
        self.assertEqual('Pune,India', country_appended_location)

    def test_should_not_append_country_in_case_location_hierarchy_already_has_it(self):
        country_appended_location = get_country_appended_location('Pune , India', 'India')
        self.assertEqual('Pune,India', country_appended_location)

    def get_organization(self, org_id="ABCD"):
        organization = Mock(spec=Organization)
        organization.org_id = org_id
        organization.in_trial_mode = True
        organization._state = "Madagascar"
        return organization

    def test_should_save_created_registration_form_for_given_entity_name(self):
        with patch("datawinners.entity.helper._generate_form_code") as form_code_generator_mock:
            with patch("datawinners.entity.helper._create_registration_form") as registration_form_creator_mock:
                database_manager = Mock(name="dbm_mock")
                form_model_mock = Mock(name="form_model_mock")
                form_code_generator_mock.return_value = "form_code"
                registration_form_creator_mock.return_value = form_model_mock

                create_registration_form(database_manager, "entityname")

                form_model_mock.save.assert_called_with()

    def test_should_create_registration_form_for_given_entity_type_and_generated_form_code(self):
        with patch("datawinners.entity.helper._generate_form_code") as form_code_generator_mock:
            with patch("datawinners.entity.helper._create_registration_form") as registration_form_creator_mock:
                database_manager = Mock(name="dbm_mock")
                form_model_mock = Mock(name="form_model_mock")
                form_code_generator_mock.return_value = "form_code"
                registration_form_creator_mock.return_value = form_model_mock

                create_registration_form(database_manager, "entitytypename")

                registration_form_creator_mock.assert_called_with(database_manager, "entitytypename", "form_code",
                                                                                                    ["entitytypename"])


    def test_should_return_created_registration_form(self):
        with patch("datawinners.entity.helper._generate_form_code") as form_code_generator_mock:
            with patch("datawinners.entity.helper._create_registration_form") as registration_form_creator_mock:
                database_manager = Mock(name="dbm_mock")
                form_model_mock = Mock(name="form_model_mock")
                form_code_generator_mock.return_value = "form_code"
                registration_form_creator_mock.return_value = form_model_mock

                actual_form_model = create_registration_form(database_manager, "entitytypename")

                self.assertEqual(actual_form_model, form_model_mock, "form_model not returned after creation")

    def test_should_return_created_registration_form(self):
        with patch("datawinners.entity.helper._generate_form_code") as form_code_generator_mock:
            with patch("datawinners.entity.helper._create_registration_form") as registration_form_creator_mock:
                database_manager = Mock(name="dbm_mock")
                form_model_mock = Mock(name="form_model_mock")
                form_code_generator_mock.return_value = "form_code"
                registration_form_creator_mock.return_value = form_model_mock

                actual_form_model = create_registration_form(database_manager, "entitytypename")

                self.assertEqual(actual_form_model, form_model_mock, "form_model not returned after creation")

    def test_should_generate_form_code_with_prefix_as_first_3_characters_of_entity_name(self):
        with patch("datawinners.entity.helper._generate_form_code") as form_code_generator_mock:
            with patch("datawinners.entity.helper._create_registration_form") as registration_form_creator_mock:
                database_manager = Mock(name="dbm_mock")
                form_model_mock = Mock(name="form_model_mock")
                form_code_generator_mock.return_value = "form_code"
                registration_form_creator_mock.return_value = form_model_mock

                create_registration_form(database_manager, "name")

                form_code_generator_mock.assert_called_with(database_manager, "nam")

    def test_should_generate_form_code_with_prefix_as_first_3_non_space_characters_of_entity_name(self):
        with patch("datawinners.entity.helper._generate_form_code") as form_code_generator_mock:
            with patch("datawinners.entity.helper._create_registration_form") as registration_form_creator_mock:
                database_manager = Mock(name="dbm_mock")
                form_model_mock = Mock(name="form_model_mock")
                form_code_generator_mock.return_value = "form_code"
                registration_form_creator_mock.return_value = form_model_mock

                create_registration_form(database_manager, "na me")

                form_code_generator_mock.assert_called_with(database_manager, "nam")