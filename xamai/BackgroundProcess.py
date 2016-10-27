#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
import json
import re
import urllib2
import psutil
import os.path

from xamai.Login import Login
from xamai.SetLog import SetLog
import xamai.Constants as const

'''
    Recibe de la API SCANDA el nombre del proceso usado para realizar los respaldos de BD
    lista todos los procesos del sistema, si encuentra alguno con el nombre recibido,
    revisa su status, si esta en 'running' o 'waiting' no inicia la subida.
    si no inicia la subida de archivos

    s = BackgroundProcess()
    if s.isRunning():
        return False
    else:
        return True
'''

class BackgroundProcess():
    THIS_FILE = os.path.realpath(__file__)
    file = THIS_FILE.split("/")
    THIS_FILE = file[-1] + "." + "BackgroundProcess()"

    # Obtiene el nombre del proceso de la API de SCANDA
    def getProcessName(self):
        # Set Log
        log = SetLog()
        # Exception
        ex = ""
        # Mombre por default
        process = 'SQLDBproc'
        '''
            Version del Sistema Operativo
            2 = Linux
            1 = Windows
        '''
        so = 2
        # extrae la informacion del usuario del archivo de configuracion
        login = Login()
        user = login.returnUserData()

        # Url de la api REST para autenticarse
        url = const.IP_SERVER + '/DBProtector/DBBackUpProcess_GET?IdPlatform=' + str(so) + '&User='+ user['user'] +'&Password=' + user['password']

        try:
            # Realiza la peticion
            req = urllib2.Request(url)
            response = urllib2.urlopen(req)
        except HTTPError as e:
            log.newLog(self.THIS_FILE + "." + "getProcessName()", "http_error", "E", 'Codigo: ', e.code)
        except URLError as e:
            log.newLog(self.THIS_FILE + "." + "getProcessName()", "http_error", "E", 'Reason: ', e.reason)

        # Devuelve la info
        res = json.loads(response.read())
        if res['Success'] == 1:
            process = res['Process']
        else:
            log.newLog(self.THIS_FILE + "." + "getProcessName()", "process_api", "E", "")
        return process

    def isRunning(self):
        log = SetLog()
        proceso = 0
        '''
            contador, si encuentra al menos un proceso corriendo con el nombre recibido por la api,
            entonces devuelve true, si no devuelve falso
        '''
        # si el nombre del proceso no es nulo...
        if self.getProcessName():
            # Lista los procesos del sistema
            if psutil.pids():
                for proc in psutil.pids():
                    process = psutil.Process(proc)
                    # busca el proceso de respaldo, dentro de los procesos del sistema
                    if re.search(r"%s" % self.getProcessName(), process.name()):
                        # si el proceso esta en "running" o "waiting" porpone la subida del archivo
                        if process.status() == "running" or process.status() == "waiting":
                            proceso+1
            if proceso > 0:
                return True
            else:
                return False
        else:
            log.newLog(self.THIS_FILE + "." + "isRunning()", "process_incorrect", "E", "BackgroundProcess.getProcessName()")

    # DB protector solo puede correrse una vez
    def dbProtesctorIsRunning(self):
        proceso = 0
        '''
            contador, si encuentra al menos un proceso corriendo con el nombre recibido por la api,
            entonces devuelve true, si no devuelve falso
        '''
         # Lista los procesos del sistema
        for proc in psutil.process_iter():
            try:
                pinfo = proc.as_dict(attrs=['pid', 'name'])
            except psutil.NoSuchProcess:
                pass
            else:
                if re.search(r"%s" % self.getProcessName(), pinfo['name']):
                    proceso = proceso + 1

        if proceso > 0:
            return True
        else:
            return False