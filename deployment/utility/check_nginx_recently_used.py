from datetime import datetime, timedelta
import re
from subprocess import check_output
import sys

minutes = int(sys.argv[1])

last_request_log = check_output(["tail", "-1", "/var/log/nginx/datawinners.access.log"])
pattern = re.compile('.*\[(.*)\].*')
match = pattern.match(last_request_log)
date_time_stamp = match.group(1)
date_time = date_time_stamp.split(' ')[0]
last_used_datetime = datetime.strptime(date_time, '%d/%b/%Y:%H:%M:%S')
threshold_date_time = datetime.now()- timedelta(minutes=minutes)
sys.exit(1) if last_used_datetime < threshold_date_time else sys.exit(0)