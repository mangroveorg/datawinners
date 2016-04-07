import os


class Questionnaire(object):

    def __init__(self, tmp_file=None, excel_raw_stream=None, file_type=None):
        self.tmp_file = tmp_file
        self.excel_raw_stream = excel_raw_stream
        self.file_type = file_type

    def save(self, questionnaire):
        questionnaire.update_media_field_flag()
        questionnaire.save(process_post_update=True)
        self._update_attachment(questionnaire)

    def _update_attachment(self, questionnaire):
        if self.excel_raw_stream is not None:
            questionnaire.update_attachments(self.excel_raw_stream, 'questionnaire.%s' %self.file_type)    
        else:
            base_name, extension = os.path.splitext(self.tmp_file.name)
            questionnaire.update_attachments(self.tmp_file, 'questionnaire%s' % extension)
