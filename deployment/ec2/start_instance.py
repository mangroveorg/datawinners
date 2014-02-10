from boto.ec2.connection import EC2Connection

import sys

if len(sys.argv) < 3:
    print "Usage: python start_instance.py instance_id aws_key aws_secret"
    print "instance_id is the id of the instance to start up"
    sys.exit(1)

instance_id = sys.argv[0]
aws_access_key = sys.argv[1]
aws_secret_key = sys.argv[2]
conn = EC2Connection(aws_access_key, aws_secret_key)
instances = conn.get_only_instances([instance_id])
if instances:
    instances[0].start()
else:
    print "No instance with instance-id:%s present" % instance_id
    sys.exit(1)