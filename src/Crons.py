#!/usr/bin/env python
import sys
import os
import json
from crontab import CronTab
from SetLog import SetLog

'''
	Crea un CRON para el usuario del sistema, el cron ejecutara el archivo
	/usr/bin/dbprotector_sync este archivo instancia una nueva clase Upload, que subira los respaldos
'''

class Cron():
	time = 0
	time_type = "dias"
	cron = ""

	# Lee los parametros de configuracion para crear un cron
	def readConf(self):
		# Set Log
		log = SetLog()
		cron_time = "* * * * * "
		# Proceso que realizara la subida de archivos
		cron_backend = "/async.py"
		# Carga el archivo configuration.json
		configuration_file = "settings/configuration.json"
		location = os.path.dirname(os.path.realpath(__file__))
		file = os.path.join(location, configuration_file)
		# Si el archivo existe...
		if ( os.path.exists(file) ):
			# abre el archivo y guarda la variable 'path' del archivo json
			with open(file, 'r') as f:
				data = json.load(f)
				self.time = data['time']
				self.time = str(self.time)
				self.time_type = data['time_type']
		else :
			log.newLog("load_config_file", "E", "")
		# Concatena el cron
		self.cron = "/usr/bin/python " + location + cron_backend

	# crea un cron
	def sincronizar(self):
		# Set Log
		log = SetLog()
		self.readConf()
		# Este comando se utiliza para extraer el usuario que ejecutara el cron
		linux_user = "echo $USER"
		# concatena la ruta de crons con el usuario que ejecutara el cron
		p = os.popen(linux_user, "r")
		linux_user_value = p.readline()

		tab = CronTab(user=linux_user_value)
		cron_job = tab.new(self.cron, comment="Ejecuta respaldo automatico de SCANDA")
		if self.time_type == "dias":
			cron_job.day.every(self.time)
		elif self.time_type == "horas":
			cron_job.hour.every(self.time)
		else:
			cron_job.hour.every(self.time)

		try:
			tab.write()
			#print tab.render()
			return True
		except:
			log.newLog("cron_error", "E", "")
			return False

#cr = Cron()
#cr.sincronizar()