#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pygtk
import gtk
import sys
import os
import hashlib
import json
import urllib
import urllib2

pygtk.require('2.0')
gtk.gdk.threads_init()

class Login():
	pw = ""
	CONFIG_FILE = "settings/configuration.json"
	LOCATION = os.path.dirname(os.path.realpath(__file__))

	def returnUserData(self):
		# Carga el archivo configuration.json
		file = os.path.join(self.LOCATION, self.CONFIG_FILE)
		# Si el archivo existe...
		if (os.path.exists(file)):
			# abre el archivo y guarda la variable 'time' del archivo json
			with open(file, 'r') as f:
				data = json.load(f)
		else:
			print "Ocurrio un error al cargar el archivo de configuracion"
		return data

	# Autenticacion con la api REST
	def loginApi(self, user, p_hash):
		# Url de la api REST para autenticarse
		url = 'http://jsonplaceholder.typicode.com/posts'
		# Pasa el usuario y la contrasenia como parametros por POST
		values = {'title': user,
				'body': p_hash }
		# Headers de la peticion
		headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)' }
		# Crea la peticion
		data = urllib.urlencode(values)
		req = urllib2.Request(url, data, headers)

		try:
			# Realiza la peticion
			response = urllib2.urlopen(req)
		except urllib2.HTTPError, e:
			print "Error: " + e.fp.read()
		# Devuelve la info
		print response.read()
		#res = json.loads(response.read())

	# Extrae los datos
	def loginHash(self, widget, username, password):
		user = username.get_text()
		passw = password.get_text()
		#if (not user) or (not password)
		#	username.set_text("Ingresa un usuario")
		# Extrae la contrasenia y la pasa a un hash
		h = hashlib.new("sha256")
		h.update(passw)
		passw = h.hexdigest()
		self.loginApi(user, passw)
		#print "User: " + user + " Pass: " + passw + " Hash: " + h.hexdigest()

	# Ventana login
	def loginMain(self, widget = None, data = None):
		# Crea una nueva ventana
		global pw
		pw = gtk.Window()
		pw.set_position(gtk.WIN_POS_CENTER)
		pw.set_size_request(300, 240)
		pw.set_title("Iniciar Sesión")
		pw.set_resizable(False);

		# Contenedores VBox & HBox
		vbox = gtk.VBox()
		hbox_user = gtk.HBox()
		hbox_pass = gtk.HBox()
		hbox_btn = gtk.HBox()
		pw.add(vbox)
		vbox.pack_start(hbox_user, fill = False)
		vbox.pack_start(hbox_pass, fill = False)
		vbox.pack_start(hbox_btn, fill = False)

		# Username lanel & Entry
		username_label = gtk.Label("Usuario:")
		hbox_user.pack_start(username_label, gtk.TRUE, gtk.FALSE, 0)
		username_label.show()
		username_entry = gtk.Entry()
		hbox_user.pack_start(username_entry, gtk.TRUE, gtk.FALSE, 0)
		username_entry.show()

		# Password lanel & Entry
		password_label = gtk.Label("Contraseña:")
		hbox_pass.pack_start(password_label, gtk.TRUE, gtk.FALSE, 0)
		password_label.show()
		password_entry = gtk.Entry()
		hbox_pass.pack_start(password_entry, gtk.TRUE, gtk.FALSE, 0)
		password_entry.set_visibility(False)
		password_entry.show()

		# Button
		login_btn = gtk.Button("Autenticar")
		hbox_btn.pack_start(login_btn, gtk.TRUE, gtk.FALSE, 0)
		login_btn.connect("clicked", self.loginHash, username_entry, password_entry)
		login_btn.show()

		vbox.show()
		hbox_user.show()
		hbox_pass.show()
		hbox_btn.show()
		pw.show()