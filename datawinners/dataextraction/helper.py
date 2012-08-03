def get_data_by_subject(dbm, subject_type, subject_id):
    rows = dbm.load_all_rows_in_view('by_entity_type_and_entity_id', startkey=[[subject_type], subject_id],
                                      endkey=[[subject_type], subject_id, {}])
    return [row["value"] for row in rows]