#!/usr/bin/env python
# -*- coding: utf-8 -*-
import gtk
import pygtk

pygtk.require('2.0')
gtk.gdk.threads_init()

import os
import Preferences as p
#import Login as l

class Scanda():
	# Nombre del icono que se mostrara en el panel
	ICONO = 'img/icon.png'

	# Constructor
	def __init__(self):
		# Almacena la ruta actual del script
		self.location = os.path.dirname(os.path.realpath(__file__))
		# Crea el icono
		self.set_icon()
		# Asigna el "listener" al boton izquierdo
		#self.icon.connect('activate', self.icon_click)
		# Asigna el "listener" al boton derecho
		self.icon.connect("popup-menu", self.set_menu)
		# Asigna nombre del applet
		self.icon.set_title('SCANDA')
		self.icon.set_name('SCANDA')
		self.icon.set_tooltip('SCANDA')
		# Muestra el icono
		self.icon.set_visible(True)

	# Cada vez que se da click derecho en el icono despliega un menu popup
	def set_menu(self, icon, button, time):
		self.menu = gtk.Menu()

		# Items del menu
		recover = gtk.MenuItem()
		recover.set_label('Recuperar respaldo')
		route = gtk.MenuItem()
		route.set_label('Ruta de respaldos')
		timeout = gtk.MenuItem()
		timeout.set_label('Respaldar cada')
		about = gtk.MenuItem()
		about.set_label('Sincronizar ahora')
		loginMenu = gtk.MenuItem()
		loginMenu.set_label('Iniciar Sesión')
		status = gtk.MenuItem()
		status.set_label('Cargando archivo')

		quit = gtk.MenuItem()
		quit.set_label('Salir')

		# Activa el item, y le asigna le accion que realizara
		# Descomentar
		action = p.Preferences()
		#login = l.Login()
		#recover.connect("activate", mr.recover)
		timeout.connect("activate", action.preferencesTime)
		route.connect("activate", action.preferencesPath)
		#loginMenu.connect("activate", login.loginMain)
		quit.connect("activate", action.salir)

		# Agrega los items al menu
		self.menu.append(recover)
		self.menu.append(route)
		self.menu.append(timeout)
		self.menu.append(about)
		self.menu.append(loginMenu)
		#if upload
		#while upload:
			#status.set_label('Cargando archivo')
		#	pass
		#self.menu.append(quit)

		# Muestra el menu
		self.menu.show_all()

		# Crea el popup
		self.menu.popup(None, None, gtk.status_icon_position_menu, button, time, icon)

	# Esta funcion sera la que coloque el icono en el panel
	def set_icon(self):
		# Crea la ruta del icono
		icon_file = os.path.join(self.location, self.ICONO)
		# Valida que exista el icono
		assert os.path.exists(icon_file), 'No se encontro el archivo: %s' % icon_file
		# Valida si existe icon dentro de la clase
		if hasattr(self, 'icon'):
			# Si existe, solo actualiza el icono
			self.icon.set_from_file(icon_file)
		else:
			# Si no existe, crea uno nuevo y agrega el icono
			self.icon = gtk.status_icon_new_from_file(icon_file)

	def main(self):
		gtk.main()

# Comentar a nivel de produccion
app = Scanda()
app.main()