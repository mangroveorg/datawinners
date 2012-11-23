from collections import defaultdict
from functools import partial
import cPickle
import os
from time import sleep
import urllib2
import jsonpickle
import sys
from find_all_db_managers import all_db_names
import logging

THRESHOLD = 100
INTERVAL = 60 * 60 * 1

LOG_FOLDER = '/var/log/datawinners'
logging.basicConfig(filename=os.path.join(LOG_FOLDER, 'view_updater.log'),
                     level=logging.DEBUG, filemode='a', format='%(asctime)s - %(levelname)s: %(message)s')

def all_view_names(server, db_name):
    query_string = '_all_docs?startkey="_design"&endkey="_design0"'
    response = urllib2.urlopen('/'.join([server, db_name, query_string])).read()
    return [each['id'].split('/')[-1] for each in eval(response)['rows']]

def committed_update_seq(server, db_name):
    response = urllib2.urlopen('/'.join([server, db_name])).read()
    logging.debug(response.strip())
    return jsonpickle.decode(response).get('committed_update_seq', 0)

def visit_view(server, db_name, view_name):
    view_url = '/'.join([server, db_name, "_design", view_name, "_view", view_name + '?reduce=false&limit=0'])
    urllib2.urlopen(view_url).read()


class ViewUpdater(object):
    def __init__(self, db_server):
        self.db_server = db_server
        self._status_file_path = os.path.join(LOG_FOLDER, "view_updater.seq")
        self._init_seq_dict()
        self._skipped_views = ["by_geo",
                            "by_aggregation_path",
                            "by_form_code_time",
                            "by_label_value",
                            "by_values",
                            "by_values_latest",
                            "by_values_latest_by_time",
                            "daily_aggregate_latest",
                            "daily_aggregate_stats",
                            "data_record_by_form_code",
                            "entity_by_label_value",
                            "entity_data",
                            "entity_datatypes",
                            "entity_datatypes_by_tag",
                            "id_time_slug_value",
                            "monthly_aggregate_latest",
                            "monthly_aggregate_stats",
                            "weekly_aggregate_latest",
                            "weekly_aggregate_stats",
                            "yearly_aggregate_latest",
                            "yearly_aggregate_stats"]

    def _init_seq_dict(self):
        if os.path.exists(self._status_file_path):
            logging.debug("Load sequence from file.")
            with open(self._status_file_path, 'rb') as f:
                self._seq_dict = cPickle.load(f)
        else:
            self._seq_dict = defaultdict(int)

    def db_changes(self, db_name):
        logging.debug("Previous update sequence is: %s" % self._seq_dict[db_name])
        seq = committed_update_seq(db_server, db_name)
        changes = seq - self._seq_dict[db_name]
        return changes

    def trigger(self, threshold):
        self.db_names = all_db_names(db_server)
        logging.debug("get %s dbs" % len(self.db_names))
        for db_name in self.db_names:
            self._try_to_update(db_name, threshold)
            logging.info("*"*80)

    def _try_to_update(self, db_name, threshold):
        try:
            changes = self.db_changes(db_name)
            if changes > threshold:
                logging.info("%-80s%s" % (db_name, "U P D A T I N G................"))
                self._update_db(db_name)
                self._seq_dict[db_name] += changes
                self.save_db_update_status()
                sleep(5)
            else:
                logging.info("%-80s%s" % (db_name, "P O S T P O N E D"))
        except Exception, e:
            logging.error(e)

    def save_db_update_status(self):
        with open(self._status_file_path, 'wb') as f:
            cPickle.dump(self._seq_dict, f)

    def _update_db(self, db_name):
        view_names = all_view_names(self.db_server, db_name)
        for each in view_names:
            if each in self._skipped_views:
                logging.info("%-80s%s" % (each, "SKIPPED."))
                continue

            try:
                visit_view(self.db_server, db_name, each)
                logging.info("%-80s%s" % (each, "U P D A T E D."))
            except Exception, e:
                logging.error("%-80s%s" % (each, "FAILED."))
                logging.error(e)

def pid_is_running(pid):
    try:
        os.kill(pid, 0)
        return pid
    except OSError:
        return

def write_pid_file_or_die(pid_file):
    if os.path.exists(pid_file):
        pid = int(open(pid_file).read())
        if pid_is_running(pid):
            print("Process {0} is still running.".format(pid))
            raise SystemExit
        else:
            os.remove(pid_file)

    open(pid_file, 'w').write(str(os.getpid()))
    return pid_file

def main():
    logging.debug(db_server)
    updater = ViewUpdater(db_server)
    task = partial(updater.trigger, THRESHOLD)
    while True:
        try:
            task()
            logging.info("="*80)
            logging.info("All views updated")
            logging.info("="*80)

            sleep(INTERVAL)
        except Exception, e:
            logging.error(e)

db_server = "http://localhost:5984"
if __name__ == '__main__':
    if len(sys.argv) > 1:
        db_server = "http://%s:5984" % sys.argv[1]
    try:
        pid = os.fork()
        if pid > 0: sys.exit(0)
    except OSError, e:
        print >>sys.stderr, "fork #1 failed: %d (%s)" % (e.errno, e.strerror)
        sys.exit(1)

    write_pid_file_or_die('/tmp/view_updater.pid')
    main()




