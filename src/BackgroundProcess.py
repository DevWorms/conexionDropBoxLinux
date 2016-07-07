#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import re
import urllib2
import psutil

from Login import Login


class BackgroundProcess():
    # Obtiene el nombre del proceso de la API de SCANDA
    def getProcessName(self):
        process = 'SQLDBproc'
        # extrae la informacion del usuario del archivo de configuracion
        login = Login()
        user = login.returnUserData()

        # Url de la api REST para autenticarse
        url = 'http://201.140.108.22:2017/DBProtector/DBBackUpProcess_GET?IdPlatform=2&User='+ user['user'] +'&Password=' + user['password']

        try:
            # Realiza la peticion
            req = urllib2.Request(url)
            response = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            print "Error: " + e.fp.read()
        # Devuelve la info
        res = json.loads(response.read())
        if res['Success'] == 1:
            process = res['Process']
        else:
            print "Ocurrio un error al autenticarse con la API REST"
        return process

    def isRunning(self):
        proceso = 0
        '''
            contador, si encuentra al menos un proceso corriendo con el nombre recibido por la api,
            entonces devuelve true, si no devuelve falso
        '''
        # si el nombre del proceso no es nulo...
        if self.getProcessName():
            # Lista los procesos del sistema
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
            print "Ocurrio un error al autenticarse con la API REST"


s = BackgroundProcess()
if s.isRunning():
    print "Esta corriendo el proceso"
else:
    print "Inicia la subida"