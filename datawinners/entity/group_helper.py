from mangrove.datastore.group import Group


def get_group_details(dbm):
    group_details = []
    rows = dbm.load_all_rows_in_view('group_by_name')
    for row in rows:
        group_details.append({'name': row['value']['name']})
    return group_details


def create_new_group(dbm, group_name):
    new_group = Group(dbm, group_name)
    new_group.save()