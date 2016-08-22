import re
import sys

from xamai.QtWebKit import Browser
from PyQt4 import QtCore, QtGui, QtWebKit
import xamai.Constants as const

class Gui():
    def login(self):
        data = {
            "css": self.loadStyles(),
            "alert": ""
        }

        win = Browser()
        win.main(win.readHTML("login.html", data))

    # Muestra una lista de respaldos
    def recover(self):
        from xamai.Recover import Recover
        r = Recover()
        data = {
            "goBakcButton": '',
            "card": r.loadYears(),
            "msg": "",
            "backup-location": ''
        }

        win = Browser()
        win.main(win.readHTML("index.html", data))

    # Muestra la configuracion y detalles de la cuenta del usuario
    def preferences(self):
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

        # carga la vista
        win = Browser()
        win.main(win.readHTML("settings.html", data))

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
                m = re.search("([A-Zz-z]{4}\d{6})(---|\w{3})", back)
                value = value + "<tr>" \
                                "<td>" + m.group(1) + "<td>" \
                                "<td>" + u.getDateFromBackup(back) + "<td>" \
                                "<tr>"
            return value

    # carga los estilos css
    def loadStyles(self):
        style = "<style>"
        # carga los estilos
        style_file = open(const.LOCATION + "/gui/assets/css/base.min.css", "r")
        style = style + "\n\n" + style_file.read()
        style_file.close()

        style_file = open(const.LOCATION + "/gui/assets/css/project.min.css", "r")
        style = style + "\n\n" + style_file.read()
        style_file.close()

        style = style + "\n\n" + "</style>"

        return style

app = Gui()
app.login()