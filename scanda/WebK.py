#!/usr/bin/env python
# -*- coding: utf-8 -*-
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit', '3.0')
from gi.repository import WebKit, Gtk
import os

CONFIG_FILE = "settings/configuration.json"
LOCATION = os.path.dirname(os.path.realpath(__file__))

class WebK(Gtk.Window):
    def __init__(self, html="", tpl={}):
        Gtk.Window.__init__(self, title='DBProtector')
        self.view = WebKit.WebView()
        settings = self.view.get_settings()
        settings.set_property('enable-default-context-menu', True)
        self.view.set_settings(settings)
        self.set_resizable(False)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.add(self.view)
        self.add(scroll)

        self.progress = 0
        if html:
            self.load_html(html, tpl)

    def load_html(self, html, tpl):
        fd = open(html, "r")
        self.tmp_page = fd.read()
        fd.close()
        output_page = self.tmp_page
        for key, value in tpl.items():
            output_page = output_page.replace("{%s}" % key, str(value))
        self.view.load_html_string(output_page, LOCATION + '/html/')