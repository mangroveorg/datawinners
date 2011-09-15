# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from datetime import datetime, date
from unittest2 import TestCase

class Deadline(object):
    def __init__(self,frequency,mode):
        self.frequency = frequency
        self.mode = mode

    def next(self, as_of):
        return self.frequency.next_date(as_of)


class Month(object):
    def __init__(self,day):
        self.day = day

    def next_date(self, as_of):
        if as_of.day > self.day:
            return None
        return date(as_of.year, as_of.month, self.day)
#        assert day in range 1-31
#        test case for feb or day = 31


class TestDeadline(TestCase):
    def test_should_return_next_deadline_date_for_current_month(self):
        deadline = Deadline(frequency=Month(24),mode="That")
        self.assertEqual(date(2011,9,24), deadline.next(date(2011,9,15)))

    def test_should_return_next_deadline_date_for_current_month_and_asof_as_deadline_day(self):
        deadline = Deadline(frequency=Month(24),mode="That")
        self.assertEqual(date(2011,9,24), deadline.next(date(2011,9,24)))

    def test_should_return_next_deadline_date_for_current_month_and_asof_post_deadline_day(self):
        deadline = Deadline(frequency=Month(24),mode="That")
        self.assertEqual(None, deadline.next(date(2011,9,30)))

    
