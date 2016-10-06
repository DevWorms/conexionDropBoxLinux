#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

import os
import re

from xamai.Login import Login
from xamai.Upload import Upload

'''
    Funciones llamadas al mostrar los respaldos del usuario
'''

class Recover():
    # codifica la ruta desde donde se descargara un archivo (no lo descarga)
    def downloadFile(self, year, month, file):
        month = self.monthsToInt(month)
        return "/"+str(self.user['IdCustomer'])+"/"+year+"/"+month+"/"+file

    # Devuelve una lista de backups por un mes determinado
    def getBackups(self, year, month):
        backups = []
        month = self.monthsToInt(month)
        files = self.u.getBackups("/" + str(self.user['IdCustomer']) + "/"+year+"/"+month+"/")
        for i in files:
            path, name = os.path.split(i.path_display)
            backups.append(name)
        backups = self.u.formatBackups(backups)
        return backups

    # regresa los backups en una tabla html
    def loadBackups(self, y, m):
        backups = self.getBackups(y, m)
        if not backups:
            cardsBackups = "<h3 style='color: #BDBDBD; text-align: center;'>No se encontraron respaldos</h3>"
        else:
            cardsBackups = '<div class="table-responsive">' \
                           '<table class="table" title="Descargar respaldo">' \
                           '<tbody>'

            for rfc in backups:
                cardsBackups = cardsBackups + '<tr><td colspan=4>'+ self.extractRFC(rfc[0]) +'</td></tr>'
                for i in rfc:
                    # Reconstruye el Backup
                    backup = "/" + str(self.user['IdCustomer']) + "/" + y + "/" + self.monthsToInt(m) + "/" + i
                    # Obtiene el tamanio del archivo
                    size = self.u.getBackupSize(backup)
                    cardsBackups = cardsBackups + '<tr>' \
                                                  '<td></td>' \
                                                  '<td>' + self.formatBackupName(str(i)) + '</td>' \
                                                  '<td>' + str(size) + '</td>' \
                                                  '<td><a class="btn btn-flat btn-brand" id="card_year_' + str(i) + '" href="#downloadBackup&year=' + y + '&month=' + m + '&backup=' + str(i) + '">Descargar</a></td>' \
                                                  '</tr>'
        cardsBackups = cardsBackups + "</tbody></table></div>"
        return cardsBackups

    # Devuelve el rfc de un respaldo
    def extractRFC(self, backup):
        m = re.search("[A-Za-z]{3,4}[0-9]{6}[A-Za-z0-9]{3}", backup)
        if m:
            return str(m.group(0))
        else:
            return ''

    # Devuelve la fecha 2016-08-24 08:20:12 de un respaldo
    def formatBackupName(self, backup):
        m = re.search("(\d{14}).(\w{3})", backup)
        if m:
            fecha = str(m.group(1))
            final = fecha[0:4] + "-" + fecha[4:6] + "-" + fecha[6:8] + " " + fecha[8:10] + ":" + fecha[10:12] + ":" + fecha[12:14]
            return final
        else:
            return ''

    # pasa los meses a digitos
    def monthsToInt(self, month):
        if month == "Enero":
            month = "01"
        elif month == "Febrero":
            month = "02"
        elif month == "Marzo":
            month = "03"
        elif month == "Abril":
            month = "04"
        elif month == "Mayo":
            month = "05"
        elif month == "Junio":
            month = "06"
        elif month == "Julio":
            month = "07"
        elif month == "Agosto":
            month = "08"
        elif month == "Septiembre":
            month = "09"
        elif month == "Octubre":
            month = "10"
        elif month == "Noviembre":
            month = "11"
        elif month == "Diciembre":
            month = "12"
        return month

    # Devuelve una lista de meses por un anio determinado
    def getMonths(self, year):
        months = []
        files = self.u.getRemoteFilesList("/" + str(self.user['IdCustomer']) + "/"+year+"/")
        for path in files:
            if self.u.getRemoteFilesList(path):
                id, month = os.path.split(path)
                if month == "01":
                    months.append("Enero")
                elif month == "02":
                    months.append("Febrero")
                elif month == "03":
                    months.append("Marzo")
                elif month == "04":
                    months.append("Abril")
                elif month == "05":
                    months.append("Mayo")
                elif month == "06":
                    months.append("Junio")
                elif month == "07":
                    months.append("Julio")
                elif month == "08":
                    months.append("Agosto")
                elif month == "09":
                    months.append("Septiembre")
                elif month == "10":
                    months.append("Octubre")
                elif month == "11":
                    months.append("Noviembre")
                elif month == "12":
                    months.append("Diciembre")
        return  months

    # Devuelve un string HTML con los cardviews por cada mes
    def loadMonths(self, year):
        cardsMonths = ""
        months = self.getMonths(year)
        if not months:
            cardsMonths = "<h3 style='color: #BDBDBD; text-align: center;'>No se encontraron respaldos</h3>"
        else:
            for i in months:
                cardsMonths = cardsMonths + '<div class="col-md-4 col-sm-3">' \
                                          '<div class="card-scanda">' \
                                          '<div class="card-main">' \
                                          '<div class="card-inner">' \
                                          '<a style="text-align: center;" class="btn btn-flat card-heading waves-attach" id="card_year_' + str(
                    i) + '" href="#getBackup&year='+year+'&month=' + str(i) + '">' + str(i) + '</a>' \
                                          '</div>' \
                                          '</div>' \
                                          '</div>' \
                                          '</div>'
        return cardsMonths

    # Devuelve una lista de anios por usuario
    def getYears(self):
        years = []
        for path in self.u.getRemoteFilesList("/"+str(self.user['IdCustomer'])+"/"):
            if self.u.getRemoteFilesList(path):
                id, year = os.path.split(path)
                years.append(year)
        return years

    # Devuelve un string HTML con los cardviews por cada anio
    def loadYears(self):
        cardsYears = ""
        years = self.getYears()
        if not years:
            cardsYears = "<h3 style='color: #BDBDBD; text-align: center;'>No se encontraron respaldos</h3>"
        else:
            for i in years:
                cardsYears = cardsYears + '<div class="col-md-4 col-sm-3">' \
                                          '<div class="card-scanda">' \
                                          '<div class="card-main">' \
                                          '<div class="card-inner">' \
                                          '<a style="text-align: center;" class="btn btn-flat card-heading waves-attach" id="card_year_' + str(i) + '" href="#getMonth&year='+ str(i) + '" ">' + str(i) + '</a>' \
                                          '</div>' \
                                          '</div>' \
                                          '</div>' \
                                          '</div>'
        return cardsYears

    def __init__(self):
        self.u = Upload()
        self.l = Login()
        self.user = self.l.returnUserData()
