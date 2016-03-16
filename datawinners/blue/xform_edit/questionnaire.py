import os


class Questionnaire(object):

    def __init__(self, tmp_file):
        self.tmp_file = tmp_file

    def save(self, questionnaire):
        questionnaire.update_media_field_flag()
        questionnaire.save(process_post_update=True)
        self._update_attachment(questionnaire)

    def _update_attachment(self, questionnaire):
        base_name, extension = os.path.splitext(self.tmp_file.name)
        questionnaire.update_attachments(self.tmp_file, 'questionnaire%s' % extension)
