from mangrove.transport.submissions import  SUCCESS_SUBMISSION_LOG_VIEW_NAME, UNDELETED_SUBMISSION_LOG_VIEW_NAME, DELETED_SUBMISSION_LOG_VIEW_NAME, get_submissions

def successful_submissions(dbm, form_code):
    return get_submissions(dbm, form_code, None, None, view_name=SUCCESS_SUBMISSION_LOG_VIEW_NAME)


def undeleted_submissions(dbm, form_code):
    return get_submissions(dbm, form_code, None, None, view_name=UNDELETED_SUBMISSION_LOG_VIEW_NAME)


def deleted_submissions(dbm, form_code, from_time=None, to_time=None, page_number=0, page_size=None):
    return get_submissions(dbm, form_code, from_time, to_time, page_number, page_size, DELETED_SUBMISSION_LOG_VIEW_NAME)


class SubmissionRouter(object):
    ALL = "all"
    SUCCESS = "success"
    ERROR = "error"
    DELETED = "deleted"

    SUBMISSION_ROUTER = {
        ALL: undeleted_submissions,
        SUCCESS: successful_submissions,
        ERROR: undeleted_submissions,
        DELETED: deleted_submissions
    }

    def route(self, type):
        return self.SUBMISSION_ROUTER.get(type, undeleted_submissions)

