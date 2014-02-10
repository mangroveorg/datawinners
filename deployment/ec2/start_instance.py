from boto.ec2.connection import EC2Connection
import sys
import time

if len(sys.argv) < 4:
    print "Usage: python start_instance.py instance_id aws_key aws_secret elastic_ip"
    sys.exit(1)

instance_id = sys.argv[0]
aws_access_key = sys.argv[1]
aws_secret_key = sys.argv[2]
elastic_ip = sys.argv[3]

conn = EC2Connection(aws_access_key, aws_secret_key)
instances = conn.get_only_instances([instance_id])

if not instances or len(instances) == 0:
    print "No instance with instance-id: %s present" % instance_id
    sys.exit(1)

target_instance = instances[0]

if target_instance.state == 'running':
    print "Instance is already running!"
    sys.exit(0)

target_instance.start()

while target_instance.state != 'running':
    print "Current instance state: %s" % target_instance.state
    if target_instance.state not in ['pending', 'running']:
        print "Instance transition state not expected..aborting!"
        sys.exit(1)
    time.sleep(1)
    target_instance.update()

elastic_ip_assign_successful = target_instance.use_ip(elastic_ip)
print "Status of ip_assignment: %s" % elastic_ip_assign_successful

if not elastic_ip_assign_successful:
    print "Assignment of elastic-ip failed"
    sys.exit(1)

sys.exit(0)