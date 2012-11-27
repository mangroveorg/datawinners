from boto.ec2.connection import EC2Connection

from datetime import datetime
import sys

# Substitute your access key and secret key here
aws_access_key = 'AKIAI763UW5YW37B4UIQ'
aws_secret_key = 'E1KijH+j2zczrFeoXVB+EI1m/GB60EB0S9ufM8pi'

if len(sys.argv) < 3:
    print "Usage: python create_snapshots.py volume_id number_of_snapshots_to_keep description"
    print "volume id and number of snapshots to keep are required. description is optional"
    sys.exit(1)

vol_id = sys.argv[1]
keep = int(sys.argv[2])
conn = EC2Connection(aws_access_key, aws_secret_key)
volumes = conn.get_all_volumes([vol_id])
print "%s" % repr(volumes)
volume = volumes[0]
description = 'Created by manage_snapshots.py at ' + datetime.today().isoformat(' ')
if len(sys.argv) > 3:
    description = sys.argv[3]

if volume.create_snapshot(description):
    print 'Snapshot created with description: ' + description

snapshots = volume.snapshots()
snapshot = snapshots[0]

def date_compare(snap1, snap2):
    if snap1.start_time < snap2.start_time:
        return -1
    elif snap1.start_time == snap2.start_time:
        return 0
    return 1

snapshots.sort(date_compare)
delta = len(snapshots) - keep
for i in range(delta):
    print 'Deleting snapshot ' + snapshots[i].description
    snapshots[i].delete()