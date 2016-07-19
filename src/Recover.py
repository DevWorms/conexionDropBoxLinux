#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from Login import Login
from Upload import Upload

'''
    Faltan logs, y descargar archivo
'''

class Recover():
    CONFIG_FILE = "settings/configuration.json"
    LOCATION = os.path.dirname(os.path.realpath(__file__))
    BACKUPS = []

    '''
        Cada vez que se da click en algun cardview, ya sea anio o mes
        llama esta funcion
    '''
    def recoverClicked(self, webview, webFrame, networkRequest):
        uri = networkRequest.get_uri()
        if uri.find("://") > 0:
            scheme, path = uri.split("://", 1)
        else:
            return False
        if scheme == 'admin' and path == "recover":
            # Extrae el anio seleccionado
            year = webFrame.get_dom_document().get_element_by_id("card_clicked").get_value()
            # vuelve a cargar la vista de index
            fd = open(self.LOCATION + "/gui/index.html", "r")
            tmp_page = fd.read()
            fd.close()

            tmp_page = tmp_page.replace("{card}", self.loadMonths(year))
            tmp_page = tmp_page.replace("{status}", "")
            tmp_page = tmp_page.replace("{msg}", "")
            webview.load_html_string(tmp_page, self.LOCATION + '/html/')
            return True
        elif scheme == 'admin' and path == "recoverMonth":
            # extrae el mes y anio seleccionado
            val = webFrame.get_dom_document().get_element_by_id("card_clicked").get_value()
            y, m = val.split("-")
            # vuelve a cargar la vista de index
            fd = open(self.LOCATION + "/gui/index.html", "r")
            tmp_page = fd.read()
            fd.close()

            tmp_page = tmp_page.replace("{card}", self.loadBackups(y, m))
            tmp_page = tmp_page.replace("{status}", "")
            tmp_page = tmp_page.replace("{msg}", "")
            webview.load_html_string(tmp_page, self.LOCATION + '/html/')
            return True
        elif scheme == 'admin' and path == "downloadBackup":
            # Extrae el respaldo seleccionado
            backup = webFrame.get_dom_document().get_element_by_id("card_clicked").get_value()
            # vuelve a cargar la vista de index
            fd = open(self.LOCATION + "/gui/index.html", "r")
            tmp_page = fd.read()
            fd.close()

            # Descarga el archivo
            print self.downloadFile(backup)

            # Recupera anio y mes
            y, m, file = backup.split("-")
            # Remplaza los parametros
            tmp_page = tmp_page.replace("{status}", "Descargando")
            tmp_page = tmp_page.replace("{card}", self.loadBackups(y, m))
            tmp_page = tmp_page.replace("{msg}", '<div class="tile-wrap">'
                                                           '<div class="tile tile-collapse tile-brand">'
                                                           '<div data-target="#ui_tile_example_red" data-toggle="tile">'
                                                           '<div class="tile-inner">'
                                                           '<div class="text-overflow">Descargando respaldo: '+file+'</div>'
                                                           '</div>'
                                                           '</div>'
                                                           '</div>'
                                                           '</div>')
            webview.load_html_string(tmp_page, self.LOCATION + '/html/')
            return True

    def downloadFile(self, args):
        year, month, file = args.split("-")
        month = self.monthsToInt(month)
        return "/"+str(self.user['IdCustomer'])+"/"+year+"/"+month+"/"+file

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

    # Devuelve una lista de backups por un mes determinado
    def getBackups(self, year, month):
        backups = []
        month = self.monthsToInt(month)
        files = self.u.getRemoteFilesList("/" + str(self.user['IdCustomer']) + "/"+year+"/"+month+"/")
        for i in files:
            path, name = os.path.split(i)
            backups.append(name)
        return backups

    def loadBackups(self, y, m):
        cardsBackups = '<div class="table-responsive">' \
                       '<table class="table" title="A basic table">' \
                       '<tbody>'
        backups = self.getBackups(y, m)
        for i in backups:
            vals = str(i).split(".")
            name = vals[0]
            cardsBackups = cardsBackups + '<tr>' \
                                          '<td>' + str(name) + '</td>' \
                                          '<td><button class="btn btn-flat btn-brand" id="card_year_' + str(
                i) + '" onClick="downloadBackup(true, \'' + y + '-' + m + '-' + str(i) + '\')">Descargar</button></td>'
        return cardsBackups + "</tbody></table></div>"

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
        for i in months:
            cardsMonths = cardsMonths + '<div class="col-md-4 col-sm-4">' \
                                      '<div class="card card-scanda">' \
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
        for i in years:
            cardsYears = cardsYears + '<div class="col-md-4 col-sm-4">' \
                                      '<div class="card card-scanda">' \
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
