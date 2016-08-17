#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import pygtk
pygtk.require('2.0')
import gtk
from xamai.Gui import Gui
from xamai.Status import Status
import xamai.Constants as const

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
        s = Status()
        statusUpload  = s.getUploadStatus()
        statusDownload = s.getDownloadStatus()

        self.menu = gtk.Menu()
        # Items del menu
        recover = gtk.MenuItem()
        recover.set_label('Recuperar respaldo')
        settings = gtk.MenuItem()
        settings.set_label('Configuración')
        sync = gtk.MenuItem()
        sync.set_label('Sincronizar ahora')
        statusMenu = gtk.MenuItem()
        separator = gtk.SeparatorMenuItem()

        # Activa el item, y le asigna le accion que realizara
        recover.connect("activate", self.setActionMenu, 1)
        settings.connect("activate", self.setActionMenu, 2)
        sync.connect("activate", self.setActionMenu, 3)

        # si se encuentra sincronizado
        if statusUpload['status'] == 0 and statusDownload['status'] == 0:
            statusMenu.set_label("Sincronizado")
        # si esta subiendo y descargando al mismo tiempo
        elif statusUpload['status'] != 0 and statusDownload['status'] == 1:
            if statusUpload['status'] == 1:
                statusMenu.set_label("Subiendo " + statusUpload['chunk'] + "% / Descargando " + statusDownload['file'])
            elif statusUpload['status'] == 2:
                #self.icon.set_from_file("img/sync.png")
                statusMenu.set_label("Descargando " + statusDownload['file'])
            elif statusUpload['status'] == 3:
                statusMenu.set_label("Cifrando archivo / Descargando " + statusDownload['file'])
        # si esta subiendo y descargando al mismo tiempo (si esta descomprimiendo el archivo)
        elif statusUpload['status'] != 0 and statusDownload['status'] == 2:
            if statusUpload['status'] == 1:
                statusMenu.set_label(
                    "Subiendo " + statusUpload['chunk'] + "% / Descifrando " + statusDownload['file'])
            elif statusUpload['status'] == 2:
                # self.icon.set_from_file("img/sync.png")
                statusMenu.set_label("Descifrando " + statusDownload['file'])
            elif statusUpload['status'] == 3:
                statusMenu.set_label("Cifrando archivo / Descifrando " + statusDownload['file'])
        # si esta subiendo, pero no descargando
        else:
            if statusUpload['status'] != 0:
                if statusUpload['status'] == 1:
                    statusMenu.set_label("Subiendo " + statusUpload['file'] + " " + statusUpload['chunk'] + "%")
                elif statusUpload['status'] == 2:
                    #self.icon.set_from_file("img/sync.png")
                    statusMenu.set_label("Sincronizado")
                elif statusUpload['status'] == 3:
                    statusMenu.set_label("Cifrando " + statusUpload['file'] + " para subir")
            if statusDownload['status'] == 1:
                statusMenu.set_label("Descargando " + statusDownload['file'])
            if statusDownload['status'] == 2:
                statusMenu.set_label("Descifrando " + statusDownload['file'])

        # Agrega los items al menu
        self.menu.append(recover)
        self.menu.append(settings)
        self.menu.append(sync)
        self.menu.append(separator)
        self.menu.append(statusMenu)

        # Muestra el menu
        self.menu.show_all()

        # Crea el popup
        #self.menu.popup(None, None, None, button, time, icon)
        self.menu.popup(None, None, None, None, 0, gtk.get_current_event_time())

    # abre una nueva interfaz
    def setActionMenu(self, widget, action):
        if action == 1 or action == 2:
            get = Gui()
            if action == 1:
                get.recover()
            elif action == 2:
                get.preferences()
        elif action == 3:
            os.system('/usr/bin/dbprotector_sync')

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
            self.icon = gtk.StatusIcon()
            self.icon.set_from_file(icon_file)

    def main(self):
        gtk.main()
