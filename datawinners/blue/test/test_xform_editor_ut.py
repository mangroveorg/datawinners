import unittest

from datawinners.blue.xform_edit.submission import Submission, SubmissionSearch
from mangrove.datastore.documents import ProjectDocument
from mangrove.form_model.project import Project
from mangrove.form_model.tests.test_form_model_unit_tests import DatabaseManagerStub
from mock import Mock

import datawinners
from datawinners.blue.rules.rule import Rule
from datawinners.blue.xform_edit.questionnaire import Questionnaire
from datawinners.blue.xform_edit.validator import Validator
from datawinners.blue.xform_editor import XFormEditor, UnsupportedXformEditException


class TestXformEditor(unittest.TestCase):

    def test_should_throw_unsupported_xform_edit_exception(self):
        rule1 = Mock(Rule)

        datawinners.blue.rules.REGISTERED_RULES[:] = []
        datawinners.blue.rules.REGISTERED_RULES.extend([rule1])

        new_questionnaire = Project.new_from_doc(DatabaseManagerStub(), ProjectDocument())
        old_questionnaire = Project.new_from_doc(DatabaseManagerStub(), ProjectDocument())
        validator = Mock(Validator)
        validator.valid.return_value = False

        self.assertRaises(UnsupportedXformEditException,
                          XFormEditor(Mock(Submission), Mock(SubmissionSearch), validator, Mock(Questionnaire)).edit,
                          new_questionnaire, old_questionnaire)

    def test_should_save_questionnaire_and_update_submission_when_valid_change(self):
        rule1 = Mock(Rule)

        datawinners.blue.rules.REGISTERED_RULES[:] = []
        datawinners.blue.rules.REGISTERED_RULES.extend([rule1])

        new_questionnaire = Project.new_from_doc(DatabaseManagerStub(), ProjectDocument())
        old_questionnaire = Project.new_from_doc(DatabaseManagerStub(), ProjectDocument())
        submission = Mock(Submission)
        submission_search = Mock(SubmissionSearch)
        validator = Mock(Validator)
        questionnaire = Mock(Questionnaire)
        validator.valid.return_value = True

        XFormEditor(submission, submission_search, validator, questionnaire).edit(new_questionnaire, old_questionnaire)
        questionnaire.save.assert_called_once_with(new_questionnaire)
        submission.update_all.assert_called_once_with(new_questionnaire)
        submission_search.update_mapping.assert_called_once_with(new_questionnaire)