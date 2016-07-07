#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pygtk
import gtk
import sys
import os
import json

pygtk.require('2.0')
gtk.gdk.threads_init()

class Preferences():
	dir_path = '/'
	time = 0
	value = 0
	pw = ""
	CONFIG_FILE = "settings/configuration.json"
	LOCATION = os.path.dirname(os.path.realpath(__file__))

	# Accion: Salir
	def salir(self):
		print 'Cerrando...'
		gtk.main_quit()

	# Recupera el texto del Entry y lo almacena en la configuracion
	def getPath(widget, entry):
		entry_text = entry.get_text()

	# Escribe los datos de configuracion del usuario en el archivo JSON
	def writePath(self, arg):
		# Carga el archivo configuration.json
		file = os.path.join(self.LOCATION, self.CONFIG_FILE)

		# Estrae el nuevo valor de path
		global dir_path
		new_path = dir_path.get_text()

		# Si el archivo existe...
		if ( os.path.exists(file) ):
			# abre el archivo y guarda la variable 'time' del archivo json
			with open(file, 'r') as f:
				data = json.load(f)
			# Si la variable de time es nula, entonces la setea en 0
			if not data['time']:
				data['time'] = 0
			# Si la variable de time_type es nula, entonces la setea en 0
			if not data['time_type']:
				data['time_type'] = "horas"
			# escribe la nueva variable path en el archivo json junto con la time
			with open(self.CONFIG_FILE, 'w') as f:
				json.dump({
					'path': new_path,
					'time': data['time'],
					'time_type': data['time_type'],
					'IdCustomer': data['IdCustomer'],
					'user': data['user'],
					'password': data['password'],
					'tokenDropbox': data['tokenDropbox'],
				}, f)
		else :
			print "Ocurrio un error al guardar la configuracion"
		# Cierra la ventana
		pw.destroy()

	# Ventana para configurar las preferencias del usuario
	def preferencesPath(self, widget = None, data = None):
		# Crea una nueva ventana
		global pw
		pw = gtk.Window()
		pw.set_position(gtk.WIN_POS_CENTER)
		pw.set_size_request(600, 100)
		pw.set_title("Configuración")
		pw.set_resizable(False);

		# Contenedores VBox & HBox
		vbox = gtk.VBox()
		hbox = gtk.HBox()
		hbox_buttons = gtk.HBox()
		pw.add(vbox)
		vbox.pack_start(hbox, fill = False)
		vbox.pack_start(hbox_buttons, fill = False)

		# Crea un Entry para almacenar la ruta de los respaldos
		global dir_path
		dir_path = gtk.Entry()
		# Asigna un Listener a la funcion saveText
		dir_path.connect("activate", self.getPath, dir_path)
		# Obtiene el directorio "HOME" del usuario y lo muestra
		from os.path import expanduser
		# Extrae el valor de path del archivoi de configuracion
		location_ = os.path.join(self.LOCATION, "../")
		file = os.path.join(self.LOCATION, self.CONFIG_FILE)
		# si el archivo existe...
		if ( os.path.exists(file) ):
			with open(file, 'r') as f:
				data = json.load(f)

		home = data['path']
		# Si home es null, entonces le asigna el dir HOME
		if not home:
			home = expanduser("~")
		# Coloca la varialble home
		dir_path.set_text(data['path'])
		# Agregar el Entry al contenedor y muestra el widget
		hbox.pack_start(dir_path, gtk.TRUE, gtk.TRUE, 0)
		dir_path.show()

		# Crea un Boton para seleccionar una nueva ruta
		button = gtk.Button("Seleccionar")
		# Cuando se presiona llama la funcion selectDir
		button.connect_object("clicked", self.selectPath, pw)
		hbox.pack_start(button, gtk.TRUE, gtk.TRUE, 0)
		button.set_flags(gtk.CAN_DEFAULT)
		button.grab_default()
		button.show()

		'''
		# Style
		map = button.get_colormap()
		color = map.alloc_color("red")

		# copy the current style and replace the background
		style = button.get_style().copy()
		style.bg[gtk.STATE_NORMAL] = color

		# set the button's style to the one you created
		button.set_style(style)
		'''
		# Boton de guardar
		button_save = gtk.Button("Guardar")
		button_save.connect_object("clicked", self.writePath, self)
		button_save.show()
		hbox_buttons.pack_start(button_save, gtk.TRUE, gtk.FALSE, 0)

		vbox.show()
		hbox.show()
		hbox_buttons.show()
		pw.show()

	def selectPath(self, arg):
		# Crea un dialogo para seleccionar la nueva ruta
		dialog = gtk.FileChooserDialog("Seleccionar un Directorio",
			None,
			# Solo se pueden seleccionar directorios
			gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
			(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
				gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		dialog.set_default_response(gtk.RESPONSE_OK)

		# Solo se pueden seleccionar directorios
		filtro = gtk.FileFilter()
		filtro.set_name("Folder")
		filtro.add_pattern("/")
		dialog.add_filter(filtro)

		response = dialog.run()
		# Si se presiona el Boton ok, coloca la ruta en el Entry
		if response == gtk.RESPONSE_OK:
			dir_path.set_text(dialog.get_filename())
		# Si se presiona el boton Cancel, coloca '/' en el Entry
		elif response == gtk.RESPONSE_CANCEL:
			dir_path.set_text('/')
		dialog.destroy()

	# Metodos de configuracion de tiempo
	# Guarda la opcion seleccionada en el ComboBox
	def saveTimeType(self, combobox):
		model = combobox.get_model()
		index = combobox.get_active()
		if index:
			self.value = model[index][0]
		return

	# Escribe los datos de configuracion del usuario en el archivo JSON
	def writeTime(self, args):
		# Carga el archivo configuration.json
		file = os.path.join(self.LOCATION, self.CONFIG_FILE)
		# Si el archivo existe...
		if (os.path.exists(file)):
			# abre el archivo y guarda la variable 'path' del archivo json
			with open(file, 'r') as f:
				data = json.load(f)
			# Si la variable de path es nula, entonces la setea en /
			if not data['path']:
				data['path'] = "/"
			# escribe la nueva variable time en el archivo json junto con la variable value
			with open(self.CONFIG_FILE, 'w') as f:
				json.dump({
					'path': data['path'],
					'time': self.time,
					'time_type': self.value,
					'IdCustomer': data['IdCustomer'],
					'user': data['user'],
					'password': data['password'],
					'tokenDropbox': data['tokenDropbox'],
				}, f)
		else:
			print "Ocurrio un error al guardar la configuracion"

	def timeValidation(self, btn, args):
		global dir_path
		self.time = dir_path.get_value_as_int()

		if self.value == "minutos":
			if self.time > 59:
				self.time = 59
			elif self.time < 0:
				self.time = 0
		elif self.value == "horas":
			if self.time > 23:
				self.time = 23
			elif self.time < 0:
				self.time = 0
		elif self.value == "dias":
			if self.time > 31:
				self.time = 31
			elif self.time < 1:
				self.time = 1
		else:
			self.value = "horas"
			self.time = self.time
		# Escribe los cambios
		self.writeTime(self)
		# Cierra la ventana
		pw.destroy()

	# Ventana para configurar las preferencias del usuario
	def preferencesTime(self, widget=None, data=None):
		# Crea una nueva ventana
		global pw
		pw = gtk.Window()
		pw.set_position(gtk.WIN_POS_CENTER)
		pw.set_size_request(300, 100)
		pw.set_title("Configuración")
		pw.set_resizable(False);

		# Contenedores VBox & HBox
		vbox = gtk.VBox()
		hbox = gtk.HBox()
		hbox_buttons = gtk.HBox()
		pw.add(vbox)
		vbox.pack_start(hbox, fill=False)
		vbox.pack_start(hbox_buttons, fill=False)

		# Carga el valor del tiempo de respaldo del archivo de configuracion
		# Carga el archivo configuration.json
		file = os.path.join(self.LOCATION, self.CONFIG_FILE)
		time_backup = 0
		time_backup_type = "dias"
		# Si el archivo existe...
		if (os.path.exists(file)):
			# abre el archivo y guarda la variable 'path' del archivo json
			with open(file, 'r') as f:
				data = json.load(f)
			# Si la variable de path es nula, entonces la setea en /
			if not data['time']:
				data['time'] = 7.0
			if not data['time_type']:
				data['time_type'] = "dias"
			time_backup = data['time']
			time_backup_type = data['time_type']
		else:
			print "Ocurrio un error al guardar la configuracion"

		# Crea un Entry para almacenar el tiempo de repaldos
		global dir_path
		adj = gtk.Adjustment(time_backup, 0.0, 365.0, 1.0, 100.0, 0.0)
		dir_path = gtk.SpinButton(adj, 0, 0)
		dir_path.set_wrap(True)
		# dir_path.set_text("168")
		# Agregar el Entry al contenedor y muestra el widget
		hbox.pack_start(dir_path, gtk.TRUE, gtk.TRUE, 0)
		dir_path.show()

		if time_backup_type == "minutos":
			time_backup_type = 1
		elif time_backup_type == "horas":
			# time_backup_type = 2
			time_backup_type = 1
		elif time_backup_type == "dias":
			#time_backup_type = 3
			time_backup_type = 2
		else:
			time_backup_type = 0

		# Crea un Boton para seleccionar una nueva ruta
		combobox = gtk.combo_box_new_text()
		hbox.pack_start(combobox, gtk.TRUE, gtk.TRUE, 0)
		combobox.append_text('')
		#combobox.append_text('minutos')
		combobox.append_text('horas')
		combobox.append_text('dias')
		combobox.connect('changed', self.saveTimeType)
		combobox.set_active(time_backup_type)
		combobox.show()

		button_save = gtk.Button("Guardar")
		button_save.connect_object("clicked", self.timeValidation, pw, self)
		button_save.show()

		hbox_buttons.pack_start(button_save, gtk.TRUE, gtk.FALSE, 0)

		vbox.show()
		hbox.show()
		hbox_buttons.show()
		pw.show()

	def main(self):
		self.LOCATION = os.path.dirname(os.path.realpath(__file__))
		self.CONFIG_FILE = "settings/configuration.json"
		self.value = ""
		self.time = 0.0