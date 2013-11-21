

def submission_stats(dbm, form_code):

    rows = dbm.load_all_rows_in_view('undeleted_survey_response', startkey=[form_code], endkey=[form_code, {}],
                                     group=True, group_level=1, reduce=True)
    submission_success,submission_errors = 0, 0
    for row in rows:
        submission_success = row["value"]["success"]
        submission_errors = row["value"]["count"] - row["value"]["success"]
    return submission_success,submission_errors