import unittest

from mangrove.datastore.documents import ProjectDocument
from mangrove.form_model.project import Project
from mangrove.form_model.tests.test_form_model_unit_tests import DatabaseManagerStub
from mangrove.form_model.xform import Xform
from mock import Mock

from datawinners.blue.rules.rule import Rule
from datawinners.blue.xform_edit.validator import Validator


class TestXformValidator(unittest.TestCase):

    def test_should_validate_xform_change(self):
        rule1 = Mock(Rule)
        rule2 = Mock(Rule)

        new_questionnaire = Project.new_from_doc(DatabaseManagerStub(), ProjectDocument())
        old_questionnaire = Project.new_from_doc(DatabaseManagerStub(), ProjectDocument())
        old_questionnaire.xform_model = Mock(Xform)
        new_questionnaire.xform_model = Mock(Xform)

        old_questionnaire.xform_model.equals.return_value = True
        self.assertTrue(Validator([rule1, rule2]).valid(new_questionnaire, old_questionnaire))
        rule1.update_xform.assert_called_once_with(old_questionnaire, new_questionnaire)

        old_questionnaire.xform_model.equals.return_value = False
        self.assertFalse(Validator([rule1, rule2]).valid(new_questionnaire, old_questionnaire))