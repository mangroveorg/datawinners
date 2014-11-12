

def get_all_projects_for_datasender(dbm, data_sender_id):
    rows = dbm.load_all_rows_in_view('projects_by_datasenders', key=data_sender_id, include_docs=True)
    return rows


def get_all_projects(dbm, data_sender_id=None):
    if data_sender_id:
        rows = dbm.load_all_rows_in_view('projects_by_datasenders', startkey=data_sender_id, endkey=data_sender_id,
                                         include_docs=True)
        for row in rows:
            row.update({'value': row["doc"]})
        return rows
    return dbm.load_all_rows_in_view('all_projects')