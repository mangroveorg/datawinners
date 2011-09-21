# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import calendar
from dateutil.relativedelta import relativedelta
from datetime import date, timedelta

class NotADeadLine(Exception):
    pass

class Deadline(object):
    def __init__(self,frequency,mode):
        self.frequency = frequency
        self.mode = mode

    def next(self, as_of):
        return self.frequency.next_date(as_of,self._get_offset())

    def current(self, as_of):
        return self.frequency.current_date(as_of)

#      Deadline class converts the modes "Following" or "That" to the currect offsets.
    def _get_offset(self):
        if self.mode == "Following":
            return 1
        return 0

    def get_applicable_frequency_period_for(self, as_of):
        return self.frequency.get_frequency_period_for(as_of, self.mode)


class Month(object):
    def __init__(self,day):
        self.day = day

#    Offset is any valid offset > 0. Month knows that offset means months.
    def next_date(self, as_of,offset):
        if as_of.day > self.day and offset == 0:
            return None
        if as_of.month == 12 and offset == 1:
            return date(as_of.year + 1, offset, self.day)
        return date(as_of.year, as_of.month + offset, self.day)

    def current_date(self, as_of):
        return date(as_of.year, as_of.month, self.day)

    def get_frequency_period_for(self, as_of, mode):
        if as_of.day != self.day:
            raise NotADeadLine
        target_date = as_of
        if mode == 'Following':
            target_date = as_of + relativedelta(months=-1)
        week_day, last_day = calendar.monthrange(target_date.year,target_date.month)

        return date(target_date.year, target_date.month, 1), date(target_date.year, target_date.month, last_day)
    
class Week(object):
    #    day is 1-7 ie Mon - Sun
    MONDAY_ISO_WEEKDAY = 1
    SUNDAY_ISO_WEEKDAY = 7

    def __init__(self,day):
        self.day = day

    def next_date(self, as_of,offset):
        if offset == 1:
            as_of = as_of + timedelta(days=7)

        if offset == 0 and as_of.isoweekday() > self.day:
            return None

        return date(as_of.year, as_of.month, as_of.day) + timedelta(days=(self.day - as_of.isoweekday()))

    def current_date(self, as_of):
        if as_of.isoweekday() > self.day:
            return as_of - timedelta(as_of.isoweekday()-self.day)
        return as_of + timedelta(self.day-as_of.isoweekday())

    def get_frequency_period_for(self, as_of, mode):
        if as_of.isoweekday() != self.day:
            raise NotADeadLine
        target_date = as_of
        if mode == 'Following':
            target_date = as_of + relativedelta(weeks=-1)
        start_date =  target_date - timedelta(days = target_date.isoweekday() - self.MONDAY_ISO_WEEKDAY)
        end_date = target_date + timedelta(days = self.SUNDAY_ISO_WEEKDAY - target_date.isoweekday())
        return start_date,end_date
