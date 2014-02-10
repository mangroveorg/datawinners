from boto.ec2.connection import EC2Connection
import sys
import time

if len(sys.argv) < 4:
    print "Usage: python stop_instance.py instance_id aws_key aws_secret is_used"
    sys.exit(1)

instance_id = sys.argv[0]
aws_access_key = sys.argv[1]
aws_secret_key = sys.argv[2]
is_instance_used = sys.argv[3]

if is_instance_used == "0":
    print "instance is in use"
    sys.exit(0)
conn = EC2Connection(aws_access_key, aws_secret_key)
instances = conn.get_only_instances([instance_id])

if not instances or len(instances) == 0:
    print "No instance with instance-id: %s present" % instance_id
    sys.exit(1)

target_instance = instances[0]

if target_instance.state == 'stopped':
    print "Instance is already stopped!"
    sys.exit(0)

target_instance.stop()
sys.exit(0)