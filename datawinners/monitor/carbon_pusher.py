import datetime
import socket
from django.conf import settings

def send_to_carbon(metric_path, value):
    if not settings.GRAPHITE_MONITORING_ENABLED:
        return

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    message = "%s %d %s\n" % (metric_path, value, datetime.datetime.now().strftime('%s'))
    sock.sendto(message, (settings.CARBON_HOST, settings.CARBON_PORT))