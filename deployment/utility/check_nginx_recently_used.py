from datetime import datetime, timedelta
import re
from subprocess import check_output
import sys

output = check_output(["tail", "-1", "/var/log/nginx/datawinners.access.log"])
pattern = re.compile('.*\[(.*)\].*')
match = pattern.match(output)
time_stamp = match.group(1)
time = time_stamp.split(' ')[0]
logged_date = datetime.strptime(time, '%d/%b/%Y:%H:%M:%S')
current_time = datetime.now()- timedelta(minutes=10)
sys.exit(1) if logged_date < current_time else sys.exit(0)