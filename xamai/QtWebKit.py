#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

from PyQt4 import QtGui, QtWebKit
from PyQt4.QtCore import SIGNAL, QUrl
from PyQt4.QtGui import QIcon
from PyQt4.QtWebKit import QWebSettings, QWebPage

import xamai.Constants as const
from xamai.Listener import ListenerWebKit

class Browser():

    def readHTML(self, file, tpl = {}):
        html = const.LOCATION + "/gui/" + file

        fd = open(html, "r")
        data = fd.read().decode("utf-8")
        fd.close()

        for key, value in tpl.items():
            data = data.replace("{%s}" % key, str(value))

        return data

    def change(self, url):
        uri = QUrl(url).toString()
        if uri:
            action = ListenerWebKit()
            if uri == "#backups":
                self.webView.setHtml(action.getFromPreferencesToRecover())
            # Se clickea sobre un anio y se muestran los meses
            elif "#getMonth" in uri:
                uri, year = uri.split("=")
                self.webView.setHtml(action.getMothsFromYear(year))
            elif "#getBackup" in uri:
                uri, year, month = uri.split("=")
                year, trash = year.split("&")
                self.webView.setHtml(action.getBackupsFromMonth(year, month))
            elif "#downloadBackup" in uri:
                uri, year, month, backup = uri.split("=")
                year, trash = year.split("&")
                month, trash = month.split("&")
                action.downloadBackup(year, month, backup)
            elif uri == "#settings":
                self.webView.setHtml(action.getFromRecoverToPreferences())

    def main(self, html):
        app = QtGui.QApplication(sys.argv)
        app.setWindowIcon(QIcon(const.LOCATION + "/img/DB_Protector_16X16-01.png"))
        #app.setWindowTitle("DB Protector")
        #app.setFixedSize(800, 600)

        self.webView = QtWebKit.QWebView()
        self.webView.setWindowTitle("DB Protector")
        self.webView.setFixedSize(800, 600)
        self.webView.settings().setDefaultTextEncoding("UTF-8")
        self.webView.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
        self.webView.settings().setAttribute(QWebSettings.PluginsEnabled, True)
        self.webView.settings().setAttribute(QWebSettings.JavascriptEnabled, True)

        # Listeners
        actionListener = ListenerWebKit()
        self.webView.connect(self.webView, SIGNAL("linkClicked(const QUrl&)"), self.change)
        self.webView.page().mainFrame().addToJavaScriptWindowObject("actionListener", actionListener)

        self.webView.setHtml(html)

        window = QtGui.QMainWindow()
        window.setCentralWidget(self.webView)
        window.show()

        #sys.exit(app.exec_())
