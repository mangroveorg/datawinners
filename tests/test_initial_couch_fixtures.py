# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import unittest
from datawinners.main.management.commands import recreatedb

class TestInitialCouchFixtures(unittest.TestCase):

    def test_should_load_data(self):
        command = recreatedb.Command()
        command.handle()
