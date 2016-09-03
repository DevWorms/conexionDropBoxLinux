#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
import os
import thread

from PyQt4 import QtCore, QtGui

import re

import xamai.Constants as const

class ListenerWebKit(QtCore.QObject):
    @QtCore.pyqtSlot(str)
    def showMessage(self, msg):
        QtGui.QMessageBox.information(None, "Info", msg)

    @QtCore.pyqtSlot(str, str)
    def doLogin(self, user, password):
        user = str(user)
        password = str(password)
        from xamai.Login import Login
        l = Login()

        if user and password:
            # Si el login es correcto
            if l.loginApi(user, password):
                # Inicia un nuevo thread, con la aplicacion
                thread.start_new_thread(os.system, ("/usr/bin/dbprotector_xamai",))
                # Cierra la aplicacion
                QtGui.QApplication.exit()
            else:
                QtGui.QMessageBox.information(None, "Notificacion", u"Usuario o contraseña incorrectos")

    @QtCore.pyqtSlot(str, str, str)
    def savePreferences(self, route, time, userPath):
        from xamai.Preferences import Preferences
        p = Preferences()

        if route:
            # if p.writePreferences(route, time, time_type):
            if p.writePreferences(str(route), int(time), "dias", str(userPath)):
                # reemplaza alert con un mensaje
                QtGui.QMessageBox.information(None, "Notificacion", "Los cambios se guardaron correctamente")
            else:
                QtGui.QMessageBox.information(None, "Notificacion", "Ocurrio un error al guardar los cambios")

    @QtCore.pyqtSlot()
    def closeSession(self):
        from xamai.Login import Login
        l = Login()
        l.closeSession()
        QtGui.QApplication.exit()

    def getFromPreferencesToRecover(self):
        from xamai.Recover import Recover
        r = Recover()
        data = {
            "card": r.loadYears(),
            "backup-location": '',
            "goBakcButton": '',
            "msg": ''
        }

        return self.readHTML("index.html", data)

    def getFromRecoverToPreferences(self):
        from xamai.Preferences import Preferences
        p = Preferences()
        # Carga los datos del usuario
        user = p.returnUserData()

        # no sera visible en esta version
        options = '<option class="form-scanda" value="horas">Horas</option>' \
                  '<option class="form-scanda" value="dias">Dias</option>'

        # Ajusta los datos a porcentajes
        if user['space'] == -1:
            user['space'] = "Ilimitado"
            espacioLibre = "Ilimitado"
            espacioUsado = "0"
        else:
            espacioLibre = p.returnPercent(int(user['space']), int(user['freeSpace'])) + "%"
            espacioUsado = p.returnPercent(int(user['space']), int(user['spaceUsed']))
            user['space'] = str(user['space']) + " MB"

        data = {
            "userPath": str(p.showExternalPath()),
            "last-success": str(self.showLastSuccess()),
            "local-history": str(user['FileHistoricalNumber']),
            "cloud-history": str(user['FileHistoricalNumberCloud']),
            "color": p.returnColorProgressBar(),
            "user": user['user'],
            "space": user["space"],
            "space-available": espacioLibre,
            "space-used": espacioUsado,
            "path": user["path"],
            "time": user["time"],
            "time_type": options,
            "alert": ""
        }

        return self.readHTML("settings.html", data)

    def getMothsFromYear(self, year):
        from xamai.Recover import Recover
        r = Recover()
        data = {
            "card": r.loadMonths(str(year)),
            "backup-location":  ' > ' + str(year),
            "goBakcButton": '<a class="btn waves-attach" href="#backups">volver</a>',
            "msg": ''
        }

        return self.readHTML("index.html", data)

    # Muestra el ultimo respaldo exitoso hecho por cada rfc de un usuario
    def showLastSuccess(self):
        from xamai.Upload import Upload
        u = Upload()
        backups = u.getLastSuccess()
        value = ''
        if not backups:
            value = "<tr><td colspan=2><h3 style='color: #BDBDBD; text-align: center;'>No se encontraron respaldos</h3></td></tr>"
        else:
            for back in backups:
                m = re.search("\[A-Za-z\]{3,4}\[0-9\]{6}\[A-Za-z0-9\]{3}", back)
                value = value + "<tr>" \
                                "<td>" + m.group(1) + "<td>" \
                                "<td>" + u.getDateFromBackup(back) + "<td>" \
                                "<tr>"
        return value

    def getBackupsFromMonth(self, year, month):
        from xamai.Recover import Recover
        r = Recover()
        data = {
            "card": r.loadBackups(str(year), str(month)),
            "backup-location": ' > ' + str(year) + ' > ' + str(month),
            "goBakcButton": '<a class="btn waves-attach" href="#backups">volver</a>',
            "msg": ''
        }
        return self.readHTML("index.html", data)

    def downloadBackup(self, year, month, backup    ):
        from xamai.Recover import Recover
        from xamai.Upload import Upload
        from xamai.Login import Login
        from os.path import expanduser
        l = Login()
        u = Upload()
        r = Recover()

        # Selecciona donde se guardara
        path = QtGui.QFileDialog.getExistingDirectory(
            None,
            "Seleccione la carpeta de destino",
            expanduser("~"),
            QtGui.QFileDialog.ShowDirsOnly
        )

        path = str(path)

        if not path:
            path = l.returnUserData()['path']

        # Descarga asincrona
        thread.start_new_thread(u.downloadFile, (r.downloadFile(str(year), str(month), str(backup)), str(path),))
        # Notificacion
        QtGui.QMessageBox.information(None, "Notificacion", "Descargando " + str(backup) + " en " + path)

    def readHTML(self, file, tpl={}):
        html = const.LOCATION + "/gui/" + file

        fd = open(html, "r")
        data = fd.read().decode("utf-8")
        fd.close()

        for key, value in tpl.items():
            data = data.replace("{%s}" % key, str(value))

        return data