#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gi
import pygtk

gi.require_version('Gtk', '3.0')

pygtk.require('2.0')


class Test:
    print "Unit Test"

app = Test()