#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib
import json
import os
import urllib2

from Ui import Ui

class Login():
    CONFIG_FILE = "settings/configuration.json"
    LOCATION = os.path.dirname(os.path.realpath(__file__))

    # Este metodo devuelve un arreglo con la info almacenad en: configuration.json
    def returnUserData(self):
        #log = SetLog()
        # Carga el archivo configuration.json
        file = os.path.join(self.LOCATION, self.CONFIG_FILE)
        # Si el archivo existe...
        if (os.path.exists(file)):
            # abre el archivo y guarda la variable 'time' del archivo json
            with open(file, 'r') as f:
                data = json.load(f)
        #else:
            #log.newLog("load_config_file", "E", "Login.returnUserData()")
        return data

    # guarda los datos del usuario recibidos
    def writeUserData(self, user, password, id):
        #log = SetLog()
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
                    'path': data['path'],
                    'time': data['time'],
                    'time_type': data['time_type'],
                    'IdCustomer': id,
                    'user': user,
                    'password': password,
                    'tokenDropbox': data['tokenDropbox'],
                }, f)
        #else:
        #    log.newLog("load_config_file", "E", "")

    # Autenticacion con la api REST
    def loginApi(self, user, p_hash):
        #log = SetLog()

        # Url de la api REST para autenticarse
        url = 'http://201.140.108.22:2017/DBProtector/Login_GET?User=' + user + '&Password=' + p_hash

        try:
            # Realiza la peticion
            req = urllib2.Request(url)
            response = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            #log.newLog("http_error", "E", e.fp.read())
            print e
        # Devuelve la info
        res = json.loads(response.read())
        if res['Success'] == 1:
            if res['Status'] == 1:
                self.writeUserData(user, p_hash, res["IdCustomer"])
            else:
                print "No se pudo guardar la configuracion"
                #log.newLog("login_status_error" + res["Status"], "E", "")
            return True
        else:
            # log.newLog("login_api_error", "E", "")
            print "Usuario o Contrasena incorrectos"
            return False

    # Signal del login, se ejecuta cada vez que envia una peticion
    def loginClicked(self, webview, webFrame, networkRequest):
        uri = networkRequest.get_uri()
        if uri.find("://") > 0:
            scheme, path = uri.split("://", 1)
        else:
            return False

        # extrae usuario y contrasena
        user = webFrame.get_dom_document().get_element_by_id("ui_login_username").get_value()
        password = webFrame.get_dom_document().get_element_by_id("ui_login_password").get_value()
        # se utiliza scheme y path para evitar un loop
        if scheme == 'admin' and path == "login":
            if user and password:
                # Si el login es correcto
                if self.loginApi(user, password):
                    from Scanda import Scanda
                    import gi
                    gi.require_version('Gtk', '3.0')
                    from gi.repository import Gtk
                    Gtk.main_quit()
                    init = Scanda()
                    init.main()
                    return True
                # Si el login NO es correcto
                else:
                    # vuelve a cargar la vista de login
                    fd = open(self.LOCATION + "/gui/login.html", "r")
                    tmp_page = fd.read()
                    fd.close()
                    # reemplaza alert con un mensaje de usuario incorrecto
                    tmp_page = tmp_page.replace("{alert}", '<div class="tile-wrap">'
                                                           '<div class="tile tile-collapse tile-red">'
                                                           '<div data-target="#ui_tile_example_red" data-toggle="tile">'
                                                           '<div class="tile-inner">'
                                                           '<div class="text-overflow">Usuario o Contraseña incorrectos</div>'
                                                           '</div>'
                                                           '</div>'
                                                           '</div>'
                                                           '</div>')
                    webview.load_html_string(tmp_page, self.LOCATION + '/html/')
                    return True

    def loginMaterial(self):
        import gi
        gi.require_version('Gtk', '3.0')
        from gi.repository import Gtk

        data = {"alert": ""}
        HTML = self.LOCATION + "/gui/login.html"
        win = Ui(HTML, data)
        win.set_default_size(800, 600)
        win.set_position(Gtk.WindowPosition.CENTER)
        win.connect("delete-event", Gtk.main_quit)
        win.view.connect("navigation-requested", self.loginClicked)
        win.show_all()
        Gtk.main()

#login = Login()
#login.loginMaterial()