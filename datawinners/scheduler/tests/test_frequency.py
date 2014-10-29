# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from datetime import date
from unittest import TestCase
from mangrove.form_model.deadline import Week, Month, Quarter


class TestQuarterlyFrequency(TestCase):
    def test_should_return_current_deadline_for_quarterly_frequency_for_date_before_deadline(self):
        quarter = Quarter(3,20)
        self.assertEqual(date(2010,12,20) ,quarter.current_deadline_date(date(2011,3,10)))

    def test_should_return_current_deadline_for_quarterly_frequency_for_date_on_deadline(self):
        quarter = Quarter(3,20)
        self.assertEqual(date(2011,3,20) ,quarter.current_deadline_date(date(2011,3,20)))

    def test_should_return_current_deadline_for_quarterly_frequency_for_date_after_deadline(self):
        quarter = Quarter(3,20)
        self.assertEqual(date(2011,3,20) ,quarter.current_deadline_date(date(2011,3,28)))

    def test_should_return_next_deadline_for_quarterly_frequency_for_date_before_deadline(self):
        quarter = Quarter(3,20)
        self.assertEqual(date(2011,3,20) ,quarter.next_deadline_date(date(2011,3,10)))

    def test_should_return_next_deadline_for_quarterly_frequency_for_date_on_deadline(self):
        quarter = Quarter(3,20)
        self.assertEqual(date(2011,6,20) ,quarter.next_deadline_date(date(2011,3,20)))

    def test_should_return_next_deadline_for_quarterly_frequency_for_date_after_deadline(self):
        quarter = Quarter(3,20)
        self.assertEqual(date(2011,6,20) ,quarter.next_deadline_date(date(2011,3,28)))

class TestWeeklyFrequency(TestCase):
    def test_should_return_current_deadline_for_weekly_frequency_for_date_before_deadline(self):
        week = Week(3)
        self.assertEqual(date(2011,8,31) ,week.current_deadline_date(date(2011,9,5)))

    def test_should_return_current_deadline_for_weekly_frequency_for_date_on_deadline(self):
        week = Week(3)
        self.assertEqual(date(2011,9,7) ,week.current_deadline_date(date(2011,9,7)))

    def test_should_return_current_deadline_for_weekly_frequency_for_date_after_deadline(self):
        week = Week(3)
        self.assertEqual(date(2011,9,7) ,week.current_deadline_date(date(2011,9,9)))

    def test_should_return_next_deadline_for_weekly_frequency_for_date_before_deadline(self):
        week = Week(3)
        self.assertEqual(date(2011,9,7) ,week.next_deadline_date(date(2011,9,5)))

    def test_should_return_next_deadline_for_weekly_frequency_for_date_on_deadline(self):
        week = Week(3)
        self.assertEqual(date(2011,9,14) ,week.next_deadline_date(date(2011,9,7)))

    def test_should_return_next_deadline_for_weekly_frequency_for_date_after_deadline(self):
        week = Week(3)
        self.assertEqual(date(2011,9,14) ,week.next_deadline_date(date(2011,9,9)))

class TestMonthlyFrequency(TestCase):
    def test_should_return_current_deadline_for_monthly_frequency_for_date_before_deadline(self):
        month = Month(3)
        self.assertEqual(date(2011,8,3) ,month.current_deadline_date(date(2011,9,1)))

    def test_should_return_current_deadline_for_monthly_frequency_for_date_on_deadline(self):
        month = Month(3)
        self.assertEqual(date(2011,9,3) ,month.current_deadline_date(date(2011,9,3)))

    def test_should_return_current_deadline_for_monthly_frequency_for_date_after_deadline(self):
        month = Month(3)
        self.assertEqual(date(2011,9,3) ,month.current_deadline_date(date(2011,9,9)))

    def test_should_return_next_deadline_for_monthly_frequency_for_date_before_deadline(self):
        month = Month(3)
        self.assertEqual(date(2011,9,3) ,month.next_deadline_date(date(2011,9,1)))

    def test_should_return_next_deadline_for_monthly_frequency_for_date_on_deadline(self):
        month = Month(3)
        self.assertEqual(date(2011,10,3) ,month.next_deadline_date(date(2011,9,3)))

    def test_should_return_next_deadline_for_monthly_frequency_for_date_after_deadline(self):
        month = Month(3)
        self.assertEqual(date(2011,10,3) ,month.next_deadline_date(date(2011,9,9)))

    #    next deadline with day 31
    def test_should_return_next_deadline_for_monthly_frequency_for_date_on_deadline_for_day31(self):
        month = Month(31)
        self.assertEqual(date(2011,10,31) ,month.next_deadline_date(date(2011,10,3)))

    def test_should_return_next_deadline_for_monthly_frequency_for_date_on_deadline_for_day31_for_asof_with_30_days(self):
        month = Month(31)
        self.assertEqual(date(2011,9,30) ,month.next_deadline_date(date(2011,9,3)))

    def test_should_return_next_deadline_for_monthly_frequency_for_date_on_deadline_for_day31_for_asof_with_30_days_on_last_day_of_month(self):
        month = Month(31)
        self.assertEqual(date(2011,10,31) ,month.next_deadline_date(date(2011,9,30)))

    def test_should_return_next_deadline_for_monthly_frequency_for_date_on_deadline_for_day31_for_feb_with_28_days(self):
        month = Month(31)
        self.assertEqual(date(2011,2,28) ,month.next_deadline_date(date(2011,2,3)))

    def test_should_return_next_deadline_for_monthly_frequency_for_date_on_deadline_for_day31_for_feb_with_29_days(self):
        month = Month(31)
        self.assertEqual(date(2012,2,29) ,month.next_deadline_date(date(2012,2,3)))

    #    current deadline with day 31
    def test_should_return_current_deadline_for_monthly_frequency_for_date_on_deadline_for_day31(self):
        month = Month(31)
        self.assertEqual(date(2011,9,30) ,month.current_deadline_date(date(2011,10,3)))

    def test_should_return_current_deadline_for_monthly_frequency_for_date_on_deadline_for_day31_for_asof_with_30_days(self):
        month = Month(31)
        self.assertEqual(date(2011,8,31) ,month.current_deadline_date(date(2011,9,3)))

    def test_should_return_current_deadline_for_monthly_frequency_for_date_on_deadline_for_day31_for_asof_with_30_days_on_last_day_of_month(self):
        month = Month(31)
        self.assertEqual(date(2011,9,30) ,month.current_deadline_date(date(2011,9,30)))

    def test_should_return_current_deadline_for_monthly_frequency_for_date_on_deadline_for_day31_for_feb_with_28_days(self):
        month = Month(31)
        self.assertEqual(date(2011,2,28)  ,month.current_deadline_date(date(2011,3,3)))

    def test_should_return_current_deadline_for_monthly_frequency_for_date_on_deadline_for_day31_for_feb_with_29_days(self):
        month = Month(31)
        self.assertEqual(date(2012,2,29)  ,month.current_deadline_date(date(2012,3,3)))

