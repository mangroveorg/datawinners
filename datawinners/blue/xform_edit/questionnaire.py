class Questionnaire(object):
    def save(self, questionnaire):
        questionnaire.save(process_post_update=False)