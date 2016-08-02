#!/usr/bin/env python
# -*- coding: utf-8 -*-
import gi
gi.require_version('Gtk', '3.0')
# only in opensuse comment this line
gi.require_version('WebKit', '3.0')
import thread
from gi.repository import Gtk
from scanda.WebK import WebK
import scanda.Constants as const

'''
    La interfaz grafica crea un webkit (WebK) y carga las vistas en /scanda/gui/*.html
    La clase Gui se encarga de cargar las vistas y crear los listeners
    usados para ejecutar las acciones de la aplicacion
'''
class GUI():
    # ---------- GUI.py's  ----------
    # Muestra el inicio de sesion
    def login(self):
        data = {
            "css": self.loadStyles(),
            "alert": ""
        }
        HTML = const.LOCATION + "/gui/login.html"
        win = WebK(HTML, data)
        win.set_default_size(800, 600)
        win.set_position(Gtk.WindowPosition.CENTER)
        win.connect("delete-event", Gtk.main_quit)
        win.view.connect("navigation-requested", self.clickedListener)
        win.show_all()
        Gtk.main()

    # Muestra una lista de respaldos
    def recover(self):
        from scanda.Recover import Recover
        r = Recover()
        data = {
            "goBakcButton": '',
            "card": r.loadYears(),
            "msg": ""
        }
        # carga la vista
        HTML = const.LOCATION + "/gui/index.html"
        win = WebK(HTML, data)
        win.set_default_size(800, 600)
        win.set_position(Gtk.WindowPosition.CENTER)
        win.connect("delete-event", Gtk.main_quit)
        win.view.connect("navigation-requested", self.clickedListener)
        win.show_all()
        Gtk.main()

    # Muestra la configuracion y detalles de la cuenta del usuario
    def preferences(self):
        from scanda.Preferences import Preferences
        p = Preferences()

        # Extrae los datos del usuario y los reemplaza en la vista
        user = p.returnUserData()
        # no sera visible en esta version
        if user["time_type"] == "dias":
            options = '<option class="form-scanda" value="dias">Dias</option>' \
                      '<option class="form-scanda" value="horas">Horas</option>'
        else:
            options = '<option class="form-scanda" value="horas">Horas</option>' \
                      '<option class="form-scanda" value="dias">Dias</option>'

        if user['space'] == -1:
            user['space'] = "Ilimitado"
            espacioLibre = "Ilimitado"
            espacioUsado = user['spaceUsed'] + " MB"
        else:
            espacioLibre = p.returnPercent(int(user['space']), int(user['freeSpace'])) + "%"
            espacioUsado = p.returnPercent(int(user['space']), int(user['spaceUsed'])) + "%"
            user['space'] = str(user['space']) + " MB"

        data = {
            "userPath": str(p.showExternalPath()),
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
        HTML = const.LOCATION + "/gui/settings.html"
        win = WebK(HTML, data)
        win.set_default_size(800, 600)
        win.set_position(Gtk.WindowPosition.CENTER)
        win.connect("delete-event", Gtk.main_quit)
        win.view.connect("navigation-requested", self.clickedListener)
        win.show_all()
        Gtk.main()

    '''
        Listener's, cada vez que sucede una redireccion en la GUI.py
    '''
    def clickedListener(self, webview, webFrame, networkRequest):
        uri = networkRequest.get_uri()
        if uri.find("://") > 0:
            scheme, path = uri.split("://", 1)
        else:
            return False
        '''
            se utiliza scheme y path para evitar un loop
            todos los schme's deben ser bajo admin
            si el path es preferences guarda los cambios del usuario
            y recarga la página
        '''
        if scheme == 'admin' and path == "preferences":
            from scanda.Preferences import Preferences
            p = Preferences()
            # extrae path y frecuencia de respaldo de los forms HTML
            route = webFrame.get_dom_document().get_element_by_id("ui_path").get_value()
            time = webFrame.get_dom_document().get_element_by_id("ui_time").get_value()
            userPath = webFrame.get_dom_document().get_element_by_id("ui_path_external").get_value()
            if route:
                # vuelve a cargar los datos del usuario
                user = p.returnUserData()
                if user["time_type"] == "dias":
                    options = '<option class="form-scanda" value="dias">Dias</option>' \
                              '<option class="form-scanda" value="horas">Horas</option>'
                else:
                    options = '<option class="form-scanda" value="horas">Horas</option>' \
                              '<option class="form-scanda" value="dias">Dias</option>'

                # vuelve a cargar la vista de settings
                fd = open(const.LOCATION + "/gui/settings.html", "r")
                tmp_page = fd.read()
                fd.close()

                # Ajusta los datos a porcentajes
                if user['space'] == -1:
                    user['space'] = "Ilimitado"
                    espacioLibre = "Ilimitado"
                    espacioUsado = user['spaceUsed'] + " MB"
                else:
                    espacioLibre = p.returnPercent(int(user['space']), int(user['freeSpace'])) + "%"
                    espacioUsado = p.returnPercent(int(user['space']), int(user['spaceUsed'])) + "%"
                    user['space'] = str(user['space']) + " MB"

                # REemplaza los datos del usuario
                tmp_page = tmp_page.replace("{userPath}", str(p.showExternalPath()))
                tmp_page = tmp_page.replace("{user}", str(user['user']))
                tmp_page = tmp_page.replace("{space}", str(user['space']))
                tmp_page = tmp_page.replace("{space-available}", espacioLibre)
                tmp_page = tmp_page.replace("{space-used}", espacioUsado)
                tmp_page = tmp_page.replace("{path}", str(user['path']))
                tmp_page = tmp_page.replace("{time}", str(user['time']))
                tmp_page = tmp_page.replace("{time_type}", str(options))

                # Escribe los datos
                '''
                    en esta version se usara por defecto el tipo de frecuencia como días,
                    si se permite al usuario configurarlo, solo hay que cambiarlo por la
                    variable time_type
                '''
                #if p.writePreferences(route, time, time_type):
                if p.writePreferences(route, time, "dias", userPath):
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

                    webview.load_html_string(tmp_page, const.LOCATION + '/html/')
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

                    webview.load_html_string(tmp_page, const.LOCATION + '/html/')
                    return True
        # Redirecciona a los respaldos del usuario
        elif scheme == 'admin' and path == "getRecover":
            webview.load_html_string(self.loadRecover(), const.LOCATION + '/html/')
            return True
        # inicia session
        elif scheme == 'admin' and path == "login":
            from scanda.Login import Login
            l = Login()

            # extrae usuario y contrasena
            user = webFrame.get_dom_document().get_element_by_id("ui_login_username").get_value()
            password = webFrame.get_dom_document().get_element_by_id("ui_login_password").get_value()

            if user and password:
                # Si el login es correcto
                if l.loginApi(user, password):
                    webview.load_html_string(self.loadPreferences(), const.LOCATION + '/html/')
                    from scanda.Scanda import Scanda
                    app = Scanda()
                    app.main()
                    return True
                # Si el login NO es correcto
                else:
                    # vuelve a cargar la vista de login
                    fd = open(const.LOCATION + "/gui/login.html", "r")
                    tmp_page = fd.read()
                    fd.close()
                    # reemplaza alert con un mensaje de usuario incorrecto
                    tmp_page = tmp_page.replace("{css}", self.loadStyles())
                    tmp_page = tmp_page.replace("{alert}", '<div class="tile-wrap">'
                                                           '<div class="tile tile-collapse tile-red">'
                                                           '<div data-target="#ui_tile_example_red" data-toggle="tile">'
                                                           '<div class="tile-inner">'
                                                           '<div class="text-overflow">Usuario o Contraseña incorrectos</div>'
                                                           '</div>'
                                                           '</div>'
                                                           '</div>'
                                                           '</div>')
                    webview.load_html_string(tmp_page, const.LOCATION + '/html/')
                    return True
        # Muestra la lista de anios disponibles en los respaldos
        elif scheme == 'admin' and path == "recover":
            from scanda.Recover import Recover
            r = Recover()
            # Extrae el anio seleccionado
            year = webFrame.get_dom_document().get_element_by_id("card_clicked").get_value()
            # vuelve a cargar la vista de index
            fd = open(const.LOCATION + "/gui/index.html", "r")
            tmp_page = fd.read()
            fd.close()

            tmp_page = tmp_page.replace("{goBakcButton}", '<a class="btn waves-attach" onclick="getRecover(true)"><span class="icon icon-lg margin-right">undo</span>volver</a>')
            tmp_page = tmp_page.replace("{card}", r.loadMonths(year))
            tmp_page = tmp_page.replace("{msg}", "")
            webview.load_html_string(tmp_page, const.LOCATION + '/html/')
            return True
        # Muestra los meses de un anio
        elif scheme == 'admin' and path == "recoverMonth":
            from scanda.Recover import Recover
            r = Recover()
            # extrae el mes y anio seleccionado
            val = webFrame.get_dom_document().get_element_by_id("card_clicked").get_value()
            y, m = val.split("-")
            # vuelve a cargar la vista de index
            fd = open(const.LOCATION + "/gui/index.html", "r")
            tmp_page = fd.read()
            fd.close()

            tmp_page = tmp_page.replace("{goBakcButton}", '<a class="btn waves-attach" onclick="getRecover(true)"><span class="icon icon-lg margin-right">undo</span>volver</a>')
            tmp_page = tmp_page.replace("{card}", r.loadBackups(y, m))
            tmp_page = tmp_page.replace("{msg}", "")
            webview.load_html_string(tmp_page, const.LOCATION + '/html/')
            return True
        # Reabre la lista de respaldos, una vez que se descargo uno
        elif scheme == 'admin' and path == "downloadBackup":
            from scanda.Recover import Recover
            from scanda.Upload import Upload
            u = Upload()
            r = Recover()
            # Extrae el respaldo seleccionado
            backup = webFrame.get_dom_document().get_element_by_id("card_clicked").get_value()
            # vuelve a cargar la vista de index
            fd = open(const.LOCATION + "/gui/index.html", "r")
            tmp_page = fd.read()
            fd.close()

            # Descarga el archivo en un nuevo thread de forma paralela
            thread.start_new_thread(u.downloadFile, (u.getData(), r.downloadFile(backup),))
            #print r.downloadFile(backup)

            # Recupera anio y mes
            y, m, file = backup.split("-")
            # Remplaza los parametros
            tmp_page = tmp_page.replace("{goBakcButton}",
                                        '<a class="btn waves-attach" onclick="getRecover(true)"><span class="icon icon-lg margin-right">undo</span>volver</a>')
            tmp_page = tmp_page.replace("{card}", r.loadBackups(y, m))
            tmp_page = tmp_page.replace("{msg}", '<div class="tile-wrap">'
                                                 '<div class="tile tile-collapse tile-brand">'
                                                 '<div data-target="#ui_tile_example_red" data-toggle="tile">'
                                                 '<div class="tile-inner">'
                                                 '<div class="text-overflow">Descargando respaldo: ' + file + '</div>'
                                                                                                              '</div>'
                                                                                                              '</div>'
                                                                                                              '</div>')
            # vuelve a cargar la vista                                                                                                  '</div>')
            webview.load_html_string(tmp_page, const.LOCATION + '/html/')
            return True
        # Redirecciona a las preferencias del usuario
        elif scheme == 'admin' and path == "getSettings":
            webview.load_html_string(self.loadPreferences(), const.LOCATION + '/html/')
            return True
        # Vuelve a cargar los respaldos
        elif scheme == 'admin' and path == "getBackups":
            webview.load_html_string(self.loadRecover(), const.LOCATION + '/html/')
            return True
    '''
        Loader's
        Activa las funciones de los items del menu items
    '''
    # Redirecciona a las preferencias del usuario
    def loadPreferences(self):
        from scanda.Preferences import Preferences
        p = Preferences()
        # Carga los datos del usuario
        user = p.returnUserData()

        if user["time_type"] == "dias":
            options = '<option class="form-scanda" value="dias">Dias</option>' \
                '<option class="form-scanda" value="horas">Horas</option>'
        else:
            options = '<option class="form-scanda" value="horas">Horas</option>' \
                '<option class="form-scanda" value="dias">Dias</option>'

        # vuelve a cargar la vista de settings
        fd = open(const.LOCATION + "/gui/settings.html", "r")
        tmp_page = fd.read()
        fd.close()

        # Ajusta los datos a porcentajes
        if user['space'] == -1:
            user['space'] = "Ilimitado"
            espacioLibre = "Ilimitado"
            espacioUsado = user['spaceUsed'] + " MB"
        else:
            espacioLibre = p.returnPercent(int(user['space']), int(user['freeSpace'])) + "%"
            espacioUsado = p.returnPercent(int(user['space']), int(user['spaceUsed'])) + "%"
            user['space'] = str(user['space']) + " MB"

        # REemplaza los datos del usuario
        tmp_page = tmp_page.replace("{userPath}", str(p.showExternalPath()))
        tmp_page = tmp_page.replace("{user}", str(user['user']))
        tmp_page = tmp_page.replace("{space}", str(user['space']))
        tmp_page = tmp_page.replace("{space-available}", espacioLibre)
        tmp_page = tmp_page.replace("{space-used}", espacioUsado)
        tmp_page = tmp_page.replace("{path}", str(user['path']))
        tmp_page = tmp_page.replace("{time}", str(user['time']))
        tmp_page = tmp_page.replace("{time_type}", str(options))
        tmp_page = tmp_page.replace("{alert}", "")

        return tmp_page

    # Redirecciona a los respaldos del usuario
    def loadRecover(self):
        from scanda.Recover import Recover
        r = Recover()
        data = {
            "card": r.loadYears()
        }

        # vuelve a cargar la vista de settings
        fd = open(const.LOCATION + "/gui/index.html", "r")
        tmp_page = fd.read()
        fd.close()

        tmp_page = tmp_page.replace("{goBakcButton}", '')
        tmp_page = tmp_page.replace("{card}", data['card'])
        tmp_page = tmp_page.replace("{msg}", "")

        return tmp_page

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
