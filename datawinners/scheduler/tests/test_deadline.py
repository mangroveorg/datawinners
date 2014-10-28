# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from datetime import date
from unittest import TestCase
from mangrove.form_model.deadline import Deadline, Month, Week, NotADeadLine


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

    def test_should_return_next_deadline_date_for_current_week_for_day3(self):
        deadline = Deadline(frequency=Week(3),mode="That")
        self.assertEqual(date(2011,9,21), deadline.next(date(2011,9,19)))

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

    def test_should_return_current_deadline_date_for_this_week_for_following_deadline_for_today_before_deadline(self):
        deadline = Deadline(frequency=Week(6),mode="Following")
        self.assertEqual(date(2011,9,17), deadline.current(date(2011,9,15)))

    def test_should_return_current_deadline_date_for_this_week_for_following_deadline_for_today_after_deadline_1(self):
        deadline = Deadline(frequency=Week(2),mode="Following")
        self.assertEqual(date(2011,9,6), deadline.current(date(2011,9,9)))

    def test_should_return_current_deadline_date_for_this_week_for_following_deadline_for_today_after_deadline_2(self):
        deadline = Deadline(frequency=Week(6),mode="Following")
        self.assertEqual(date(2011,9,17), deadline.current(date(2011,9,18)))

    def test_should_return_current_deadline_date_for_this_week_for_following_deadline_for_today_on_deadline(self):
        deadline = Deadline(frequency=Week(6),mode="Following")
        self.assertEqual(date(2011,9,17), deadline.current(date(2011,9,17)))

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
        self.assertEqual(date(2011,9,17), deadline.current(date(2011,9,18)))

    def test_should_return_current_deadline_date_for_that_week_and_asof_post_deadline_day(self):
        deadline = Deadline(frequency=Week(6),mode="That")
        self.assertEqual(date(2011,9,17), deadline.current(date(2011,9,18)))

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

    def test_should_return_current_deadline_date_for_following_month_and_asof_post_deadline_day(self):
        deadline = Deadline(frequency=Month(6),mode="Following")
        self.assertEqual(date(2011,9,6), deadline.current(date(2011,9,18)))

    def test_should_return_current_deadline_date_for_that_month_and_asof_post_deadline_day(self):
        deadline = Deadline(frequency=Month(6),mode="That")
        self.assertEqual(date(2011,9,6), deadline.current(date(2011,9,18)))

    def test_should_retun_frequency_period_for_a_given_deadline_when_deadline_frequency_is_month_and_mode_is_that(self):
        deadline = Deadline(frequency=Month(6),mode="That")
        self.assertEqual((date(2011,9,1),date(2011,9,30)), deadline.get_applicable_frequency_period_for(date(2011,9,6)))

    def test_should_retun_frequency_period_for_a_given_deadline_when_deadline_frequency_is_month_and_mode_is_following(self):
        deadline = Deadline(frequency=Month(6),mode="Following")
        self.assertEqual((date(2011,8,1),date(2011,8,31)), deadline.get_applicable_frequency_period_for(date(2011,9,6)))

    def test_should_retun_frequency_period_for_a_given_deadline_when_deadline_frequency_is_month_and_mode_is_following_1(self):
        deadline = Deadline(frequency=Month(10),mode="Following")
        self.assertEqual((date(2011,8,1),date(2011,8,31)), deadline.get_applicable_frequency_period_for(date(2011,9,10)))

    def test_should_retun_frequency_period_for_a_given_deadline_when_deadline_frequency_is_month_and_mode_is_following_2(self):
        deadline = Deadline(frequency=Month(30),mode="Following")
        self.assertEqual((date(2011,7,1),date(2011,7,31)), deadline.get_applicable_frequency_period_for(date(2011,8,30)))


    def test_should_retun_frequency_period_for_a_given_deadline_when_deadline_frequency_is_week_and_mode_is_that(self):
        deadline = Deadline(frequency=Week(5),mode="That")
        self.assertEqual((date(2011,9,12),date(2011,9,18)), deadline.get_applicable_frequency_period_for(date(2011,9,16)))

    def test_should_retun_frequency_period_for_a_given_deadline_when_deadline_frequency_is_week_and_mode_is_that_1(self):
        deadline = Deadline(frequency=Week(2),mode="That")
        self.assertEqual((date(2011,9,12),date(2011,9,18)), deadline.get_applicable_frequency_period_for(date(2011,9,13)))


    def test_should_retun_frequency_period_for_a_given_deadline_when_deadline_frequency_is_week_and_mode_is_following(self):
        deadline = Deadline(frequency=Week(5),mode="Following")
        self.assertEqual((date(2011,9,5),date(2011,9,11)), deadline.get_applicable_frequency_period_for(date(2011,9,16)))


    def test_should_retun_frequency_period_for_a_given_deadline_when_deadline_frequency_is_week_and_mode_is_following_1(self):
        deadline = Deadline(frequency=Week(2),mode="Following")
        self.assertEqual((date(2011,9,5),date(2011,9,11)), deadline.get_applicable_frequency_period_for(date(2011,9,13)))

    def test_should_get_applicapable_frequency_only_if_given_date_is_a_weekly_deadline(self):
        deadline = Deadline(frequency=Week(2),mode="Following")
        self.assertRaises(  NotADeadLine , deadline.get_applicable_frequency_period_for,date(2011,9,14))

    def test_should_get_applicapable_frequency_only_if_given_date_is_a_monthly_deadline(self):
        deadline = Deadline(frequency=Month(2),mode="Following")
        self.assertRaises(  NotADeadLine , deadline.get_applicable_frequency_period_for,date(2011,9,14))

    def test_should_return_description_of_weekly_deadline_in_that_mode(self):
        deadline = Deadline(frequency=Week(1),mode="That")
        self.assertEqual('Monday of the Week',deadline.description())

    def test_should_return_description_of_weekly_deadline_in_following_mode(self):
        deadline = Deadline(frequency=Week(5),mode="Following")
        self.assertEqual('Friday of the Following Week',deadline.description())
