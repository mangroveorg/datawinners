# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from datetime import date
from unittest import TestCase
from datawinners.scheduler.deadline import Deadline, Month, Week

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

    def test_should_return_next_deadline_date_for_following_month(self):
        deadline = Deadline(frequency=Month(24),mode="Following")
        self.assertEqual(date(2011,10,24), deadline.next(date(2011,9,15)))

    def test_should_return_next_deadline_date_for_following_month_when_current_month_is_december(self):
        deadline = Deadline(frequency=Month(24),mode="Following")
        self.assertEqual(date(2014,1,24), deadline.next(date(2013,12,15)))

    def test_should_return_next_deadline_date_for_following_month_with_asof_as_deadline_day(self):
        deadline = Deadline(frequency=Month(24),mode="Following")
        self.assertEqual(date(2011,10,24), deadline.next(date(2011,9,24)))

    def test_should_return_next_deadline_date_for_following_month_with_asof_after_deadline_day(self):
        deadline = Deadline(frequency=Month(24),mode="Following")
        self.assertEqual(date(2011,10,24), deadline.next(date(2011,9,28)))

    def test_should_return_next_deadline_date_for_current_week(self):
        deadline = Deadline(frequency=Week(6),mode="That")
        self.assertEqual(date(2011,9,17), deadline.next(date(2011,9,15)))

    def test_should_return_next_deadline_date_for_current_week_and_asof_as_deadline_day(self):
        deadline = Deadline(frequency=Week(6),mode="That")
        self.assertEqual(date(2011,9,17), deadline.next(date(2011,9,17)))

    def test_should_return_next_deadline_date_for_current_week_and_asof_post_deadline_day(self):
        deadline = Deadline(frequency=Week(6),mode="That")
        self.assertEqual(None, deadline.next(date(2011,9,18)))

    def test_should_return_next_deadline_date_for_following_week(self):
        deadline = Deadline(frequency=Week(6),mode="Following")
        self.assertEqual(date(2011,9,24), deadline.next(date(2011,9,15)))

    def test_should_return_next_deadline_date_for_following_week_and_asof_as_deadline_day(self):
        deadline = Deadline(frequency=Week(6),mode="Following")
        self.assertEqual(date(2011,9,24), deadline.next(date(2011,9,17)))

    def test_should_return_next_deadline_date_for_following_week_and_asof_post_deadline_day(self):
        deadline = Deadline(frequency=Week(6),mode="Following")
        self.assertEqual(date(2011,9,24), deadline.next(date(2011,9,18)))

    def test_should_return_current_deadline_date_for_this_week_for_following_deadline(self):
        deadline = Deadline(frequency=Week(6),mode="Following")
        self.assertEqual(date(2011,9,17), deadline.current(date(2011,9,15)))

    def test_should_return_current_deadline_date_for_this_week_for_that_deadline(self):
        deadline = Deadline(frequency=Week(6),mode="That")
        self.assertEqual(date(2011,9,17), deadline.current(date(2011,9,15)))

    def test_should_return_current_deadline_date_for_this_week_for_that_deadline_for_day3_for_deadline_on_same_day(self):
        deadline = Deadline(frequency=Week(3),mode="That")
        self.assertEqual(date(2011,9,21), deadline.current(date(2011,9,21)))

    def test_should_return_current_deadline_date_for_this_week_for_that_deadline_for_day3_for_deadline_on_different_day(self):
        deadline = Deadline(frequency=Week(3),mode="That")
        self.assertEqual(date(2011,9,21), deadline.current(date(2011,9,19)))


    def test_should_return_current_deadline_date_for_following_week_and_asof_as_deadline_day(self):
        deadline = Deadline(frequency=Week(6),mode="Following")
        self.assertEqual(date(2011,9,17), deadline.current(date(2011,9,17)))

    def test_should_return_current_deadline_date_for_that_week_and_asof_as_deadline_day(self):
        deadline = Deadline(frequency=Week(6),mode="That")
        self.assertEqual(date(2011,9,17), deadline.current(date(2011,9,17)))

    def test_should_return_current_deadline_date_for_following_week_and_asof_post_deadline_day(self):
        deadline = Deadline(frequency=Week(6),mode="Following")
        self.assertEqual(None, deadline.current(date(2011,9,18)))

    def test_should_return_current_deadline_date_for_that_week_and_asof_post_deadline_day(self):
        deadline = Deadline(frequency=Week(6),mode="That")
        self.assertEqual(None, deadline.current(date(2011,9,18)))

    def test_should_return_current_deadline_date_for_this_month_for_following_deadline(self):
        deadline = Deadline(frequency=Month(6),mode="Following")
        self.assertEqual(date(2011,9,6), deadline.current(date(2011,9,5)))

    def test_should_return_current_deadline_date_for_this_month_for_that_deadline(self):
        deadline = Deadline(frequency=Month(6),mode="That")
        self.assertEqual(date(2011,9,6), deadline.current(date(2011,9,5)))

    def test_should_return_current_deadline_date_for_following_month_and_asof_as_deadline_day(self):
        deadline = Deadline(frequency=Month(6),mode="Following")
        self.assertEqual(date(2011,9,6), deadline.current(date(2011,9,6)))

    def test_should_return_current_deadline_date_for_that_month_and_asof_as_deadline_day(self):
        deadline = Deadline(frequency=Month(6),mode="That")
        self.assertEqual(date(2011,9,6), deadline.current(date(2011,9,6)))

    def test_should_return_current_deadline_date_for_following_week_and_asof_post_deadline_day(self):
        deadline = Deadline(frequency=Month(6),mode="Following")
        self.assertEqual(None, deadline.current(date(2011,9,18)))

    def test_should_return_current_deadline_date_for_that_week_and_asof_post_deadline_day(self):
        deadline = Deadline(frequency=Month(6),mode="That")
        self.assertEqual(None, deadline.current(date(2011,9,18)))


