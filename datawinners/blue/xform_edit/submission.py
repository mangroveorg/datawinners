from mangrove.datastore.documents import SurveyResponseDocument

from datawinners.blue.rules import REGISTERED_RULES
from datawinners.search.submission_index import SubmissionSearchStore


class Submission(object):
    def __init__(self, manager):
        self.manager = manager

    def update_all(self, questionnaire):
        start_key = [questionnaire.id]
        end_key = [questionnaire.id, {}]
        rows = self.manager.database.iterview("surveyresponse/surveyresponse", 1000, reduce=False, include_docs=False, startkey=start_key, endkey=end_key)

        success = False
        for row in rows:
            submission = SurveyResponseDocument._wrap_row(row)
            for rule in REGISTERED_RULES:
                success = success or rule.update_submission(submission)
            # TODO: save submission

        if success:
            # TODO: reindex elasticsearch
            pass


class SubmissionSearch(object):
    def __init__(self, manager):
        self.manager = manager

    def update_mapping(self, questionnaire):
        change_mapping = False
        for rule in REGISTERED_RULES:
            change_mapping = change_mapping or rule.change_mapping()

        if change_mapping:
            SubmissionSearchStore(self.manager, questionnaire, None).recreate_elastic_store()
