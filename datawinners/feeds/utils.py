# class Coordinate(object):
#     def __init__(self, a, b):
#         self.a = a
#         self.b = b
#
#     def __str__(self):
#         return "coords : " + str(self.__dict__)
#
# def add(x, y):
#     print Coordinate(x.a + y.a, x.b + y.b)
#     return Coordinate(x.a + y.a, x.b + y.b)
#
#
# def sub(x, y):
#     print Coordinate(x.a - y.a, x.b - y.b)
#
# def wrapper(func):
#     def check(one, two):#how does this check will hv access to func parameters?
#         if one.a < 0 or one.b < 0:
#             one = Coordinate(one.a if one.a > 0 else 0, one.b if one.b > 0 else 0)
#
#         if two.a < 0 or two.b < 0:
#             two = Coordinate(two.a if two.a > 0 else 0, two.b if two.b > 0 else 0)
#
#         ret = func(one,two)
#         if ret.a < 0 or ret.b < 0:
#             ret = Coordinate(ret.a if ret.a > 0 else 0,ret.b if ret.b > 0 else 0)
#         return ret
#     return check
#
# one = Coordinate(10, 20)
# two = Coordinate(-5, -7)
#
# add = wrapper(add)
# add(two,one)

# def logging(func):
#     def inner(*args,**kwargs):
#         print "args are %s ,%s" %(args,kwargs)
#         print args[0]
#         return func(*args,**kwargs)
#     return inner
#
# @logging
# def foo(x,y):
#     print x * y
#
#
# foo(2,3)

from django.http import HttpResponse, HttpRequest


def is_not_datasender(func):
    def inner(*args, **kwargs):
        request = args[0]
        if request.user.get_profile().reporter:
            return HttpResponse(content="You are not authorized to view this content", status=400)
        return func(*args, **kwargs)

    return inner


from unittest import TestCase
from mock import Mock, PropertyMock
from accountmanagement.models import NGOUserProfile


class TestUtils(TestCase):
    def test_should_restrict_ds(self):
        def foo(request):
            return HttpResponse(status=200)

        foo = is_not_datasender(foo)
        mock_request = Mock()
        mock_user = Mock(spec=NGOUserProfile)
        type(mock_user).reporter = PropertyMock(return_value=True)
        config = {"user.get_profile.return_value": mock_user}
        mock_request.configure_mock(**config)
        response = foo(mock_request)
        self.assertEquals(400, response.status_code)
        self.assertEquals("You are not authorized to view this content", response.content)

    def test_should_allow_others(self):
        def foo(request):
            return HttpResponse(content="welcome",status=200)

        foo = is_not_datasender(foo)
        mock_request = Mock()
        mock_user = Mock(spec=NGOUserProfile)
        type(mock_user).reporter = PropertyMock(return_value=False)
        config = {"user.get_profile.return_value": mock_user}
        mock_request.configure_mock(**config)
        response = foo(mock_request)
        self.assertEquals(200, response.status_code)
        self.assertEquals("welcome", response.content)


