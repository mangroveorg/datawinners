from mangrove.datastore.documents import SurveyResponseDocument

from datawinners.search.submission_index_task import async_reindex


class Submission(object):
    def __init__(self, manager, dbname, rules):
        self.manager = manager
        self.dbname = dbname
        self.rules = rules

    def update_all(self, questionnaire):
        rows = self.manager.database.iterview("surveyresponse/surveyresponse", 1000, reduce=False, include_docs=False,
                                              startkey=[questionnaire.id], endkey=[questionnaire.id, {}])

        success = False
        for row in rows:
            submission = SurveyResponseDocument._wrap_row(row)
            for rule in self.rules:
                success = success or rule.update_submission(submission)
                if success:
                    submission.store(self.manager.database)

        if success:
            async_reindex.apply_async((self.dbname, questionnaire.id), countdown=5, retry=False)
