#!/usr/bin/env python
# -*- coding: utf-8 -*-
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit', '3.0')
from gi.repository import WebKit, Gtk
import os

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))

class Ui(Gtk.Window):

    def __init__(self, html="", tpl={}):
        Gtk.Window.__init__(self, title='Recuperar Respaldos')
        self.view = WebKit.WebView()
        self.add(self.view)
        settings = self.view.get_settings()
        settings.set_property('enable-default-context-menu', True)
        self.view.set_settings(settings)
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
        self.view.load_html_string(output_page, ROOT_DIR + '/html/')