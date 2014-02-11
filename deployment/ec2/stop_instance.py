from boto.ec2.connection import EC2Connection
import sys
import time

if len(sys.argv) < 3:
    print "Usage: python stop_instance.py instance_id aws_key aws_secret"
    sys.exit(1)

instance_id = sys.argv[1]
aws_access_key = sys.argv[2]
aws_secret_key = sys.argv[3]

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