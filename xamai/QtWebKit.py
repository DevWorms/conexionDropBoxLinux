#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-
from PyQt4 import QtWebKit

from PyQt4.QtCore import QUrl, SIGNAL
from PyQt4.QtGui import QIcon
from PyQt4.QtWebKit import QWebSettings, QWebPage

import xamai.Constants as const
from xamai.Listener import ListenerWebKit


class QtWebkit(QtWebKit.QWebView):
    # Crea un webkit para las vistas
    def __init__(self, parent, html):
        QtWebKit.QWebView.__init__(self, None)
        self.setWindowIcon(QIcon(const.LOCATION + "/img/DB_Protector_16X16-01.png"))
        self.setWindowTitle("DBProtector")
        self.setFixedSize(800, 600)
        self.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)

        # Listeners
        actionListener = ListenerWebKit()
        self.connect(self, SIGNAL("linkClicked(const QUrl&)"), self.change)
        self.page().mainFrame().addToJavaScriptWindowObject("actionListener", actionListener)

        self.setHtml(html)
        self.parent = parent

    # listener: cada vez que se cambia de vista
    def change(self, url):
        uri = QUrl(url).toString()
        if uri:
            action = ListenerWebKit()
            if "#backups" in uri:
                self.setHtml(action.getFromPreferencesToRecover())
            # Se clickea sobre un anio y se muestran los meses
            elif "#getMonth" in uri:
                uri, year = uri.split("=")
                self.setHtml(action.getMothsFromYear(year))
            elif "#getBackup" in uri:
                uri, year, month = uri.split("=")
                year, trash = year.split("&")
                self.setHtml(action.getBackupsFromMonth(year, month))
            elif "#downloadBackup" in uri:
                uri, year, month, backup = uri.split("=")
                year, trash = year.split("&")
                month, trash = month.split("&")
                action.downloadBackup(year, month, backup)
            elif "#settings" in uri:
                self.setHtml(action.getFromRecoverToPreferences())
