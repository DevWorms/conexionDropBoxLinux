#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
import json
import os
import threading
import urllib2

#import thread
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
    THIS_FILE = os.path.realpath(__file__)
    file = THIS_FILE.split("/")
    THIS_FILE = file[-1] + "." + "Cron()"

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
            log.newLog(self.THIS_FILE + "." + "readConf()", "load_config_file", "E", "")
        # Comando que ejecutara el cron, es el archivo que realizara los respaldos
        self.cron = "/usr/local/bin/dbprotector_sync"

    # crea el cron para respaldar cada x tiempo
    def sync(self):
        # Set Log
        log = SetLog()
        self.readConf()

        # crea el cron
        tab = CronTab(user=True)
        # elimina cualquier cron previo con el comentario xamai_sync
        tab.remove_all(comment='xamai_sync')
        # crea una nueva tarea en el cron, agrega el comentario xamai_sync, para poder ser identificado despues
        cron_job = tab.new(self.cron, comment="xamai_sync")

        # datos de la frecuencia de respaldo
        dias = 0
        self.time = int(self.time)
        # pasa las horas a horas y dias
        if self.time > 23:
            while self.time > 23:
                dias = dias + 1
                self.time = self.time - 24

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
            log.newLog(self.THIS_FILE + "." + "sync()", "cron_error", "E", "")
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
        except HTTPError as e:
            log.newLog(self.THIS_FILE + "." + "getCloudSync()", "http_error", "E", 'Codigo: ', e.code)
        except URLError as e:
            log.newLog(self.THIS_FILE + "." + "getCloudSync()", "http_error", "E", 'Reason: ', e.reason)
        # Devuelve la info
        res = json.loads(response.read())
        # Si el inicio de sesion es correcto
        if res['Success'] == 1:
            user['FileTreatmen'] = res['FileTreatmen']
            user['UploadFrecuency'] = res['UploadFrecuency']
            user['FileHistoricalNumber'] = res['FileHistoricalNumber']
        else:
            log.newLog(self.THIS_FILE + "." + "getCloudSync()", "login_api_error", "E", "")
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
            threading.Thread(target=self.sync).start()
            #self.sync()
        else:
            log.newLog(self.THIS_FILE + "." + "cloudSync()", "load_config_file", "E", "")

    # Crea el cron: cada vez que el servidor se reinicia se ejecuta dbprotector
    def rebootCron(self):
        # Set Log
        log = SetLog()

        # crea el cron
        tab = CronTab(user=True)
        # elimina cualquier cron previo con el comentario xamai_sync
        tab.remove_all(comment='xamai_init')
        # crea una nueva tarea en el cron, agrega el comentario xamai_sync, para poder ser identificado despues
        cron_job = tab.new("dbprotector_xamai", comment="xamai_init")

        # configura el cron para que la aplicacion se inicie cada reinicio del sistema
        cron_job.every_reboot()

        # escribe y guarda el cron
        try:
            tab.write()
            return True
        except:
            log.newLog(self.THIS_FILE + "." + "rebootCron()", "cron_error", "E", "")
            return False

    # Elimina los crons de sincronizacion y autoinicio de la aplicacion
    def removeCrons(self):
        log = SetLog()

        tab = CronTab(user=True)
        # elimina cualquier cron previo con el comentario xamai_sync
        tab.remove_all(comment='xamai_init')
        # elimina cualquier cron previo con el comentario xamai_sync
        tab.remove_all(comment='xamai_sync')

        # escribe y guarda el cron
        try:
            tab.write()
            return True
        except:
            log.newLog(self.THIS_FILE + "." + "removeCrons()", "cron_error", "E", "")
            return False