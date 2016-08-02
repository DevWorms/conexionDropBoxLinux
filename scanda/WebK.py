#!/usr/bin/env python
# -*- coding: utf-8 -*-
import gi
gi.require_version('Gtk', '3.0')
# only in opensuse comment this line
gi.require_version('WebKit', '3.0')
from gi.repository import WebKit, Gtk
import scanda.Constants as const

class WebK(Gtk.Window):
    def __init__(self, html="", tpl={}):
        Gtk.Window.__init__(self, title='DB Protector')
        self.view = WebKit.WebView()
        settings = self.view.get_settings()
        settings.set_property('enable-default-context-menu', True)
        settings.set_property("enable-file-access-from-file-uris", True)
        settings.set_property("enable-plugins", True)
        settings.set_property("enable-scripts", True)
        settings.set_property("enable-universal-access-from-file-uris", True)
        settings.set_property("enable-developer-extras", True)

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
        self.view.load_html_string(output_page, const.LOCATION + '/html/')
