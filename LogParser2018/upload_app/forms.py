#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.forms import forms

class FileUploadForm(forms.Form):
    my_file = forms.FileField(label='', label_suffix='')