from mangrove.datastore.documents import SurveyResponseDocument

from datawinners.blue.rules import REGISTERED_RULES
from datawinners.search.submission_index_task import async_reindex


class Submission(object):
    def __init__(self, manager, dbname):
        self.manager = manager
        self.dbname = dbname

    def update_all(self, questionnaire):
        start_key = [questionnaire.id]
        end_key = [questionnaire.id, {}]
        rows = self.manager.database.iterview("surveyresponse/surveyresponse", 1000, reduce=False, include_docs=False, startkey=start_key, endkey=end_key)

        success = False
        for row in rows:
            submission = SurveyResponseDocument._wrap_row(row)
            for rule in REGISTERED_RULES:
                success = success or rule.update_submission(submission)
                if success:
                    submission.store(self.manager.database)

        if success:
            async_reindex.apply_async((self.dbname, questionnaire.id), countdown=5, retry=False)
