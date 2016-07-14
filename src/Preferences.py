#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import urllib2

import pygtk
import gi
import os
from Ui import Ui
from Login import Login
from SetLog import SetLog

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

pygtk.require('2.0')

class Preferences():
    CONFIG_FILE = "settings/configuration.json"
    LOCATION = os.path.dirname(os.path.realpath(__file__))

    def timeValidation(self, time, value, path):
        if value == "minutos":
            if time > 59:
                time = 59
            elif time < 0:
                time = 0
        elif value == "horas":
            if time > 23:
                time = 23
            elif time < 0:
                time = 0
        elif value == "dias":
            if time > 31:
                time = 31
            elif time < 1:
                time = 1
        else:
            value = "horas"
            time = time
        self.writePreferences(path, time, value)

    # guarda los datos del usuario recibidos
    def writePreferences(self, path, time, time_type):
        log = SetLog()
        # Carga el archivo configuration.json
        file = os.path.join(self.LOCATION, self.CONFIG_FILE)
        # Si el archivo existe...
        if (os.path.exists(file)):
            # abre el archivo y guarda la variable 'path' del archivo json
            with open(file, 'r') as f:
                data = json.load(f)
            # escribe la nueva variable time en el archivo json junto con la variable value
            with open(file, 'w') as f:
                json.dump({
                    'path': path,
                    'time': time,
                    'time_type': time_type,
                    'IdCustomer': data['IdCustomer'],
                    'user': data['user'],
                    'password': data['password'],
                    'tokenDropbox': data['tokenDropbox'],
                }, f)
            return True
        else:
            log.newLog("load_config_file", "E", "")
            return False

    '''
        Cada vez que se da click se ejecuta esta funcion,
        dependiendo de la accion...
    '''
    def preferencesClicked(self, webview, webFrame, networkRequest):
        uri = networkRequest.get_uri()
        if uri.find("://") > 0:
            scheme, path = uri.split("://", 1)
        else:
            return False

        # extrae path y frecuencia de respaldo de los forms HTML
        route = webFrame.get_dom_document().get_element_by_id("ui_path").get_value()
        time = webFrame.get_dom_document().get_element_by_id("ui_time").get_value()
        time_type = webFrame.get_dom_document().get_element_by_id("ui_time_type").get_value()
        # se utiliza scheme y path para evitar un loop
        if scheme == 'admin' and path == "preferences":
            if time and route:
                # vuelve a cargar los datos del usuario
                user = self.returnUserData()
                if user["time_type"] == "dias":
                    options = '<option class="form-scanda" value="dias">Dias</option>' \
                              '<option class="form-scanda" value="horas">Horas</option>'
                else:
                    options = '<option class="form-scanda" value="horas">Horas</option>' \
                              '<option class="form-scanda" value="dias">Dias</option>'

                # vuelve a cargar la vista de settings
                fd = open(self.LOCATION + "/gui/settings.html", "r")
                tmp_page = fd.read()
                fd.close()

                # REemplaza los datos del usuario
                tmp_page = tmp_page.replace("{user}", str(user['user']))
                tmp_page = tmp_page.replace("{space}", str(user['space']))
                tmp_page = tmp_page.replace("{space-available}", str(user['freeSpace']))
                tmp_page = tmp_page.replace("{space-used}", str(user['spaceUsed']))
                tmp_page = tmp_page.replace("{path}", str(user['path']))
                tmp_page = tmp_page.replace("{time}", str(user['time']))
                tmp_page = tmp_page.replace("{time_type}", str(options))

                # Escribe los datos
                if self.writePreferences(route, time, time_type):
                    # reemplaza alert con un mensaje
                    tmp_page = tmp_page.replace("{alert}", '<div class="tile-wrap">'
                                                           '<div class="tile tile-collapse tile-brand">'
                                                           '<div data-target="#ui_tile_example_red" data-toggle="tile">'
                                                           '<div class="tile-inner">'
                                                           '<div class="text-overflow">Cambios guardados correctamente</div>'
                                                           '</div>'
                                                           '</div>'
                                                           '</div>'
                                                           '</div>')

                    webview.load_html_string(tmp_page, self.LOCATION + '/html/')
                    return True
                else:
                    # reemplaza alert con un mensaje
                    tmp_page = tmp_page.replace("{alert}", '<div class="tile-wrap">'
                                                           '<div class="tile tile-collapse tile-red">'
                                                           '<div data-target="#ui_tile_example_red" data-toggle="tile">'
                                                           '<div class="tile-inner">'
                                                           '<div class="text-overflow">Ocurrio un error al guardar los datos</div>'
                                                           '</div>'
                                                           '</div>'
                                                           '</div>'
                                                           '</div>')

                    webview.load_html_string(tmp_page, self.LOCATION + '/html/')
                    return True
        elif scheme == 'admin' and path == "getRecover":
            print "saliendo"
            Gtk.main_quit()
            return True

    def returnUserData(self):
        log = SetLog()
        # Datos del usuario
        l = Login()
        user = l.returnUserData()  # Url de la api REST para autenticarse
        url = 'http://201.140.108.22:2017/DBProtector/Account_GET?User=' + user['user'] + '&Password=' + user[
            'password']
        try:
            # Realiza la peticion
            req = urllib2.Request(url)
            response = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            log.newLog("http_error", "E", e.fp.read())
        # Devuelve la info
        res = json.loads(response.read())
        # Si el inicio de sesion es correcto
        if res['Success'] == 1:
            # si  StorageLimit == -1 el espacio es Ilimitado
            if res['StorageLimit'] == -1:
                user['space'] = "Ilimitado"
                user['freeSpace'] = "Ilimitado"
            else:
                user['space'] = res['StorageLimit']
                user['freeSpace'] = res['StorageLimit'] - res['UsedStorage']
            user['spaceUsed'] = res['UsedStorage']
        else:
            log.newLog("login_api_error", "E", "")
        # devuelve todos los datos del usuario
        return user

    def preferences(self):
        # Extrae los datos del usuario y los reemplaza en la vista
        user = self.returnUserData()
        if user["time_type"] == "dias":
            options = '<option class="form-scanda" value="dias">Dias</option>' \
                      '<option class="form-scanda" value="horas">Horas</option>'
        else:
            options = '<option class="form-scanda" value="horas">Horas</option>' \
                      '<option class="form-scanda" value="dias">Dias</option>'
        data = {
            "user": user['user'],
            "space": user["space"],
            "space-available": user['freeSpace'],
            "space-used": user["spaceUsed"],
            "path": user["path"],
            "time": user["time"],
            "time_type": options,
            "alert": ""
        }
        # carga la vista
        HTML = self.LOCATION + "/gui/settings.html"
        win = Ui(HTML, data)
        win.set_default_size(800, 600)
        win.set_position(Gtk.WindowPosition.CENTER)
        win.connect("delete-event", Gtk.main_quit)
        win.view.connect("navigation-requested", self.preferencesClicked)
        win.show_all()
        Gtk.main()

app = Preferences()
app.preferences()
