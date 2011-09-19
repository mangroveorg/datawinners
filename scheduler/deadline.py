# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from datetime import date, timedelta

class Deadline(object):
    def __init__(self,frequency,mode):
        self.frequency = frequency
        self.mode = mode

    def next(self, as_of):
        return self.frequency.next_date(as_of,self._get_offset())

#      Deadline class converts the modes "Following" or "That" to the currect offsets.
    def _get_offset(self):
        if self.mode == "Following":
            return 1
        return 0


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

class Week(object):
#    day is 1-7 ie Mon - Sun
    def __init__(self,day):
        self.day = day

    def next_date(self, as_of,offset):
        if offset == 1:
            as_of = as_of + timedelta(days=7)

        if offset == 0 and as_of.isoweekday() > self.day:
            return None

        return date(as_of.year, as_of.month, as_of.day) + timedelta(days=(6 - as_of.isoweekday()))