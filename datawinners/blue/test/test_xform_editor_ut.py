import unittest

import mock
from mangrove.datastore.documents import ProjectDocument
from mangrove.form_model.project import Project
from mangrove.form_model.tests.test_form_model_unit_tests import DatabaseManagerStub
from mangrove.form_model.xform import Xform
from mock import Mock

import datawinners
from datawinners.blue.rules.rule import Rule
from datawinners.blue.xform_editor import XFormEditor, UnsupportedXformEditException


class TestXformEditor(unittest.TestCase):

    def test_should_validate_xform_change(self):
        rule1 = Mock(Rule)
        rule2 = Mock(Rule)

        datawinners.blue.rules.REGISTERED_RULES[:] = []
        datawinners.blue.rules.REGISTERED_RULES.extend([rule1, rule2])

        new_questionnaire = Project.new_from_doc(DatabaseManagerStub(), ProjectDocument())
        old_questionnaire = Project.new_from_doc(DatabaseManagerStub(), ProjectDocument())
        old_questionnaire.xform_model = Mock(Xform)

        old_questionnaire.xform_model.equals.return_value = True
        self.assertTrue(XFormEditor()._validate(new_questionnaire, old_questionnaire))
        rule1.update_xform.assert_called_once_with(old_questionnaire, new_questionnaire)

        old_questionnaire.xform_model.equals.return_value = False
        self.assertFalse(XFormEditor()._validate(new_questionnaire, old_questionnaire))

    def test_should_throw_unsupported_xform_edit_exception(self):
        rule1 = Mock(Rule)

        datawinners.blue.rules.REGISTERED_RULES[:] = []
        datawinners.blue.rules.REGISTERED_RULES.extend([rule1])

        new_questionnaire = Project.new_from_doc(DatabaseManagerStub(), ProjectDocument())
        old_questionnaire = Project.new_from_doc(DatabaseManagerStub(), ProjectDocument())
        old_questionnaire.xform_model = Mock(Xform)

        old_questionnaire.xform_model.equals.return_value = False
        self.assertRaises(UnsupportedXformEditException, XFormEditor().edit, new_questionnaire, old_questionnaire)

        old_questionnaire.xform_model.equals.return_value = True
        XFormEditor().edit(new_questionnaire, old_questionnaire)
