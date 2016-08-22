#!/usr/bin/env python
# -*- coding: utf-8 -*-
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class ChooseDirectory(Gtk.Window):
    def getFolder(self):
        dialog = Gtk.FileChooserDialog("Seleccione la carpeta de destino", self,
                                       Gtk.FileChooserAction.SELECT_FOLDER,
                                       ("Seleccionar", Gtk.ResponseType.OK))
        dialog.set_default_size(800, 400)
        dialog.run()
        path = dialog.get_filename()
        dialog.destroy()

        return path
