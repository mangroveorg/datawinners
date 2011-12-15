# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from exceptions import Exception

class CouldNotLocatePageException(Exception):
    pass

class ElementStillPresentException(Exception):
    pass

class ElementFoundWithoutDesiredVisibility(Exception):
    pass

class CouldNotLocateElementException(Exception):
    def __init__(self, selector, locator):
        self.selector = selector
        self.locator = locator

    def __str__(self):
        return "Could not find %s by %s" % (self.locator, self.selector)
