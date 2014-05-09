import csv
import logging
from apscheduler.threadpool import ThreadPool
from datawinners import settings

skip_dbs = []
completed_dbs_csv_file_name = ''
completed_dbs_csv_file = None
username = settings.COUCHDBMAIN_USERNAME
password = settings.COUCHDBMAIN_PASSWORD


def configure_csv(completed_dbs_csv):
    global completed_dbs_csv_file_name
    global completed_dbs_csv_file
    global skip_dbs
    completed_dbs_csv_file_name = completed_dbs_csv
    completed_dbs_csv_file = open(completed_dbs_csv_file_name, 'a')
    set_skip_dbs()


def mark_as_completed(db_name):
    completed_dbs_csv_file.writelines('%s\n' % db_name)
    completed_dbs_csv_file.flush()


def set_skip_dbs():
    progress_file = open(completed_dbs_csv_file_name, 'r')
    reader = csv.reader(progress_file, delimiter=',')
    for row in reader:
        skip_dbs.extend(row)


def should_not_skip(db_name):
    return not skip_dbs.__contains__(db_name)


def migration_tag(version): # version = (7,0,1)
    return str(version[0]) + "_" + str(version[1]) + "_" + str(version[2])


def configure_logging(version):
    version_tag = migration_tag(version)
    logging.basicConfig(filename='/var/log/datawinners/migration_release_' + version_tag + '.log', level=logging.DEBUG,
                        format="%(asctime)s | %(thread)d | %(levelname)s | %(name)s | %(message)s")


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


def migrate(all_db_names, callback_function, version, threads=7):
    configure_csv('/var/log/datawinners/dbs_migrated_release_' + migration_tag(version) + '.csv')
    configure_logging(version)

    pool = DWThreadPool(threads, threads)
    for db_name in all_db_names:
        if should_not_skip(db_name):
            pool.submit(callback_function, db_name)

    pool.wait_for_completion()
    print "Completed!"
