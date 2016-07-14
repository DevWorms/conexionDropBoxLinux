#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pygtk
import gi
import os

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
pygtk.require('2.0')

class Scanda():
    # Nombre del icono que se mostrara en el panel
    ICONO = 'img/icon.png'

    # Constructor
    def __init__(self):
        # Almacena la ruta actual del script
        self.location = os.path.dirname(os.path.realpath(__file__))
        # Crea el icono
        self.set_icon()
        # Asigna el "listener" al boton derecho
        self.icon.connect("popup-menu", self.set_menu)
        # Asigna nombre del applet
        self.icon.set_title('DBProtector')
        self.icon.set_name('DBProtector')
        self.icon.set_has_tooltip('DBProtector')
        # Muestra el icono
        self.icon.set_visible(True)

    # Cada vez que se da click derecho en el icono despliega un menu popup
    def set_menu(self, icon, button, time):
        self.menu = Gtk.Menu()

        # Items del menu
        recover = Gtk.MenuItem()
        recover.set_label('Recuperar respaldo')
        route = Gtk.MenuItem()
        route.set_label('Configuración')
        about = Gtk.MenuItem()
        about.set_label('Sincronizar ahora')
        status = Gtk.MenuItem()
        status.set_label('Cargando archivo')
        quit = Gtk.MenuItem()
        quit.set_label('Salir')

        # Activa el item, y le asigna le accion que realizara
        #action = p.Preferences()
        # login = l.Login()
        # recover.connect("activate", mr.recover)
        #timeout.connect("activate", action.preferencesTime)
        #route.connect("activate", action.preferencesPath)
        # loginMenu.connect("activate", login.loginMain)
        quit.connect("activate", Gtk.main_quit)

        # Agrega los items al menu
        self.menu.append(recover)
        self.menu.append(route)
        self.menu.append(about)
        self.menu.append(quit)

        # Muestra el menu
        self.menu.show_all()

        # Crea el popup
        #self.menu.popup(None, None, None, button, time, icon)
        self.menu.popup(None, None, None, None, 0, Gtk.get_current_event_time())

    # Esta funcion sera la que coloque el icono en el panel
    def set_icon(self):
        # Crea la ruta del icono
        icon_file = os.path.join("/home/rk521/PycharmProjects/conexionDropBoxLinux/src/", self.ICONO)
        # Valida que exista el icono
        assert os.path.exists(icon_file), 'No se encontro el archivo: %s' % icon_file
        # Valida si existe icon dentro de la clase
        if hasattr(self, 'icon'):
            # Si existe, solo actualiza el icono
            self.icon.set_from_file(icon_file)
        else:
            # Si no existe, crea uno nuevo y agrega el icono
            self.icon = Gtk.StatusIcon()
            self.icon.set_from_file(icon_file)

    def main(self):
        Gtk.main()

app = Scanda()
app.main()
