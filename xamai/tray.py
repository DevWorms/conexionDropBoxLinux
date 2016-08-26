#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from PyQt4 import QtGui

from PyQt4.QtCore import SIGNAL

import xamai.Constants as const
from xamai.Gui import Gui
from xamai.Status import Status


class RightClickMenu(QtGui.QMenu):
    def __init__(self, parent=None):
        QtGui.QMenu.__init__(self, "File", parent)

        s = Status()
        statusUpload = s.getUploadStatus()
        statusDownload = s.getDownloadStatus()

        icon = QtGui.QIcon.fromTheme("")
        recover = QtGui.QAction(icon, "&Recuperar respaldo", self)
        recover.triggered.connect(lambda : self.setActionMenu(1))
        self.addAction(recover)

        settings = QtGui.QAction(icon, "&Ajustes", self)
        settings.triggered.connect(lambda: self.setActionMenu(2))
        self.addAction(settings)

        sync = QtGui.QAction(icon, "&Sincronizar ahora", self)
        sync.triggered.connect(lambda: self.setActionMenu(3))
        self.addAction(sync)

        separator = QtGui.QAction(icon, "", self)
        separator.setSeparator(True)
        self.addAction(separator)

        # si se encuentra sincronizado
        if statusUpload['status'] == 0 and statusDownload['status'] == 0:
            status_label = "Sincronizado"
        # si esta subiendo y descargando al mismo tiempo
        elif statusUpload['status'] != 0 and statusDownload['status'] == 1:
            if statusUpload['status'] == 1:
                status_label = "Subiendo " + statusUpload['chunk'] + "% / Descargando " + statusDownload['file']
            elif statusUpload['status'] == 2:
                # self.icon.set_from_file("img/sync.png")
                status_label = "Descargando " + statusDownload['file']
            elif statusUpload['status'] == 3:
                status_label = "Cifrando archivo / Descargando " + statusDownload['file']
        # si esta subiendo y descargando al mismo tiempo (si esta descomprimiendo el archivo)
        elif statusUpload['status'] != 0 and statusDownload['status'] == 2:
            if statusUpload['status'] == 1:
                status_label = "Subiendo " + statusUpload['chunk'] + "% / Descifrando " + statusDownload['file']
            elif statusUpload['status'] == 2:
                # self.icon.set_from_file("img/sync.png")
                status_label = "Descifrando " + statusDownload['file']
            elif statusUpload['status'] == 3:
                status_label = "Cifrando archivo / Descifrando " + statusDownload['file']
        # si esta subiendo, pero no descargando
        else:
            if statusUpload['status'] != 0:
                if statusUpload['status'] == 1:
                    status_label = "Subiendo " + statusUpload['file'] + " " + statusUpload['chunk'] + "%"
                elif statusUpload['status'] == 2:
                    # self.icon.set_from_file("img/sync.png")
                    status_label = "Sincronizado"
                elif statusUpload['status'] == 3:
                    status_label = "Cifrando " + statusUpload['file'] + " para subir"
            if statusDownload['status'] == 1:
                status_label = "Descargando " + statusDownload['file']
            if statusDownload['status'] == 2:
                status_label = "Descifrando " + statusDownload['file']

        status = QtGui.QAction(icon, "&%s" %status_label, self)
        status.setDisabled(True)
        self.addAction(status)

    # abre una nueva interfaz
    def setActionMenu(self, action):
        if action == 1 or action == 2:
            get = Gui()
            if action == 1:
                get.recover()
            elif action == 2:
                get.preferences()
        elif action == 3:
            os.system('/usr/bin/dbprotector_sync')

class SystemTrayIcon(QtGui.QSystemTrayIcon):
    def __init__(self, parent=None):
        QtGui.QSystemTrayIcon.__init__(self, parent)
        icon_file = os.path.join(const.LOCATION, const.ICONO)
        self.setIcon(QtGui.QIcon(icon_file))

        self.right_menu = RightClickMenu()
        self.setContextMenu(self.right_menu)

    def show(self):
        QtGui.QSystemTrayIcon.show(self)

if __name__ == "__main__":
    app = QtGui.QApplication([])

    tray = SystemTrayIcon()
    tray.show()

    #set the exec loop going
    app.exec_()