import csv

skip_dbs = []
completed_dbs_csv_file_name = ''
completed_dbs_csv_file = None

def init_migrations(completed_dbs_csv):
    global completed_dbs_csv_file_name
    global completed_dbs_csv_file
    global skip_dbs
    completed_dbs_csv_file_name = completed_dbs_csv
    completed_dbs_csv_file = open(completed_dbs_csv_file_name, 'a')
    set_skip_dbs()

def mark_start_of_migration(db_name):
    completed_dbs_csv_file.writelines('%s\n' % db_name)

def set_skip_dbs():
    progress_file = open(completed_dbs_csv_file_name, 'r')
    reader = csv.reader(progress_file, delimiter=',')
    for row in reader:
        skip_dbs.extend(row)

def should_not_skip(db_name):
    return not skip_dbs.__contains__(db_name)



