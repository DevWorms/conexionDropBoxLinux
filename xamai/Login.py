#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import urllib2

import thread

import xamai.Constants as const

'''
    Autentica al usurio con la API Scanda y guarda su usuario/password en el archivo de configuracion
'''

class Login():
    # Este metodo devuelve un arreglo con la info almacenad en: configuration.json
    def returnUserData(self):
        #log = SetLog()
        # Carga el archivo configuration.json
        file = os.path.join(const.LOCATION, const.CONFIGURATION_FILE)
        # Si el archivo existe...
        if (os.path.exists(file)):
            # abre el archivo y guarda los datos
            with open(file, 'r') as f:
                data = json.load(f)
        #else:
            #log.newLog("load_config_file", "E", "Login.returnUserData()")
        return data

    # guarda los datos del usuario recibidos
    def writeUserData(self, user, password, id):
        #from scanda.SetLog import SetLog
        #log = SetLog()
        # Carga el archivo configuration.json
        file = os.path.join(const.LOCATION, const.CONFIGURATION_FILE)
        uData = self.returnUserData()
        if not uData['user'] or not uData['password']:
    	    # crea un cron para iniciar la app cada reinicio
            from xamai.Crons import Cron
            c = Cron()
            thread.start_new_thread(c.rebootCron, ())
            #c.rebootCron()

        # Si el archivo existe...
        if (os.path.exists(file)):
            # abre el archivo y guarda la variable 'path' del archivo json
            with open(file, 'r') as f:
                data = json.load(f)
            # escribe la nueva variable time en el archivo json junto con la variable value
            with open(file, 'w') as f:
                json.dump({
                    'userPath': data['userPath'],
                    'path': data['path'],
                    'time': data['time'],
                    'time_type': data['time_type'],
                    'IdCustomer': id,
                    'user': user,
                    'password': password,
                    'tokenDropbox': data['tokenDropbox'],
                }, f)
        else:
            print "No existe el archivo"
            #log.newLog("load_config_file", "E", "")

    # Autenticacion con la api REST
    def loginApi(self, user, p_hash):
        #from scanda.SetLog import SetLog
        #log = SetLog()

        # Url de la api REST para autenticarse
        url = const.IP_SERVER + '/DBProtector/Login_GET?User=' + user + '&Password=' + p_hash

        try:
            # Realiza la peticion
            req = urllib2.Request(url)
            response = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            #log.newLog("http_error", "E", e.fp.read())
            print e
        # Devuelve la info
        res = json.loads(response.read())
        if res['Success'] == 1:
            if res['Status'] == 1:
                self.writeUserData(user, p_hash, res["IdCustomer"])
            else:
                print "No se pudo guardar la configuracion"
                #log.newLog("login_status_error" + res["Status"], "E", "")
            return True
        else:
            #log.newLogLogin(user, p_hash)
            return False

    # valida si un usuario esta loguado correctamente
    def isActive(self):
        user = self.returnUserData()
        if not user['user'] or not user['password'] or not user['IdCustomer']:
            return False
        else:
            if self.loginApi(user['user'], user['password']):
                return True
            else:
                return False

    def closeSession(self):
        file = os.path.join(const.LOCATION, const.CONFIGURATION_FILE)
        # Si el archivo existe...
        if (os.path.exists(file)):
            # abre el archivo y guarda la variable 'path' del archivo json
            with open(file, 'r') as f:
                data = json.load(f)
            # escribe la nueva variable time en el archivo json junto con la variable value
            with open(file, 'w') as f:
                json.dump({
                    'userPath': data['userPath'],
                    'path': data['path'],
                    'time': data['time'],
                    'time_type': data['time_type'],
                    'IdCustomer': 0,
                    'user': "",
                    'password': "",
                    'tokenDropbox': data['tokenDropbox'],
                }, f)
        else:
            print "No existe el archivo"