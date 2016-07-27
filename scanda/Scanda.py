#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import gi
from scanda.Ui import GUI
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import scanda.Constants as const

class Scanda():
    # Constructor
    def __init__(self):
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
        from scanda.Status import Status
        s = Status()
        status  = s.getDownloadStatus()

        self.menu = Gtk.Menu()
        # Items del menu
        recover = Gtk.MenuItem()
        recover.set_label('Recuperar respaldo')
        settings = Gtk.MenuItem()
        settings.set_label('Configuración')
        sync = Gtk.MenuItem()
        sync.set_label('Sincronizar ahora')
        statusMenu = Gtk.MenuItem()

        # Activa el item, y le asigna le accion que realizara
        recover.connect("activate", self.setActionMenu, 1)
        settings.connect("activate", self.setActionMenu, 2)
        sync.connect("activate", self.setActionMenu, 3)

        if status['status'] == 1:
            statusMenu.set_label("Subiendo " + status['file'] + " " + status['chunk'] + "%")
        elif status['status'] == 2:
            statusMenu.set_label(status['file'] + " sincronizado")
        else:
            statusMenu.set_label("Sincronizado")

        # Agrega los items al menu
        self.menu.append(recover)
        self.menu.append(settings)
        self.menu.append(sync)
        self.menu.append(statusMenu)

        # Muestra el menu
        self.menu.show_all()

        # Crea el popup
        #self.menu.popup(None, None, None, button, time, icon)
        self.menu.popup(None, None, None, None, 0, Gtk.get_current_event_time())

    # abre una nueva interfaz
    def setActionMenu(self, widget, action):
        if action == 1 or action == 2:
            get = GUI()
            if action == 1:
                get.recover()
            elif action == 2:
                get.preferences()
        elif action == 3:
            os.system('/usr/bin/dbprotector_sync')

    # se utilizara para mostrar que se esta realizando una accion Subida / Descarga
    def setActionActive(self):
        download = Gtk.MenuItem()
        download.set_label('Recuperar respaldo')
        self.menu.append(download)

    # Esta funcion sera la que coloque el icono en el panel
    def set_icon(self):
        # Crea la ruta del icono
        icon_file = os.path.join(const.LOCATION, const.ICONO)
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