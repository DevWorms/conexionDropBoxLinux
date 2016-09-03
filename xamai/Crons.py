#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
import json
import os
import urllib2

import thread
from crontab import CronTab

from xamai.Login import Login
from xamai.SetLog import SetLog
import xamai.Constants as const

'''
	Crea un CRON para el usuario del sistema, el cron ejecutara el archivo
	/usr/bin/dbprotector_sync este archivo instancia una nueva clase Upload, que subira los respaldos
	Estrae la info de frecuencia del respaldo
	cr = Cron()
	cr.sincronizar()
'''

class Cron():
	time = 0
	time_type = "dias"
	cron = ""

	# Lee los parametros de configuracion para crear un cron
	def readConf(self):
		# Set Log
		log = SetLog()
		# Carga el archivo configuration.json
		file = os.path.join(const.LOCATION, const.CONFIGURATION_FILE)
		# Si el archivo existe...
		if ( os.path.exists(file) ):
			# abre el archivo lee los parametros
			with open(file, 'r') as f:
				data = json.load(f)
				self.time = data['time']
				self.time = str(self.time)
				self.time_type = data['time_type']
		else :
			log.newLog(os.path.realpath(__file__), "load_config_file", "E", "")
		# Comando que ejecutara el cron, es el archivo que realizara los respaldos
		self.cron = "/usr/bin/dbprotector_sync"

	# crea un cron
	def sync(self):
		# Set Log
		log = SetLog()
		self.readConf()
		# Este comando se utiliza para extraer el usuario que ejecutara el cron
		linux_user = "echo $USER"
		# lee el resultado del comando anterior
		p = os.popen(linux_user, "r")
		linux_user_value = p.readline()

		# crea el cron
		tab = CronTab(user=True)
		# elimina cualquier cron previo con el comentario SCANDA_sync
		tab.remove_all(comment='SCANDA_sync')
		# crea una nueva tarea en el cron, agrega el comentario SCANDA_sync, para poder ser identificado despues
		cron_job = tab.new(self.cron, comment="SCANDA_sync")

		# datos de la frecuencia de respaldo
		dias = 0
		# pasa las horas a horas y dias
		if self.time > 23:
			while self.time > 23:
				dias += 1
				self.time -= 24

		# Agrega las frecuencias de respaldo
		if dias > 0:
			cron_job.day.every(dias)
		if self.time > 0:
			cron_job.hour.every(self.time)

		# escribe y guarda el cron
		try:
			tab.write()
			#print tab.render()
			return True
		except:
			log.newLog(os.path.realpath(__file__), "cron_error", "E", "")
			return False

	# Extrae los datos de frecuencia de respaldo desde la nube
	def getCloudSync(self):
		log = SetLog()
		# Datos del usuario
		l = Login()
		user = l.returnUserData()
		# Url de la api REST para autenticarse
		url = const.IP_SERVER + '/DBProtector/Account_GET?User=' + user['user'] + '&Password=' + user['password']
		try:
			# Realiza la peticion
			req = urllib2.Request(url)
			response = urllib2.urlopen(req)
		except urllib2.HTTPError, e:
			log.newLog(os.path.realpath(__file__), "http_error", "E", e.fp.read())
		# Devuelve la info
		res = json.loads(response.read())
		# Si el inicio de sesion es correcto
		if res['Success'] == 1:
			user['FileTreatmen'] = res['FileTreatmen']
			user['UploadFrecuency'] = res['UploadFrecuency']
			user['FileHistoricalNumber'] = res['FileHistoricalNumber']
		else:
			log.newLog(os.path.realpath(__file__), "login_api_error", "E", "")
		# devuelve todos los datos del usuario
		return user

	# Guarda los datos de extraidos por getCloudSync y vuelve a generar los crons
	def cloudSync(self):
		# Set Log
		log = SetLog()
		# Carga el archivo configuration.json
		file = os.path.join(const.LOCATION, const.CONFIGURATION_FILE)
		# Si el archivo existe...
		if (os.path.exists(file)):
			# lee los parametros de la api
			cloud = self.getCloudSync()
			# abre el archivo lee los parametros
			with open(file, 'r') as f:
				data = json.load(f)
			with open(file, 'w') as f:
				json.dump({
					'userPath': data['userPath'],
					'path': data['path'],
					'time': cloud['UploadFrecuency'],
					'time_type': data['time_type'],
					'IdCustomer': data['IdCustomer'],
					'user': data['user'],
					'password': data['password'],
					'tokenDropbox': data['tokenDropbox'],
				}, f)
			thread.start_new_thread(self.sync, ())
			#self.sync()
		else:
			log.newLog(os.path.realpath(__file__), "load_config_file", "E", "")

	def rebootCron(self):
		# Set Log
		log = SetLog()
		# Este comando se utiliza para extraer el usuario que ejecutara el cron
		linux_user = "echo $USER"
		# lee el resultado del comando anterior
		p = os.popen(linux_user, "r")
		linux_user_value = p.readline()

		# crea el cron
		tab = CronTab(user=True)
		# elimina cualquier cron previo con el comentario SCANDA_sync
		tab.remove_all(comment='SCANDA_init')
		# crea una nueva tarea en el cron, agrega el comentario SCANDA_sync, para poder ser identificado despues
		cron_job = tab.new("/usr/bin/dbprotector_xamai", comment="SCANDA_init")

		# configura el cron para que la aplicacion se inicie cada reinicio del sistema
		cron_job.every_reboot()

		# escribe y guarda el cron
		try:
			tab.write()
			# print tab.render()
			return True
		except:
			log.newLog(os.path.realpath(__file__), "cron_error", "E", "")
			return False

	# Elimina los crons de sincronizacion y autoinicio de la aplicacion
	def removeCrons(self):
		log = SetLog()
		# Este comando se utiliza para extraer el usuario que ejecutara el cron
		linux_user = "echo $USER"
		# lee el resultado del comando anterior
		p = os.popen(linux_user, "r")
		linux_user_value = p.readline()

		tab = CronTab(user=True)
		# elimina cualquier cron previo con el comentario SCANDA_sync
		tab.remove_all(comment='SCANDA_init')
		# elimina cualquier cron previo con el comentario SCANDA_sync
		tab.remove_all(comment='SCANDA_sync')

		# escribe y guarda el cron
		try:
			tab.write()
			# print tab.render()
			return True
		except:
			log.newLog(os.path.realpath(__file__), "cron_error", "E", "")
			return False