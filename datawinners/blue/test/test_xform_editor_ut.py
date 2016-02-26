import unittest

import mock
from mangrove.datastore.documents import ProjectDocument
from mangrove.form_model.project import Project
from mangrove.form_model.tests.test_form_model_unit_tests import DatabaseManagerStub
from mock import Mock

import datawinners
from datawinners.blue.rules.rule import Rule
from datawinners.blue.xform_editor import XFormEditor, UnsupportedXformEditException


class TestEditLabelRule(unittest.TestCase):

    def test_should_validate_xform_change(self):
        def rule1_stub(old, new):
            old.xform = "<text>This is jar bharath. I'm pairing with Ramanathan</text>"

        def rule2_stub(old, new):
            old.xform = "<text>This is jar bharath. I'm pairing with Sairam</text>"

        rule1 = Mock(Rule)
        rule2 = Mock(Rule)
        rule1.update_xform = rule1_stub
        datawinners.blue.rules.REGISTERED_RULES[:] = []
        datawinners.blue.rules.REGISTERED_RULES.extend([rule1, rule2])

        editor = XFormEditor()
        old_doc = ProjectDocument()
        old_doc.xform = "<text>This is raj bharath. I'm pairing with Ramanathan</text>"
        new_doc = ProjectDocument()
        new_doc.xform = "<text>This is jar bharath. I'm pairing with Sairam</text>"
        old_questionnaire = Project.new_from_doc(DatabaseManagerStub(), old_doc)
        new_questionnaire = Project.new_from_doc(DatabaseManagerStub(), new_doc)
        self.assertFalse(editor._validate(new_questionnaire, old_questionnaire))

        rule2.update_xform = rule2_stub
        self.assertTrue(editor._validate(new_questionnaire, old_questionnaire))

    def test_should_throw_unsupported_xform_edit_exception(self):
        rule1 = Mock(Rule)
        datawinners.blue.rules.REGISTERED_RULES[:] = []
        datawinners.blue.rules.REGISTERED_RULES.extend([rule1])
        editor = XFormEditor()
        old_doc = ProjectDocument()
        old_doc.xform = "<text>This is raj bharath. I'm pairing with Ramanathan</text>"
        new_doc = ProjectDocument()
        new_doc.xform = "<text>This is jar bharath. I'm pairing with Sairam</text>"
        old_questionnaire = Project.new_from_doc(DatabaseManagerStub(), old_doc)
        new_questionnaire = Project.new_from_doc(DatabaseManagerStub(), new_doc)
        self.assertRaises(UnsupportedXformEditException, editor.edit, new_questionnaire, old_questionnaire)
