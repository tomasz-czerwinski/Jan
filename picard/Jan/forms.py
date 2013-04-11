# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from django import forms
from picard.Jan.models import *
from django.forms.extras.widgets import SelectDateWidget
from datetime import datetime, timedelta


class BranchForm(forms.ModelForm):

    class Meta:
        model = Branch
        fields = ('strategy',)


class HistoryFilterForm(forms.Form):
    branch = forms.ModelChoiceField(queryset=Branch.objects.all())
    from_date = forms.DateField(widget=SelectDateWidget(), initial=datetime.today() - timedelta(days=30))
    to_date = forms.DateField(widget=SelectDateWidget(), initial=datetime.today())
