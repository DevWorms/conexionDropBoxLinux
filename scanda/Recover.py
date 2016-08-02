#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from scanda.Login import Login
from scanda.Upload import Upload

'''
    Funciones llamadas al mostrar los respaldos del usuario
'''

class Recover():
    # codifica la ruta desde donde se descargara un archivo (no lo descarga)
    def downloadFile(self, args):
        year, month, file = args.split("-")
        month = self.monthsToInt(month)
        return "/"+str(self.user['IdCustomer'])+"/"+year+"/"+month+"/"+file

    # Devuelve una lista de backups por un mes determinado
    def getBackups(self, year, month):
        backups = []
        month = self.monthsToInt(month)
        files = self.u.getRemoteFilesList("/" + str(self.user['IdCustomer']) + "/"+year+"/"+month+"/")
        for i in files:
            path, name = os.path.split(i)
            backups.append(name)
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

            for i in backups:
                vals = str(i).split(".")
                name = vals[0]
                cardsBackups = cardsBackups + '<tr>' \
                                              '<td>' + str(name) + '</td>' \
                                              '<td><button class="btn btn-flat btn-brand" id="card_year_' + str(
                    i) + '" onClick="downloadBackup(true, \'' + y + '-' + m + '-' + str(i) + '\')">Descargar</button></td>'
        return cardsBackups + "</tbody></table></div>"

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
                                          '<button class="btn btn-flat card-heading waves-attach" id="card_year_' + str(
                    i) + '" onClick="recoverMonth(true, \''+year+'-' + str(i) + '\')">' + str(i) + '</button>' \
                                                                                 '</div>' \
                                                                                 '</div>' \
                                                                                 '</div>' \
                                                                                 '</div>'
        return cardsMonths

    # Devuelve una lista de anios por usuario
    def getYears(self):
        years = []
        for path in self.u.getRemoteFilesList("/"+str(self.user['IdCustomer'])+"/"):
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
                                          '<button class="btn btn-flat card-heading waves-attach" id="card_year_' + str(i) + '" onClick="recover(true, '+str(i)+')">' + str(i) + '</button>' \
                                          '</div>' \
                                          '</div>' \
                                          '</div>' \
                                          '</div>'
        return cardsYears

    def __init__(self):
        self.u = Upload()
        self.l = Login()
        self.user = self.l.returnUserData()
