#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
import os
import sys
from PyQt4 import QtGui, QtCore

import xamai.Ui as gui
from xamai.QtWebKit import QtWebkit
from xamai.Status import Status
#import xamai.Constants as const

# Crea el icono de escritprio
class DBProtectorTrayIcon(QtGui.QSystemTrayIcon):
    def __init__(self, icon, parent = None):
        QtGui.QSystemTrayIcon.__init__(self, icon, parent)
        self.setupDialog = None

        self.parent = parent
        menu = QtGui.QMenu(parent)

        startAction = menu.addAction("Sincronizar ahora")
        self.connect(startAction, QtCore.SIGNAL("triggered()"), self.syncNow)
        self.setContextMenu(menu)

        startAction = menu.addAction("Recuperar respaldo")
        self.connect(startAction, QtCore.SIGNAL("triggered()"), self.openRecover)

        startAction = menu.addAction(u"Configuración")
        self.connect(startAction, QtCore.SIGNAL("triggered()"), self.openPreferences)
        self.setContextMenu(menu)

        menu.addSeparator()

        exitAction = menu.addAction("Status...")
        self.connect(exitAction, QtCore.SIGNAL("triggered()"), self.notifyStatus)
        self.setContextMenu(menu)

    def notifyStatus(self):
        s = Status()
        status_label = s.trayIconStatus()

        icon = QtGui.QSystemTrayIcon.MessageIcon()
        self.showMessage("DBProtector Status...", status_label, icon, 3 * 1000)

    def exit(self):
        sys.exit(0)

    def syncNow(self):
        icon = QtGui.QSystemTrayIcon.MessageIcon()
        self.showMessage("DBProtector Status...", "Sincronizando", icon, 3 * 1000)
        os.system('dbprotector_sync')

    def openRecover(self):
        from xamai.Recover import Recover
        r = Recover()
        data = {
            "css": gui.loadStyles(),
            "js": gui.loadJS(),
            "img": gui.loadImg(),
            "goBakcButton": '',
            "card": r.loadYears(),
            "msg": "",
            "backup-location": ''
        }

        html = gui.readHTML("index.html", data)

        # carga la vista
        self.setupDialog = QtWebkit(self, html)
        self.setupDialog.show()
        self.setupDialog.raise_()

    def openPreferences(self):
        from xamai.Preferences import Preferences
        p = Preferences()

        # Extrae los datos del usuario y los reemplaza en la vista
        user = p.returnUserData()
        # no sera visible en esta version
        options = '<option class="form-scanda" value="horas">Horas</option>' \
                  '<option class="form-scanda" value="dias">Dias</option>'
        # Si el espacio del user es ilimitado
        if user["space"] == -1:
            user["space"] = "Ilimitado"
            espacioLibre = "Ilimitado"
            espacioUsado = "0"
        else:
            espacioLibre = p.returnPercent(int(user['space']), int(user['freeSpace'])) + "%"
            espacioUsado = p.returnPercent(int(user['space']), int(user['spaceUsed']))
            user['space'] = str(user['space']) + " MB"

        data = {
            "css": gui.loadStyles(),
            "js": gui.loadJS(),
            "img": gui.loadImg(),
            "userPath": str(p.showExternalPath()),
            "last-success": str(gui.showLastSuccess()),
            "local-history": str(user['FileHistoricalNumber']),
            "cloud-history": str(user['FileHistoricalNumberCloud']),
            "color": p.returnColorProgressBar(),
            "user": user['user'],
            "space": user["space"],
            "space-available": espacioLibre,
            "space-used": espacioUsado,
            "space-used-mb": int(user['spaceUsed']),
            "path": user["path"],
            "time": user["time"],
            "time_type": options,
            "alert": ""
        }

        html = gui.readHTML("settings.html", data)

        # carga la vista
        self.setupDialog = QtWebkit(self, html)
        self.setupDialog.show()
        self.setupDialog.raise_()

'''
def main():
    app = QtGui.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    w = QtGui.QWidget()
    icon_file = os.path.join(const.LOCATION, const.ICONO)
    trayIcon = DBProtectorTrayIcon(QtGui.QIcon(icon_file), w)

    trayIcon.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
'''