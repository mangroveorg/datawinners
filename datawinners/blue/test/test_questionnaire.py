import unittest
from tempfile import NamedTemporaryFile

from mangrove.form_model.project import Project
from mock import Mock, PropertyMock

from datawinners.blue.xform_edit.questionnaire import Questionnaire


class TestQuestionnaire(unittest.TestCase):

    def test_questionnaire_save(self):
        tmp_file = Mock(NamedTemporaryFile)
        extension = ".xlsx"
        name = PropertyMock(return_value="filename" + extension)
        type(tmp_file).name = name

        project = Mock(Project)
        questionnaire = Questionnaire(tmp_file)
        questionnaire.save(project)
        project.update_media_field_flag.assert_called_once_with()
        project.save.assert_called_once_with(process_post_update=False)
        project.update_attachments.assert_called_once_with(tmp_file, 'questionnaire%s' % extension)

