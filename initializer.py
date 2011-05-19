# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from datawinners.main.utils import create_views
from mangrove import initializer as mangrove_intializer


def run(manager):
    create_views(manager)
    mangrove_intializer.run(manager)
