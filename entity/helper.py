# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import re
from mangrove.errors.MangroveException import NumberNotRegisteredException
from mangrove.transport.reporter import  find_reporter_entity
from django.utils.encoding import smart_unicode

def remove_hyphens(telephone_number):
    return re.sub('[- \(\)+]', '', smart_unicode(telephone_number))

def unique(dbm, telephone_number):
    telephone_number = remove_hyphens(telephone_number)
    try:
        find_reporter_entity(dbm, telephone_number)
    except NumberNotRegisteredException:
        return True
    return False
