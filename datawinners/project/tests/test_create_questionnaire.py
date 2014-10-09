from unittest import TestCase
from mock import Mock, patch, PropertyMock
from datawinners.accountmanagement.models import Organization
from datawinners.project.views.create_questionnaire import _is_open_survey_allowed


class TestCreateQuestionnaire(TestCase):
    def test_should_return_true_for_prosms_account_and_survey_is_marked_as_open(self):
        organization_mock = Mock(spec=Organization)
        type(organization_mock).is_pro_sms = PropertyMock(return_value=True)
        with patch("datawinners.project.views.create_questionnaire.get_organization") as get_organization:
            get_organization.return_value = organization_mock
            self.assertTrue(_is_open_survey_allowed({}, True))

    def test_should_return_false_for_prosms_account_and_survey_is_not_marked_as_open(self):
        organization_mock = Mock(spec=Organization)
        type(organization_mock).is_pro_sms = PropertyMock(return_value=True)
        with patch("datawinners.project.views.create_questionnaire.get_organization") as get_organization:
            get_organization.return_value = organization_mock
            self.assertFalse(_is_open_survey_allowed({}, False))

    def test_should_return_false_for_non_prosms_account_and_survey_is_marked_as_open(self):
        organization_mock = Mock(spec=Organization)
        type(organization_mock).is_pro_sms = PropertyMock(return_value=False)
        with patch("datawinners.project.views.create_questionnaire.get_organization") as get_organization:
            get_organization.return_value = organization_mock
            self.assertFalse(_is_open_survey_allowed({}, True))