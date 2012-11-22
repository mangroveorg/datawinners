from collections import defaultdict
from functools import partial
import os
from time import sleep
import urllib2
import jsonpickle
import sys
from find_all_db_managers import all_db_names
import logging

LOG_FOLDER = '/var/log/datawinners'
logging.basicConfig(filename=os.path.join(LOG_FOLDER, 'view_updater.log'),
                     level=logging.DEBUG, filemode='a', format='%(asctime)s - %(levelname)s: %(message)s')

def all_view_names(server, db_name):
    query_string = '_all_docs?startkey="_design"&endkey="_design0"'
    response = urllib2.urlopen('/'.join([server, db_name, query_string])).read()
    return [each['id'].split('/')[-1] for each in eval(response)['rows']]

def committed_update_seq(server, db_name):
    response = urllib2.urlopen('/'.join([server, db_name])).read()
    logging.debug(response)
    return jsonpickle.decode(response).get('committed_update_seq', 0)

def visit_view(server, db_name, view_name):
    view_url = '/'.join([server, db_name, "_design", view_name, "_view", view_name + '?reduce=false&limit=1'])
    urllib2.urlopen(view_url).read()


class ViewUpdater(object):

    def __init__(self, db_server):
        self.db_server = db_server
        self.db_names = all_db_names(db_server)
        self._seq_dict = defaultdict(int)

    def db_changes(self, db_name):
        seq = committed_update_seq(db_server, db_name)
        changes = seq - self._seq_dict[db_name]
        return changes

    def trigger(self, threshold):
        logging.debug("get %s dbs" % len(self.db_names))
        try:
            for db_name in self.db_names:
                self._try_to_update(db_name, threshold)
        except Exception, e:
            logging.error(e)

    def _try_to_update(self, db_name, threshold):
        changes = self.db_changes(db_name)
        if changes > threshold:
            logging.info("%-80s%s" % (db_name, "U P D A T I N G................"))
            self._update_db(db_name)
            self._seq_dict[db_name] += changes
            sleep(5)
        else:
            logging.info("%-80s%s" % (db_name, "P O S T P O N E D"))

    def _update_db(self, db_name):
        view_names = all_view_names(self.db_server, db_name)
        for each in view_names:
            try:
                visit_view(self.db_server, db_name, each)
                logging.info("%-80s%s" % (each, "U P D A T E D."))
            except:
                logging.info("%-80s%s" % (each, "FAILED."))

def pid_is_running(pid):
    try:
        os.kill(pid, 0)
        return pid
    except OSError:
        return

def write_pidfile_or_die(pid_file):
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
    updater = ViewUpdater(db_server)
    task = partial(updater.trigger, 100)
    while True:
        task()
        sleep(60 * 60 * 2)

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

    write_pidfile_or_die('/tmp/view_updater.pid')
    main()




