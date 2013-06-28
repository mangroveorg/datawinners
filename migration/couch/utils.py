import csv
import logging
from apscheduler.threadpool import ThreadPool
import requests
from datawinners import  settings

skip_dbs = []
completed_dbs_csv_file_name = ''
completed_dbs_csv_file = None
username = settings.COUCHDBMAIN_USERNAME
password = settings.COUCHDBMAIN_PASSWORD

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


def all_db_names(server=settings.COUCH_DB_SERVER):
    all_dbs = requests.get(server + "/_all_dbs", auth=settings.COUCHDBMAIN_CREDENTIALS)
    return filter(lambda x: x.startswith('hni_'), all_dbs.json())



class DWThreadPool(ThreadPool):
    def submit(self, func, *args, **kwargs):
        def callback_wrapper(*args, **kwargs):
            try:
            #logging.info("Invoking " + str(func) + ":" + str(args))
                func(*args, **kwargs)
            except Exception as e:
                logging.exception(e.message)
            self._queue.task_done()
        return super(DWThreadPool, self).submit(callback_wrapper, *args, **kwargs)

    def wait_for_completion(self):
        self._queue.join()

