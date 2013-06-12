from boto.ec2.connection import EC2Connection

from datetime import datetime
import sys

if len(sys.argv) < 5:
    print "Usage: python create_snapshots.py volume_id number_of_snapshots_to_keep aws_key aws_secret description"
    print "volume id and number of snapshots to keep are required. description is optional"
    sys.exit(1)

vol_id = sys.argv[1]
keep = int(sys.argv[2])
aws_access_key = sys.argv[3]
aws_secret_key = sys.argv[4]
conn = EC2Connection(aws_access_key, aws_secret_key)
volumes = conn.get_all_volumes([vol_id])
print "%s" % repr(volumes)
volume = volumes[0]
description = 'Created automatically at ' + datetime.today().isoformat(' ')
if len(sys.argv) > 5:
    description = sys.argv[5]

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
snapshots = [s for s in snapshots if s.description.index("Created automatically at ") == 0]
delta = len(snapshots) - keep
for i in range(delta):
    print 'Deleting snapshot ' + snapshots[i].description
    snapshots[i].delete()