"""
Adds filtering by ranges of dates in the admin filter sidebar.

https://github.com/coolchevy/django-datefilterspec

Example:

from django.db import models
import datefilterspec
 
class Person(models.Model):
    date = models.DateTimeField(default=datetime.datetime.now)
    date.date_filter = True

    class Admin:
        list_filter = ['date']
"""

__author__ = "Vitalii Kulchevych  <coolchevy@gmail.com>"
__date__ = "01 Feb 2011"
__all__ = ["DateFilterSpec"]


import datetime
from django.conf import settings
from django import forms
from django.utils.translation import ugettext as _
from django.contrib.admin.filterspecs import FilterSpec, DateFieldFilterSpec
from django.utils.safestring import mark_safe
from django.contrib.admin.widgets import AdminDateWidget


class DateForm(forms.Form):

    def __init__(self, *args, **kwargs):
        field_name = kwargs.pop('field_name')
        super(DateForm, self).__init__(*args, **kwargs)
        self.fields['%s__gte' % field_name ] = forms.DateField(label=(_('From')),widget=AdminDateWidget,required=False)
        self.fields['%s__lte' % field_name ] = forms.DateField(label=(_('To')),widget=AdminDateWidget,required=False)
        for k in kwargs.get('initial',{}):
            if not self.fields.has_key(k):
                self.fields[k] = forms.CharField(widget=forms.HiddenInput())
                self.fields[k].initial = kwargs.get('initial').get(k)


class DateFilterSpec(DateFieldFilterSpec):

    def __init__(self, f, request, params, model, model_admin, field_path=None):
        super(DateFilterSpec, self).__init__(f, request, params, model,
                                                   model_admin,field_path=field_path)
        self.field_generic = '%s__' % self.field.name

    def title(self):
        title = super(DateFilterSpec, self).title()
        form = DateForm(initial=self.params, field_name=self.field.name)
        out =  u"""
        <style>
            .calendarbox {
                /*left:0 !important;*/
                z-index:1100;
        }
        </style>
        <form method="GET" action="">
        <ul>
        %(form)s
        <li> <input type="submit" value="%(search)s"> </li>
        </ul>
        </form>
        """ % {'search':_('Go'),'form':form.as_ul()}
        return mark_safe(title) + mark_safe(out)
        

# register the filter
FilterSpec.filter_specs.insert(0, (lambda f: hasattr(f, 'date_filter'), DateFilterSpec))