from datawinners.accountmanagement.helper import is_org_user


def submission_stats(dbm, form_model_id):

    rows = dbm.load_all_rows_in_view('undeleted_survey_response', startkey=[form_model_id], endkey=[form_model_id, {}],
                                     group=True, group_level=1, reduce=True)
    submission_success,submission_errors = 0, 0
    for row in rows:
        submission_success = row["value"]["success"]
        submission_errors = row["value"]["count"] - row["value"]["success"]
    return submission_success,submission_errors
